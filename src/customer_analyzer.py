"""Analyze customer behavior and spending for the OpsIQ platform."""

from collections import defaultdict

from src.sales_analyzer import load_csv


def analyze_customers(orders, customers, order_items):
    """Calculate repeat customers, customer spending, and state distribution."""

    # Map each customer record to its unique customer identity.
    customer_id_to_unique_id = {
        customer["customer_id"]: customer["customer_unique_id"]
        for customer in customers
    }

    # Connect each order to the actual unique customer.
    order_to_customer = {
        order["order_id"]: customer_id_to_unique_id[order["customer_id"]]
        for order in orders
        if order.get("customer_id") in customer_id_to_unique_id
    }

    # Track each customer's distinct orders.
    customer_orders = defaultdict(set)

    for order_id, unique_id in order_to_customer.items():
        customer_orders[unique_id].add(order_id)

    total_unique_customers = len(customer_orders)

    repeat_customers = sum(
        1 for order_ids in customer_orders.values()
        if len(order_ids) > 1
    )

    repeat_percentage = (
        repeat_customers / total_unique_customers * 100
        if total_unique_customers
        else 0
    )

    # Calculate product spending for each unique customer.
    customer_spending = defaultdict(float)

    for item in order_items:
        unique_id = order_to_customer.get(item["order_id"])

        if unique_id is not None:
            customer_spending[unique_id] += float(item["price"] or 0)

    top_customers = sorted(
        customer_spending.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:10]

    # Count unique customers in each state.
    customers_by_state = defaultdict(set)

    for customer in customers:
        unique_id = customer["customer_unique_id"]
        state = customer["customer_state"]

        if unique_id in customer_orders:
            customers_by_state[state].add(unique_id)

    state_counts = {
        state: len(unique_ids)
        for state, unique_ids in customers_by_state.items()
    }

    return {
        "total_unique_customers": total_unique_customers,
        "repeat_customers": repeat_customers,
        "repeat_customer_percentage": repeat_percentage,
        "top_customers": top_customers,
        "customers_by_state": state_counts,
    }


if __name__ == "__main__":
    orders = load_csv("data/raw/olist_orders_dataset.csv")
    customers = load_csv("data/raw/olist_customers_dataset.csv")
    order_items = load_csv("data/raw/olist_order_items_dataset.csv")

    report = analyze_customers(orders, customers, order_items)

    print("\nCUSTOMER ANALYSIS")
    print("-" * 40)
    print(f"Unique customers: {report['total_unique_customers']:,}")
    print(f"Repeat customers: {report['repeat_customers']:,}")
    print(
        "Repeat customer percentage: "
        f"{report['repeat_customer_percentage']:.2f}%"
    )

    print("\nTop 10 customers by product spending:")
    for customer_id, spending in report["top_customers"]:
        print(f"{customer_id}: {spending:,.2f}")

    print("\nTop 10 states by unique customer count:")
    for state, count in sorted(
        report["customers_by_state"].items(),
        key=lambda item: item[1],
        reverse=True,
    )[:10]:
        print(f"{state}: {count:,} customers")