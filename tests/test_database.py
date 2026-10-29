"""
OpsIQ - Business Operations Intelligence Platform

Module: test_database.py

Purpose:
    Test the optional SQLite database: building it from CSV files,
    handling duplicates, missing values, and broken relationships,
    and checking that the SQL queries agree with the Python analytics.

The tests write small CSV files into a temporary folder, so they do not
need the Olist dataset.
"""

import sqlite3
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from src import database

CSV_FILES = {
    "olist_customers_dataset.csv": (
        "customer_id,customer_unique_id,customer_zip_code_prefix,"
        "customer_city,customer_state\n"
        "C1,U1,01000,sao paulo,SP\n"
        "C2,U1,01000,sao paulo,SP\n"
        "C3,U2,20000,rio de janeiro,RJ\n"
    ),
    "olist_sellers_dataset.csv": (
        "seller_id,seller_zip_code_prefix,seller_city,seller_state\n"
        "S1,13000,campinas,SP\n"
    ),
    "product_category_name_translation.csv": (
        "product_category_name,product_category_name_english\n"
        "beleza_saude,health_beauty\n"
    ),
    # P2 has no category and no measurements.
    "olist_products_dataset.csv": (
        "product_id,product_category_name,product_name_lenght,"
        "product_description_lenght,product_photos_qty,product_weight_g,"
        "product_length_cm,product_height_cm,product_width_cm\n"
        "P1,beleza_saude,40,287,1,225,16,10,14\n"
        "P2,,,,,,,,\n"
    ),
    # O1 on time, O2 late by 3.5 days, O3 late by 10 days,
    # O4 delivered without a delivery date, O5 shipped.
    "olist_orders_dataset.csv": (
        "order_id,customer_id,order_status,order_purchase_timestamp,"
        "order_approved_at,order_delivered_carrier_date,"
        "order_delivered_customer_date,order_estimated_delivery_date\n"
        "O1,C1,delivered,2026-01-01 08:00:00,,,"
        "2026-01-05 10:00:00,2026-01-10 00:00:00\n"
        "O2,C2,delivered,2026-01-02 09:00:00,,,"
        "2026-01-15 12:00:00,2026-01-12 00:00:00\n"
        "O3,C3,delivered,2026-01-03 09:00:00,,,"
        "2026-01-20 00:00:00,2026-01-10 00:00:00\n"
        "O4,C3,delivered,2026-01-04 09:00:00,,,,2026-01-10 00:00:00\n"
        "O5,C3,shipped,2026-01-05 09:00:00,,,,2026-01-20 00:00:00\n"
    ),
    "olist_order_items_dataset.csv": (
        "order_id,order_item_id,product_id,seller_id,shipping_limit_date,"
        "price,freight_value\n"
        "O1,1,P1,S1,2026-01-02 00:00:00,100.00,10.00\n"
        "O1,2,P2,S1,2026-01-02 00:00:00,50.00,5.00\n"
        "O2,1,P1,S1,2026-01-03 00:00:00,100.00,10.00\n"
    ),
    "olist_order_payments_dataset.csv": (
        "order_id,payment_sequential,payment_type,payment_installments,"
        "payment_value\n"
        "O1,1,credit_card,1,165.00\n"
        "O2,1,boleto,1,110.00\n"
    ),
}


class DatabaseTestCase(unittest.TestCase):
    """Base class: a temporary folder with the sample CSV files."""

    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.folder = Path(temp_dir.name)
        self.data_dir = self.folder / "raw"
        self.data_dir.mkdir()
        self.db_path = self.folder / "processed" / "test.db"
        self.write_csv_files()

    def write_csv_files(self, changes=None):
        files = {**CSV_FILES, **(changes or {})}
        for name, content in files.items():
            (self.data_dir / name).write_text(content, encoding="utf-8")

    def build(self):
        return database.build_database(self.db_path, self.data_dir)

    def open(self):
        connection = database.connect(self.db_path)
        self.addCleanup(connection.close)
        return connection


