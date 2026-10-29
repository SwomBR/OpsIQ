"""
OpsIQ - Business Operations Intelligence Platform

Module: database.py

Purpose:
    Load the Olist CSV files into an SQLite database and run the example
    SQL queries in sql/queries/.

The database is optional. The CSV files stay the source of truth, and
the business report and the API keep reading the CSV files directly.

Commands (run from the project root):
    python -m src.database build            Create data/processed/opsiq.db
    python -m src.database list             List the example queries
    python -m src.database query NAME       Run one example query
    python -m src.database late --min-days 30 --limit 5
                                            Late orders (parameterised query)
    python -m src.database verify           Compare SQL results with the
                                            Python analytics
"""

import argparse
import csv
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from src.data_loader import PROJECT_ROOT, RAW_DATA_DIR

SQL_DIR = PROJECT_ROOT / "sql"
SCHEMA_FILE = SQL_DIR / "schema.sql"
QUERIES_DIR = SQL_DIR / "queries"
DEFAULT_DATABASE = PROJECT_ROOT / "data" / "processed" / "opsiq.db"

# Tables and their source files, in an order where every table comes
# after the tables it refers to (so foreign keys can be checked).
TABLE_SOURCES = [
    ("customers", "olist_customers_dataset.csv"),
    ("sellers", "olist_sellers_dataset.csv"),
    ("category_translations", "product_category_name_translation.csv"),
    ("products", "olist_products_dataset.csv"),
    ("orders", "olist_orders_dataset.csv"),
    ("order_items", "olist_order_items_dataset.csv"),
    ("order_payments", "olist_order_payments_dataset.csv"),
]


@dataclass
class ImportResult:
    rows_read: int
    rows_inserted: int

    @property
    def duplicates_skipped(self):
        return self.rows_read - self.rows_inserted


def connect(database_path=DEFAULT_DATABASE):
    """Open an existing database with foreign key checks turned on."""

    database_path = Path(database_path)

    if not database_path.exists():
        raise FileNotFoundError(
            f"Database not found: {database_path}. "
            "Create it with: python -m src.database build"
        )

    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _convert(value, column_type):
    """Turn one CSV text value into the column's SQL type.

    Empty values become NULL. A value that cannot be converted raises
    ValueError, so bad data is reported instead of silently stored.
    """

    if value is None or value.strip() == "":
        return None

    if column_type == "INTEGER":
        return int(value)

    if column_type == "REAL":
        return float(value)

    return value


