
"""
OpsIQ - Business Operations Intelligence Platform

Module: data_analyzer.py

Purpose:
    Analyze order data and generate basic business insights.

Analysis performed:
    1. Count total orders.
    2. Count orders by status.
    3. Calculate the percentage of delivered orders.
"""


def analyze_orders(orders):
    """Analyze orders and print a business summary."""

    if not orders:
        print("No order data available to analyze.")
        return

    # Count all order records.
    total_orders = len(orders)

    # Count orders belonging to each status.
    status_counts = {}

    for order in orders:
        status = order.get("order_status", "unknown")

        if status in status_counts:
            status_counts[status] += 1
        else:
            status_counts[status] = 1

    # Find the number of delivered orders.
    delivered_orders = status_counts.get("delivered", 0)

    # Calculate the percentage of delivered orders.
    delivered_percentage = (delivered_orders / total_orders) * 100

    # Display the business summary.
    print("\n--- OpsIQ Order Analysis Report ---")

    print("\nTotal orders:", total_orders)

    print("\nOrders by status:")

    for status, count in sorted(status_counts.items()):
        print(f"{status}: {count}")

    print(f"\nDelivered orders: {delivered_orders}")

    print(f"Delivered order percentage: {delivered_percentage:.2f}%")


if __name__ == "__main__":
    from data_loader import open_order

    orders = open_order()
    analyze_orders(orders)
