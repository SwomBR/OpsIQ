
"""
OpsIQ - Business Operations Intelligence Platform

Module: data_validator.py

Purpose:
    Check the quality of order data loaded from the CSV file.

Checks performed:
    1. Identify missing values in each column.
    2. Check for missing order IDs.
    3. Identify duplicate order IDs.
"""


def check_missing_values(orders):
    """Count missing values in each column."""

    if not orders:
        return {}

    missing_counts = {}

    for column in orders[0].keys():
        missing_count = 0

        for order in orders:
            value = order.get(column)

            if value is None or value.strip() == "":
                missing_count += 1

        missing_counts[column] = missing_count

    return missing_counts


def check_missing_order_ids(orders):
    """Count orders that do not have an order ID."""

    missing_id_count = 0

    for order in orders:
        order_id = order.get("order_id")

        if order_id is None or order_id.strip() == "":
            missing_id_count += 1

    return missing_id_count


def check_duplicate_order_ids(orders):
    """Count repeated occurrences of order IDs."""

    seen_order_ids = set()
    duplicate_count = 0

    for order in orders:
        order_id = order.get("order_id")

        if order_id is None or order_id.strip() == "":
            continue

        if order_id in seen_order_ids:
            duplicate_count += 1
        else:
            seen_order_ids.add(order_id)

    return duplicate_count


def validate_orders(orders):
    """Run all order-data quality checks and print a report."""

    if not orders:
        print("No order data available to validate.")
        return

    print("\n--- OpsIQ Data Quality Report ---")

    missing_counts = check_missing_values(orders)

    print("\nMissing values by column:")

    for column, count in missing_counts.items():
        print(f"{column}: {count}")

    missing_ids = check_missing_order_ids(orders)
    duplicate_ids = check_duplicate_order_ids(orders)

    print("\nMissing order IDs:", missing_ids)
    print("Duplicate order ID occurrences:", duplicate_ids)


if __name__ == "__main__":
    from data_loader import open_order

    orders = open_order()
    validate_orders(orders)
