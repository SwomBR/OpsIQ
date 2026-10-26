"""
OpsIQ - Business Operations Intelligence Platform

Module: business_report.py

Purpose:
    Generate a combined business summary using order analysis,
    delivery performance analysis, and delivery exceptions.
"""

from src.data_loader import open_order
from src.delivery_analyzer import analyze_delivery_performance
from src.delivery_exceptions import find_delivery_exceptions


def generate_business_report(orders):
    """Generate a business-friendly summary of order performance."""

    if not orders:
        print("No order data available.")
        return

    total_orders = len(orders)

    delivered_orders = sum(
        1
        for order in orders
        if order.get("order_status") == "delivered"
    )

    delivered_percentage = (
        delivered_orders / total_orders
    ) * 100

    exceptions = find_delivery_exceptions(orders)

    print("\n" + "=" * 50)
    print("       OPSIQ BUSINESS SUMMARY REPORT")
    print("=" * 50)

    print(f"Total orders: {total_orders:,}")
    print(f"Delivered orders: {delivered_orders:,}")
    print(f"Delivered order percentage: {delivered_percentage:.2f}%")
    print(f"Late-delivered orders: {len(exceptions):,}")

    print("\n--- Delivery Performance Details ---")
    analyze_delivery_performance(orders)

    print("\n--- Highest-Priority Delivery Exceptions ---")

    if not exceptions:
        print("No late-delivered orders found.")
    else:
        for exception in exceptions[:5]:
            print(
                f"Order: {exception['order_id']} | "
                f"Days late: {exception['days_late']}"
            )

    print("\n" + "=" * 50)
    print("       END OF OPSIQ REPORT")
    print("=" * 50)


if __name__ == "__main__":
    orders = open_order()
    generate_business_report(orders)