class TestBuildDatabase(DatabaseTestCase):

    def test_imports_every_row(self):
        results = self.build()

        self.assertEqual(
            {table: result.rows_inserted for table, result in results.items()},
            {
                "customers": 3,
                "sellers": 1,
                "category_translations": 1,
                "products": 2,
                "orders": 5,
                "order_items": 3,
                "order_payments": 2,
            },
        )

    def test_empty_values_become_null(self):
        self.build()
        connection = self.open()

        product = connection.execute(
            "SELECT product_category_name, product_weight_g "
            "FROM products WHERE product_id = 'P2'"
        ).fetchone()
        delivery_date = connection.execute(
            "SELECT order_delivered_customer_date FROM orders "
            "WHERE order_id = 'O4'"
        ).fetchone()

        self.assertEqual(product, (None, None))
        self.assertEqual(delivery_date, (None,))

    def test_numbers_are_stored_as_numbers(self):
        self.build()

        price_type, item_type = self.open().execute(
            "SELECT typeof(price), typeof(order_item_id) FROM order_items "
            "LIMIT 1"
        ).fetchone()

        self.assertEqual((price_type, item_type), ("real", "integer"))

    def test_duplicate_rows_are_skipped_and_counted(self):
        orders = CSV_FILES["olist_orders_dataset.csv"]
        duplicate_row = orders.splitlines()[1] + "\n"
        self.write_csv_files({"olist_orders_dataset.csv": orders + duplicate_row})

        results = self.build()

        self.assertEqual(results["orders"].rows_read, 6)
        self.assertEqual(results["orders"].rows_inserted, 5)
        self.assertEqual(results["orders"].duplicates_skipped, 1)

    def test_building_twice_gives_the_same_result(self):
        self.build()
        self.build()

        count = self.open().execute("SELECT COUNT(*) FROM orders").fetchone()

        self.assertEqual(count, (5,))

    def test_foreign_keys_are_enforced(self):
        self.build()

        with self.assertRaises(sqlite3.IntegrityError):
            self.open().execute(
                "INSERT INTO orders (order_id, customer_id, order_status) "
                "VALUES ('O9', 'NO-SUCH-CUSTOMER', 'created')"
            )

    def test_unknown_reference_stops_the_build(self):
        items = CSV_FILES["olist_order_items_dataset.csv"]
        self.write_csv_files({
            "olist_order_items_dataset.csv":
                items + "O1,3,NO-SUCH-PRODUCT,S1,,1.00,1.00\n",
        })

        with self.assertRaisesRegex(ValueError, "line 5.*FOREIGN KEY"):
            self.build()

    def test_bad_number_stops_the_build_with_its_line(self):
        items = CSV_FILES["olist_order_items_dataset.csv"]
        self.write_csv_files({
            "olist_order_items_dataset.csv": items.replace("50.00", "fifty"),
        })

        with self.assertRaisesRegex(
            ValueError, "olist_order_items_dataset.csv, line 3"
        ):
            self.build()

    def test_failed_build_keeps_the_previous_database(self):
        self.build()
        self.write_csv_files({
            "olist_orders_dataset.csv": "order_id\nBROKEN\n",
        })

        with self.assertRaisesRegex(ValueError, "missing columns"):
            self.build()

        count = self.open().execute("SELECT COUNT(*) FROM orders").fetchone()
        self.assertEqual(count, (5,))
        self.assertFalse(
            self.db_path.with_name(self.db_path.name + ".building").exists()
        )

    def test_missing_csv_file_raises_file_not_found(self):
        (self.data_dir / "olist_sellers_dataset.csv").unlink()

        with self.assertRaises(FileNotFoundError):
            self.build()

    def test_connect_explains_how_to_create_a_missing_database(self):
        with self.assertRaisesRegex(FileNotFoundError, "src.database build"):
            database.connect(self.folder / "missing.db")


