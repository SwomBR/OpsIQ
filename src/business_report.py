"""
OpsIQ - Business Operations Intelligence Platform

Module: business_report.py

Purpose:
    Generate a combined business report containing:
    1. Order summary.
    2. Delivery performance.
    3. Priority delivery exceptions.
    4. Sales revenue and freight charges.
    5. Average product value per order.
    6. Payment method breakdown.
"""

from src.data_loader import open_order
from src.delivery_analyzer import analyze_delivery_performance
from src.delivery_exceptions import find_delivery_exceptions
from src.sales_analyzer import analyze_sales, load_csv


def generate_business_report(orders, sales_report=None):
    """Generate a combined business summary report."""

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

    if sales_report is not None:
        print("\n--- Sales & Payment Analytics ---")
        print(
            "Total product revenue: "
            f"{sales_report['total_product_revenue']:,.2f}"
        )
        print(
            "Total freight charges: "
            f"{sales_report['total_freight_charges']:,.2f}"
        )
        print(
            "Orders with item records: "
            f"{sales_report['total_orders']:,}"
        )
        print(
            "Average product value per order: "
            f"{sales_report['average_order_value']:,.2f}"
        )

        print("\nPayment totals by method:")

        for method, value in sales_report[
            "payment_method_totals"
        ].items():
            print(f"{method}: {value:,.2f}")

    print("\n" + "=" * 50)
    print("       END OF OPSIQ REPORT")
    print("=" * 50)


if __name__ == "__main__":
    orders = open_order()

    order_items = load_csv(
        "data/raw/olist_order_items_dataset.csv"
    )

    payments = load_csv(
        "data/raw/olist_order_payments_dataset.csv"
    )

    sales_report = analyze_sales(order_items, payments)

    generate_business_report(orders, sales_report)