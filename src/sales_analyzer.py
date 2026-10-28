"""
OpsIQ - Business Operations Intelligence Platform

Module: sales_analyzer.py

Purpose:
    Analyze product sales and customer payment data.

What this module does:
    1. Calculate total product sales revenue.
    2. Calculate total freight charges.
    3. Calculate average order value.
    4. Summarize payment values by payment method.
"""

import csv
from collections import defaultdict


def load_csv(file_path):
    """Load CSV records and return them as a list of dictionaries."""

    with open(
        file_path,
        mode="r",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        return list(csv.DictReader(file))


def analyze_sales(order_items, payments):
    """
    Calculate sales and payment metrics.

    Args:
        order_items: Records from the order-items CSV.
        payments: Records from the order-payments CSV.

    Returns:
        A dictionary containing sales and payment metrics.
    """

    # Calculate product revenue and freight separately.
    total_product_revenue = sum(
        float(item["price"]) for item in order_items
    )

    total_freight_charges = sum(
        float(item["freight_value"]) for item in order_items
    )

    # Count each order only once when calculating average order value.
    order_totals = defaultdict(float)

    for item in order_items:
        order_totals[item["order_id"]] += float(item["price"])

    total_orders = len(order_totals)

    average_order_value = (
        total_product_revenue / total_orders
        if total_orders
        else 0
    )

    # Group payment values by payment method.
    payment_method_totals = defaultdict(float)

    for payment in payments:
        method = payment["payment_type"]
        value = float(payment["payment_value"])
        payment_method_totals[method] += value

    return {
        "total_product_revenue": round(total_product_revenue, 2),
        "total_freight_charges": round(total_freight_charges, 2),
        "total_orders": total_orders,
        "average_order_value": round(average_order_value, 2),
        "payment_method_totals": {
            method: round(value, 2)
            for method, value in sorted(payment_method_totals.items())
        },
    }


if __name__ == "__main__":
    order_items = load_csv(
        "data/raw/olist_order_items_dataset.csv"
    )

    payments = load_csv(
        "data/raw/olist_order_payments_dataset.csv"
    )

    report = analyze_sales(order_items, payments)

    print("\n--- OpsIQ Sales & Payment Report ---")
    print("Total product revenue:", report["total_product_revenue"])
    print("Total freight charges:", report["total_freight_charges"])
    print("Total orders:", report["total_orders"])
    print("Average product value per order:", report["average_order_value"])

    print("\nPayment totals by method:")

    for method, value in report["payment_method_totals"].items():
        print(f"{method}: {value}")