def import_table(connection, table, csv_path):
    """Insert every row of csv_path into table.

    Rows whose primary key is already in the table are skipped and
    counted as duplicates. Any other problem raises an error.
    """

    # Read the column names and types from the schema, so they are
    # defined in one place only (sql/schema.sql).
    columns = [
        (row[1], row[2])
        for row in connection.execute(f"PRAGMA table_info({table})")
    ]
    column_names = [name for name, _ in columns]

    with open(csv_path, mode="r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        missing_columns = set(column_names) - set(reader.fieldnames or [])
        if missing_columns:
            raise ValueError(
                f"{Path(csv_path).name} is missing columns: "
                f"{', '.join(sorted(missing_columns))}"
            )

        # The table and column names come from our own schema, never
        # from user input. The values are passed separately as ?
        # parameters, which keeps them from being run as SQL.
        statement = (
            f"INSERT INTO {table} ({', '.join(column_names)}) "
            f"VALUES ({', '.join('?' for _ in column_names)}) "
            "ON CONFLICT DO NOTHING"
        )

        rows_read = 0
        changes_before = connection.total_changes

        for line_number, record in enumerate(reader, start=2):
            rows_read += 1

            try:
                values = [
                    _convert(record[name], column_type)
                    for name, column_type in columns
                ]
                connection.execute(statement, values)
            except (ValueError, sqlite3.IntegrityError) as error:
                raise ValueError(
                    f"{Path(csv_path).name}, line {line_number}: {error}"
                ) from error

    return ImportResult(
        rows_read=rows_read,
        rows_inserted=connection.total_changes - changes_before,
    )


def build_database(database_path=DEFAULT_DATABASE, data_dir=RAW_DATA_DIR):
    """Create a fresh database from the CSV files.

    The database is built in a temporary file and only replaces the old
    one when every table imported successfully. Running it again always
    gives the same result, and a failed build leaves the old database
    untouched.

    Returns:
        dict[str, ImportResult]: The import counts for each table.
    """

    database_path = Path(database_path)
    data_dir = Path(data_dir)
    database_path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = database_path.with_name(database_path.name + ".building")
    temp_path.unlink(missing_ok=True)

    connection = sqlite3.connect(temp_path)

    try:
        connection.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
        connection.execute("PRAGMA foreign_keys = ON")

        results = {}

        # One transaction: either every table is imported, or none is.
        with connection:
            for table, file_name in TABLE_SOURCES:
                results[table] = import_table(
                    connection, table, data_dir / file_name
                )

        connection.close()
    except BaseException:
        connection.close()
        temp_path.unlink(missing_ok=True)
        raise

    os.replace(temp_path, database_path)
    return results


def list_queries():
    """Return the names of the example queries in sql/queries/."""

    return sorted(path.stem for path in QUERIES_DIR.glob("*.sql"))


def run_query(connection, name):
    """Run an example query by name.

    Only names of files in sql/queries/ are accepted, so this cannot be
    used to run arbitrary SQL or read other files.

    Returns:
        tuple[list[str], list[tuple]]: The column names and the rows.
    """

    if name not in list_queries():
        raise ValueError(
            f"Unknown query: {name!r}. "
            f"Choose one of: {', '.join(list_queries())}"
        )

    sql = (QUERIES_DIR / f"{name}.sql").read_text(encoding="utf-8")
    cursor = connection.execute(sql)
    return [column[0] for column in cursor.description], cursor.fetchall()


def find_late_orders(connection, min_days_late=0, limit=10):
    """Return delivered orders more than min_days_late days late.

    This query takes values from the user, so they are passed as ?
    parameters, never pasted into the SQL text. Input such as
    "0; DROP TABLE orders" is rejected by float() instead of being run.
    """

    min_days_late = float(min_days_late)
    limit = int(limit)

    if min_days_late < 0 or limit < 1:
        raise ValueError("min_days_late must be >= 0 and limit >= 1.")

    cursor = connection.execute(
        """
        SELECT
            order_id,
            order_estimated_delivery_date AS estimated_delivery,
            order_delivered_customer_date AS actual_delivery,
            ROUND(julianday(order_delivered_customer_date)
                  - julianday(order_estimated_delivery_date), 2) AS days_late
        FROM orders
        WHERE order_status = 'delivered'
          AND julianday(order_delivered_customer_date)
              - julianday(order_estimated_delivery_date) > ?
        ORDER BY days_late DESC, order_id
        LIMIT ?
        """,
        (min_days_late, limit),
    )
    return [column[0] for column in cursor.description], cursor.fetchall()


def compare_with_python(connection, data_dir=RAW_DATA_DIR):
    """Calculate key metrics with SQL and with the Python analytics.

    Returns:
        list[tuple[str, object, object]]: (metric, python value, SQL value).
    """

    # Imported here so `python -m src.database build` stays light.
    from src.customer_analyzer import analyze_customers
    from src.data_analyzer import count_orders_by_status
    from src.data_loader import open_order
    from src.delivery_analyzer import calculate_delivery_performance
    from src.product_analyzer import analyze_products
    from src.sales_analyzer import analyze_sales, load_csv

    data_dir = Path(data_dir)
    orders = open_order(data_dir / "olist_orders_dataset.csv")
    order_items = load_csv(data_dir / "olist_order_items_dataset.csv")
    payments = load_csv(data_dir / "olist_order_payments_dataset.csv")
    products = load_csv(data_dir / "olist_products_dataset.csv")
    customers = load_csv(data_dir / "olist_customers_dataset.csv")
    translations = {
        row["product_category_name"]: row["product_category_name_english"]
        for row in load_csv(data_dir / "product_category_name_translation.csv")
    }

    def one_row(name):
        columns, rows = run_query(connection, name)
        return dict(zip(columns, rows[0]))

    def rounded(value):
        return None if value is None else round(value, 2)

    comparisons = []

    # Orders by status.
    _, status_rows = run_query(connection, "orders_by_status")
    for status, count in sorted(count_orders_by_status(orders).items()):
        sql_count = dict(status_rows).get(status)
        comparisons.append((f"orders: {status}", count, sql_count))

    # Delivery performance.
    python_delivery = calculate_delivery_performance(orders)
    sql_delivery = one_row("delivery_performance")
    for key in [
        "delivered_orders_analyzed",
        "on_time_orders",
        "late_orders",
        "on_time_percentage",
        "late_percentage",
        "average_delay_days",
        "maximum_delay_days",
        "delayed_more_than_3_days",
        "delayed_more_than_7_days",
    ]:
        python_value = python_delivery[key]
        if isinstance(python_value, float):
            python_value = rounded(python_value)
        comparisons.append((f"delivery: {key}", python_value, sql_delivery[key]))

    # Sales.
    sales = analyze_sales(order_items, payments)
    sql_sales = connection.execute(
        "SELECT ROUND(SUM(price), 2), ROUND(SUM(freight_value), 2), "
        "COUNT(DISTINCT order_id) FROM order_items"
    ).fetchone()
    comparisons += [
        ("sales: total_product_revenue",
         sales["total_product_revenue"], sql_sales[0]),
        ("sales: total_freight_charges",
         sales["total_freight_charges"], sql_sales[1]),
        ("sales: orders_with_items", sales["total_orders"], sql_sales[2]),
    ]

    # Revenue by category (top 10).
    product_report = analyze_products(order_items, products, translations)
    _, category_rows = run_query(connection, "revenue_by_category")
    for python_row, sql_row in zip(
        product_report["top_categories"], category_rows
    ):
        comparisons.append((
            f"category revenue: {python_row['category']}",
            (python_row["category"], python_row["revenue"],
             python_row["quantity_sold"]),
            tuple(sql_row),
        ))

    # Customers.
    customer_report = analyze_customers(orders, customers, order_items)
    sql_customers = one_row("repeat_customers")
    comparisons += [
        ("customers: unique_customers",
         customer_report["total_unique_customers"],
         sql_customers["unique_customers"]),
        ("customers: repeat_customers",
         customer_report["repeat_customers"],
         sql_customers["repeat_customers"]),
        ("customers: repeat_customer_percentage",
         rounded(customer_report["repeat_customer_percentage"]),
         sql_customers["repeat_customer_percentage"]),
    ]

    return comparisons


def _print_table(columns, rows):
    """Print query results as an aligned text table."""

    text_rows = [
        ["NULL" if value is None else str(value) for value in row]
        for row in rows
    ]
    widths = [
        max([len(column)] + [len(row[index]) for row in text_rows])
        for index, column in enumerate(columns)
    ]

    print("  ".join(column.ljust(width) for column, width in zip(columns, widths)))
    print("  ".join("-" * width for width in widths))

    for row in text_rows:
        print("  ".join(value.ljust(width) for value, width in zip(row, widths)))

    print(f"({len(rows)} row{'s' if len(rows) != 1 else ''})")


def main(arguments=None):
    parser = argparse.ArgumentParser(
        prog="python -m src.database",
        description="Build and query the optional OpsIQ SQLite database.",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DATABASE,
        help="Database file (default: data/processed/opsiq.db).",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    build = commands.add_parser("build", help="Create the database from the CSV files.")
    build.add_argument("--data-dir", type=Path, default=RAW_DATA_DIR)

    commands.add_parser("list", help="List the example queries.")

    query = commands.add_parser("query", help="Run one example query.")
    query.add_argument("name", help="Query name, for example orders_by_status.")

    late = commands.add_parser("late", help="Show late-delivered orders.")
    late.add_argument("--min-days", type=float, default=0)
    late.add_argument("--limit", type=int, default=10)

    verify = commands.add_parser(
        "verify", help="Compare SQL results with the Python analytics."
    )
    verify.add_argument("--data-dir", type=Path, default=RAW_DATA_DIR)

    args = parser.parse_args(arguments)

    try:
        if args.command == "build":
            results = build_database(args.db, args.data_dir)
            print(f"Database created: {args.db}")
            for table, result in results.items():
                print(
                    f"  {table}: {result.rows_inserted:,} rows "
                    f"({result.duplicates_skipped:,} duplicates skipped)"
                )
            return 0

        if args.command == "list":
            for name in list_queries():
                print(name)
            return 0

        connection = connect(args.db)

        try:
            if args.command == "query":
                _print_table(*run_query(connection, args.name))
            elif args.command == "late":
                _print_table(
                    *find_late_orders(connection, args.min_days, args.limit)
                )
            elif args.command == "verify":
                comparisons = compare_with_python(connection, args.data_dir)
                mismatches = 0
                for metric, python_value, sql_value in comparisons:
                    matches = python_value == sql_value
                    mismatches += not matches
                    print(
                        f"{'OK  ' if matches else 'DIFF'} {metric}: "
                        f"Python={python_value} SQL={sql_value}"
                    )
                print(
                    f"\n{len(comparisons) - mismatches} of {len(comparisons)} "
                    "metrics match."
                )
                return 1 if mismatches else 0
        finally:
            connection.close()

    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
