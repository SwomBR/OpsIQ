"""
OpsIQ - Business Operations Intelligence Platform

Module: delivery_exceptions.py

Purpose:
    Identify delivered orders that arrived later than their
    estimated delivery dates.

Features:
    1. Find late-delivered orders.
    2. Calculate the delay in days for each order.
    3. Record the order ID and delivery dates.
    4. Sort orders from the longest delay to the shortest.
    5. Display the most delayed orders for investigation.
"""

from datetime import datetime


def find_delivery_exceptions(orders):
    """Find and return delivered orders that arrived late."""

    exceptions = []

    for order in orders:

        # Only analyze orders marked as delivered.
        if order.get("order_status") != "delivered":
            continue

        actual_date_text = order.get(
            "order_delivered_customer_date", ""
        )
        estimated_date_text = order.get(
            "order_estimated_delivery_date", ""
        )

        # Skip orders with missing delivery dates.
        if not actual_date_text or not estimated_date_text:
            continue

        try:
            actual_date = datetime.strptime(
                actual_date_text, "%Y-%m-%d %H:%M:%S"
            )

            estimated_date = datetime.strptime(
                estimated_date_text, "%Y-%m-%d %H:%M:%S"
            )

        except ValueError:
            # Skip records with dates in an unexpected format.
            continue

        delay = actual_date - estimated_date

        # Only keep orders delivered after the estimated date.
        if delay.total_seconds() > 0:

            delay_days = delay.total_seconds() / 86400

            exception = {
                "order_id": order.get("order_id", ""),
                "estimated_delivery": estimated_date_text,
                "actual_delivery": actual_date_text,
                "days_late": round(delay_days, 2),
            }

            exceptions.append(exception)

    # Show the longest delays first.
    exceptions.sort(
        key=lambda exception: exception["days_late"],
        reverse=True,
    )

    return exceptions


def display_delivery_exceptions(exceptions, limit=10):
    """Display the most delayed orders in a readable report."""

    print("\n--- OpsIQ Delivery Exception Report ---")

    print("Total late orders found:", len(exceptions))

    if not exceptions:
        print("No late-delivered orders found.")
        return

    print(f"\nShowing the top {min(limit, len(exceptions))} delayed orders:\n")

    for exception in exceptions[:limit]:
        print("Order ID:", exception["order_id"])
        print("Estimated delivery:", exception["estimated_delivery"])
        print("Actual delivery:", exception["actual_delivery"])
        print("Days late:", exception["days_late"])
        print("-" * 40)


if __name__ == "__main__":
    from data_loader import open_order

    orders = open_order()

    exceptions = find_delivery_exceptions(orders)

    display_delivery_exceptions(exceptions)