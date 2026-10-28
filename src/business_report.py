
"""
OpsIQ - Business Operations Intelligence Platform

Module: business_report.py

Purpose:
    Generate a consolidated business report covering:
    1. Order summary.
    2. Delivery performance.
    3. Priority delivery exceptions.
    4. Sales and payment analytics.
    5. Product and category performance.
    6. Customer behavior and geographic distribution.
"""

from src.data_loader import open_order
from src.delivery_analyzer import analyze_delivery_performance
from src.delivery_exceptions import find_delivery_exceptions
from src.sales_analyzer import analyze_sales, load_csv
from src.product_analyzer import analyze_products
from src.customer_analyzer import analyze_customers


def generate_business_report(
    orders,
    sales_report=None,
    product_report=None,
    customer_report=None,
):
    """Generate a consolidated business summary report."""

    if not orders:
        print("No order data available.")
        return

    total_orders = len(orders)

    delivered_orders = sum(
        1
        for order in orders
        if order.get("order_status") == "delivered"
    )

    delivered_percentage = delivered_orders / total_orders * 100
    exceptions = find_delivery_exceptions(orders)

    print("\n" + "=" * 55)
    print("          OPSIQ BUSINESS SUMMARY REPORT")
    print("=" * 55)

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
            f"Total product revenue: "
            f"{sales_report['total_product_revenue']:,.2f}"
        )
        print(
            f"Total freight charges: "
            f"{sales_report['total_freight_charges']:,.2f}"
        )
        print(
            f"Orders with item records: "
            f"{sales_report['total_orders']:,}"
        )
        print(
            f"Average product value per order: "
            f"{sales_report['average_order_value']:,.2f}"
        )

        print("\nPayment totals by method:")

        for method, value in sales_report[
            "payment_method_totals"
        ].items():
            print(f"{method}: {value:,.2f}")

    if product_report is not None:
        print("\n--- Product Performance Analytics ---")
        print(f"Products in catalog: {product_report['total_products']:,}")
        print(
            "Products missing category: "
            f"{product_report['products_missing_category']:,}"
        )

        print("\nTop 5 categories by revenue:")

        for category in product_report["top_categories"][:5]:
            print(
                f"{category['category']}: "
                f"Revenue = {category['revenue']:,.2f}, "
                f"Items sold = {category['quantity_sold']:,}"
            )

        print("\nTop 5 products by quantity sold:")

        for product in product_report["top_products"][:5]:
            print(
                f"Product ID: {product['product_id']} | "
                f"Items sold: {product['quantity_sold']:,} | "
                f"Revenue: {product['revenue']:,.2f}"
            )

    if customer_report is not None:
        print("\n--- Customer Analytics ---")
        print(
            f"Unique customers: "
            f"{customer_report['total_unique_customers']:,}"
        )
        print(
            f"Repeat customers: "
            f"{customer_report['repeat_customers']:,}"
        )
        print(
            f"Repeat customer percentage: "
            f"{customer_report['repeat_customer_percentage']:.2f}%"
        )

        print("\nTop 5 customers by product spending:")

        for customer_id, spending in customer_report["top_customers"][:5]:
            print(
                f"Customer ID: {customer_id} | "
                f"Product spending: {spending:,.2f}"
            )

        print("\nTop 10 states by unique customer count:")

        top_states = sorted(
            customer_report["customers_by_state"].items(),
            key=lambda item: item[1],
            reverse=True,
        )[:10]

        for state, count in top_states:
            print(f"{state}: {count:,} customers")

    print("\n" + "=" * 55)
    print("             END OF OPSIQ REPORT")
    print("=" * 55)


if __name__ == "__main__":
    orders = open_order()

    order_items = load_csv(
        "data/raw/olist_order_items_dataset.csv"
    )
    payments = load_csv(
        "data/raw/olist_order_payments_dataset.csv"
    )
    products = load_csv(
        "data/raw/olist_products_dataset.csv"
    )
    customers = load_csv(
        "data/raw/olist_customers_dataset.csv"
    )
    translations = load_csv(
        "data/raw/product_category_name_translation.csv"
    )

    sales_report = analyze_sales(order_items, payments)

    category_translations = {
        row["product_category_name"]: row["product_category_name_english"]
        for row in translations
    }

    product_report = analyze_products(
        order_items,
        products,
        category_translations,
    )

    customer_report = analyze_customers(
        orders,
        customers,
        order_items,
    )

    generate_business_report(
        orders,
        sales_report,
        product_report,
        customer_report,
    )
