"""
OpsIQ - Business Operations Intelligence Platform

Module: product_analyzer.py

Purpose:
    Analyze product sales and category performance.

Features:
    1. Calculate revenue by product category.
    2. Identify top-selling products by quantity.
    3. Calculate total products in the catalog.
    4. Report products with missing category information.
"""

from collections import defaultdict


def analyze_products(order_items, products, category_translations=None):
    """Generate product and category performance metrics."""

    category_translations = category_translations or {}

    # Map each product ID to its category.
    product_categories = {
        product["product_id"]: (
            product.get("product_category_name") or "unknown"
        )
        for product in products
    }

    # Accumulate sales quantity and revenue.
    category_revenue = defaultdict(float)
    category_quantity = defaultdict(int)
    product_quantity = defaultdict(int)
    product_revenue = defaultdict(float)

    for item in order_items:
        product_id = item["product_id"]
        category = product_categories.get(product_id, "unknown")
        category = category_translations.get(category, category)

        quantity = int(item["order_item_id"] != "")
        price = float(item["price"])

        category_revenue[category] += price
        category_quantity[category] += quantity

        product_quantity[product_id] += quantity
        product_revenue[product_id] += price

    # Sort categories and products from highest to lowest.
    top_categories = sorted(
        [
            {
                "category": category,
                "revenue": round(revenue, 2),
                "quantity_sold": category_quantity[category],
            }
            for category, revenue in category_revenue.items()
        ],
        key=lambda record: record["revenue"],
        reverse=True,
    )

    top_products = sorted(
        [
            {
                "product_id": product_id,
                "quantity_sold": quantity,
                "revenue": round(product_revenue[product_id], 2),
            }
            for product_id, quantity in product_quantity.items()
        ],
        key=lambda record: record["quantity_sold"],
        reverse=True,
    )

    return {
        "total_products": len(products),
        "products_missing_category": sum(
            1
            for product in products
            if not product.get("product_category_name")
        ),
        "top_categories": top_categories[:10],
        "top_products": top_products[:10],
    }


if __name__ == "__main__":
    from src.sales_analyzer import load_csv

    order_items = load_csv(
        "data/raw/olist_order_items_dataset.csv"
    )

    products = load_csv(
        "data/raw/olist_products_dataset.csv"
    )

    translations = load_csv(
        "data/raw/product_category_name_translation.csv"
    )

    category_translations = {
        row["product_category_name"]: row["product_category_name_english"]
        for row in translations
    }

    report = analyze_products(
        order_items,
        products,
        category_translations,
    )

    print("\n--- OpsIQ Product Performance Report ---")
    print("Products in catalog:", report["total_products"])
    print(
        "Products missing category:",
        report["products_missing_category"],
    )

    print("\nTop 10 categories by revenue:")

    for category in report["top_categories"]:
        print(
            f"{category['category']}: "
            f"Revenue = {category['revenue']:,.2f}, "
            f"Quantity sold = {category['quantity_sold']:,}"
        )

    print("\nTop 10 products by quantity sold:")

    for product in report["top_products"]:
        print(
            f"Product ID: {product['product_id']} | "
            f"Quantity sold: {product['quantity_sold']} | "
            f"Revenue: {product['revenue']:,.2f}"
        )