class TestQueries(DatabaseTestCase):

    def setUp(self):
        super().setUp()
        self.build()
        self.connection = self.open()

    def query(self, name):
        columns, rows = database.run_query(self.connection, name)
        return [dict(zip(columns, row)) for row in rows]

    def test_every_example_query_runs(self):
        for name in database.list_queries():
            with self.subTest(query=name):
                database.run_query(self.connection, name)

    def test_orders_by_status(self):
        self.assertEqual(
            self.query("orders_by_status"),
            [
                {"order_status": "delivered", "orders": 4},
                {"order_status": "shipped", "orders": 1},
            ],
        )

    def test_delivery_performance(self):
        self.assertEqual(
            self.query("delivery_performance"),
            [{
                "delivered_orders_analyzed": 3,
                "on_time_orders": 1,
                "late_orders": 2,
                "on_time_percentage": 33.33,
                "late_percentage": 66.67,
                "average_delay_days": 6.75,
                "maximum_delay_days": 10.0,
                "delayed_more_than_3_days": 2,
                "delayed_more_than_7_days": 1,
            }],
        )

    def test_late_deliveries_longest_first(self):
        self.assertEqual(
            [row["order_id"] for row in self.query("late_deliveries")],
            ["O3", "O2"],
        )

    def test_revenue_by_category_uses_translation_and_unknown(self):
        self.assertEqual(
            self.query("revenue_by_category"),
            [
                {"category": "health_beauty", "revenue": 200.0, "items_sold": 2},
                {"category": "unknown", "revenue": 50.0, "items_sold": 1},
            ],
        )

    def test_repeat_customers(self):
        self.assertEqual(
            self.query("repeat_customers"),
            [{
                "unique_customers": 2,
                "repeat_customers": 2,
                "repeat_customer_percentage": 100.0,
            }],
        )

    def test_unknown_query_name_is_rejected(self):
        for name in ["does_not_exist", "../schema", "orders; DROP TABLE orders"]:
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    database.run_query(self.connection, name)

    def test_find_late_orders_uses_parameters(self):
        _, rows = database.find_late_orders(self.connection, min_days_late=5)

        self.assertEqual([row[0] for row in rows], ["O3"])

    def test_find_late_orders_rejects_sql_in_its_input(self):
        with self.assertRaises(ValueError):
            database.find_late_orders(self.connection, "0; DROP TABLE orders")

        # The table is still there.
        count = self.connection.execute("SELECT COUNT(*) FROM orders")
        self.assertEqual(count.fetchone(), (5,))

    def test_find_late_orders_validates_range(self):
        for min_days, limit in [(-1, 10), (0, 0)]:
            with self.subTest(min_days=min_days, limit=limit):
                with self.assertRaises(ValueError):
                    database.find_late_orders(self.connection, min_days, limit)

    def test_sql_agrees_with_python_analytics(self):
        comparisons = database.compare_with_python(
            self.connection, self.data_dir
        )

        self.assertGreater(len(comparisons), 10)
        for metric, python_value, sql_value in comparisons:
            with self.subTest(metric=metric):
                self.assertEqual(python_value, sql_value)


class TestCommandLine(DatabaseTestCase):

    def run_command(self, *arguments):
        output = StringIO()
        with redirect_stdout(output):
            exit_code = database.main(["--db", str(self.db_path), *arguments])
        return exit_code, output.getvalue()

    def test_build_query_and_verify(self):
        exit_code, output = self.run_command(
            "build", "--data-dir", str(self.data_dir)
        )
        self.assertEqual(exit_code, 0)
        self.assertIn("orders: 5 rows (0 duplicates skipped)", output)

        exit_code, output = self.run_command("query", "orders_by_status")
        self.assertEqual(exit_code, 0)
        self.assertIn("delivered", output)
        self.assertIn("(2 rows)", output)

        exit_code, output = self.run_command(
            "verify", "--data-dir", str(self.data_dir)
        )
        self.assertEqual(exit_code, 0)
        self.assertNotIn("DIFF", output)

    def test_query_without_database_explains_what_to_do(self):
        exit_code, output = self.run_command("query", "orders_by_status")

        self.assertEqual(exit_code, 1)
        self.assertIn("python -m src.database build", output)


if __name__ == "__main__":
    unittest.main()
