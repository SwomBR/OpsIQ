
"""
OpsIQ - Business Operations Intelligence Platform

Module: data_validator.py

Purpose:
    Validate order data quality and identify records requiring investigation.

Checks:
    1. Missing values.
    2. Missing order IDs.
    3. Duplicate order IDs.
    4. Invalid order statuses.
    5. Invalid date formats.
    6. Inconsistent processing timestamps.
    7. Delivered orders missing actual delivery dates.
"""

from datetime import datetime


VALID_ORDER_STATUSES = {
    "created",
    "approved",
    "invoiced",
    "processing",
    "shipped",
    "delivered",
    "canceled",
    "unavailable",
}

DATE_COLUMNS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

PROCESSING_DATE_COLUMNS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
]


def is_missing(value):
    """Return True if a value is None, empty, or whitespace only."""

    return value is None or (
        isinstance(value, str) and value.strip() == ""
    )


def check_missing_values(orders):
    """Count missing values in every column."""

    if not orders:
        return {}

    missing_counts = {}

    for column in orders[0].keys():
        missing_counts[column] = sum(
            1 for order in orders
            if is_missing(order.get(column))
        )

    return missing_counts


def check_missing_order_ids(orders):
    """Count records without an order ID."""

    return sum(
        1 for order in orders
        if is_missing(order.get("order_id"))
    )


def check_duplicate_order_ids(orders):
    """Count repeated occurrences of non-empty order IDs."""

    seen_order_ids = set()
    duplicate_count = 0

    for order in orders:
        order_id = order.get("order_id")

        if is_missing(order_id):
            continue

        if order_id in seen_order_ids:
            duplicate_count += 1
        else:
            seen_order_ids.add(order_id)

    return duplicate_count


def check_invalid_order_statuses(orders):
    """Return records with unexpected non-empty order statuses."""

    invalid_orders = []

    for order in orders:
        status = order.get("order_status")

        if is_missing(status):
            continue

        if str(status).strip().lower() not in VALID_ORDER_STATUSES:
            invalid_orders.append({
                "order_id": order.get("order_id"),
                "order_status": status,
            })

    return invalid_orders


def parse_order_date(value):
    """Parse a timestamp; return None for missing or invalid values."""

    if is_missing(value) or not isinstance(value, str):
        return None

    try:
        return datetime.strptime(
            value.strip(),
            "%Y-%m-%d %H:%M:%S"
        )
    except ValueError:
        return None


def check_invalid_date_formats(orders):
    """Find non-empty date values that cannot be parsed."""

    invalid_dates = []

    for order in orders:
        for column in DATE_COLUMNS:
            value = order.get(column)

            if is_missing(value):
                continue

            if parse_order_date(value) is None:
                invalid_dates.append({
                    "order_id": order.get("order_id"),
                    "column": column,
                    "value": value,
                })

    return invalid_dates


def check_inconsistent_dates(orders):
    """
    Find all adjacent available processing timestamps that are out of order.

    Missing intermediate timestamps are skipped.
    Invalid date formats are handled by check_invalid_date_formats().
    """

    inconsistent_dates = []

    for order in orders:
        parsed_dates = []
        has_invalid_date = False

        for column in PROCESSING_DATE_COLUMNS:
            value = order.get(column)

            if is_missing(value):
                continue

            parsed_date = parse_order_date(value)

            if parsed_date is None:
                has_invalid_date = True
                break

            parsed_dates.append((column, parsed_date))

        if has_invalid_date:
            continue

        for index in range(1, len(parsed_dates)):
            previous_column, previous_date = parsed_dates[index - 1]
            current_column, current_date = parsed_dates[index]

            if current_date < previous_date:
                inconsistent_dates.append({
                    "order_id": order.get("order_id"),
                    "previous_column": previous_column,
                    "current_column": current_column,
                    "previous_date": previous_date,
                    "current_date": current_date,
                })

    return inconsistent_dates


def check_delivered_orders_missing_delivery_dates(orders):
    """Return IDs of delivered orders missing their actual delivery date."""

    missing_delivery_dates = []

    for order in orders:
        status = order.get("order_status", "")

        if (
            isinstance(status, str)
            and status.strip().lower() == "delivered"
            and is_missing(order.get("order_delivered_customer_date"))
        ):
            missing_delivery_dates.append(order.get("order_id"))

    return missing_delivery_dates


def validate_orders(orders, issue_limit=10):
    """Run validation checks and print a summary with issue examples."""

    if not orders:
        print("No order data available to validate.")
        return

    missing_counts = check_missing_values(orders)
    missing_ids = check_missing_order_ids(orders)
    duplicate_ids = check_duplicate_order_ids(orders)
    invalid_statuses = check_invalid_order_statuses(orders)
    invalid_dates = check_invalid_date_formats(orders)
    inconsistent_dates = check_inconsistent_dates(orders)
    missing_delivery_dates = (
        check_delivered_orders_missing_delivery_dates(orders)
    )

    issue_groups = [
        ("Invalid order statuses", invalid_statuses),
        ("Invalid date formats", invalid_dates),
        ("Inconsistent processing timestamps", inconsistent_dates),
        (
            "Delivered orders missing customer delivery dates",
            missing_delivery_dates,
        ),
    ]

    print("\n" + "=" * 55)
    print("           OPSIQ DATA QUALITY REPORT")
    print("=" * 55)
    print(f"Total orders checked: {len(orders):,}")

    print("\n--- Missing Values by Column ---")
    for column, count in missing_counts.items():
        print(f"{column}: {count:,}")

    print("\n--- Issue Summary ---")
    print(f"Missing order IDs: {missing_ids:,}")
    print(f"Duplicate order ID occurrences: {duplicate_ids:,}")

    for label, items in issue_groups:
        print(f"{label}: {len(items):,}")

    print("\n--- Issue Examples ---")
    for label, items in issue_groups:
        if not items:
            continue

        print(f"\n{label} (showing up to {issue_limit}):")
        for item in items[:issue_limit]:
            print(f"  {item}")

    has_issues = any([
        missing_ids,
        duplicate_ids,
        *[len(items) for _, items in issue_groups],
    ])

    print("\n--- Validation Result ---")
    if has_issues:
        print("Potential data-quality issues require investigation.")
    else:
        print("No issues detected by the implemented checks.")

    print("=" * 55)


if __name__ == "__main__":
    from src.data_loader import open_order

    orders = open_order()
    validate_orders(orders)
