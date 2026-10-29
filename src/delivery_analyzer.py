
"""
OpsIQ - Business Operations Intelligence Platform

Module: delivery_analyzer.py

Purpose:
    Analyze delivery performance by comparing actual delivery dates
    with estimated delivery dates.

Analysis performed:
    1. Count delivered orders with valid delivery dates.
    2. Count orders delivered on time and late.
    3. Calculate on-time and late delivery percentages.
    4. Calculate the average delay for late orders.
    5. Identify the maximum delivery delay.
    6. Count orders delayed by more than 3 and 7 days.
"""

from datetime import datetime


def calculate_delivery_performance(orders):
    """Calculate delivery timeliness and delay metrics.

    Returns:
        dict: The delivery metrics. Percentages, the average delay,
        and the maximum delay are None when no delivered orders
        with valid dates are available.
    """

    delivered_orders = 0
    on_time_orders = 0
    late_orders = 0
    skipped_orders = 0

    total_delay_seconds = 0
    maximum_delay_seconds = 0

    delayed_more_than_3_days = 0
    delayed_more_than_7_days = 0

    for order in orders:

        # Analyze only orders marked as delivered.
        if order.get("order_status") != "delivered":
            continue

        actual_date_text = order.get(
            "order_delivered_customer_date", ""
        )
        estimated_date_text = order.get(
            "order_estimated_delivery_date", ""
        )

        # Skip records with missing dates.
        if not actual_date_text or not estimated_date_text:
            skipped_orders += 1
            continue

        try:
            actual_date = datetime.strptime(
                actual_date_text, "%Y-%m-%d %H:%M:%S"
            )

            estimated_date = datetime.strptime(
                estimated_date_text, "%Y-%m-%d %H:%M:%S"
            )

        except ValueError:
            skipped_orders += 1
            continue

        delivered_orders += 1

        # Calculate the difference between actual and estimated delivery.
        delay = actual_date - estimated_date

        if delay.total_seconds() <= 0:
            on_time_orders += 1
            continue

        # The order was delivered late.
        late_orders += 1

        delay_seconds = delay.total_seconds()
        total_delay_seconds += delay_seconds

        maximum_delay_seconds = max(
            maximum_delay_seconds, delay_seconds
        )

        delay_days = delay.total_seconds() / 86400

        if delay_days > 3:
            delayed_more_than_3_days += 1

        if delay_days > 7:
            delayed_more_than_7_days += 1

    on_time_percentage = None
    late_percentage = None
    average_delay_days = None
    maximum_delay_days = None

    if delivered_orders > 0:
        on_time_percentage = (on_time_orders / delivered_orders) * 100
        late_percentage = (late_orders / delivered_orders) * 100

        if late_orders > 0:
            average_delay_days = (
                total_delay_seconds / late_orders / 86400
            )
            maximum_delay_days = maximum_delay_seconds / 86400
        else:
            average_delay_days = 0.0
            maximum_delay_days = 0.0

    return {
        "delivered_orders_analyzed": delivered_orders,
        "on_time_orders": on_time_orders,
        "late_orders": late_orders,
        "skipped_orders": skipped_orders,
        "on_time_percentage": on_time_percentage,
        "late_percentage": late_percentage,
        "average_delay_days": average_delay_days,
        "maximum_delay_days": maximum_delay_days,
        "delayed_more_than_3_days": delayed_more_than_3_days,
        "delayed_more_than_7_days": delayed_more_than_7_days,
    }


def analyze_delivery_performance(orders):
    """Analyze delivery timeliness and delay duration."""

    if not orders:
        print("No order data available to analyze.")
        return

    metrics = calculate_delivery_performance(orders)

    print("\n--- OpsIQ Delivery Performance Report ---")

    print("Delivered orders analyzed:", metrics["delivered_orders_analyzed"])
    print("On-time orders:", metrics["on_time_orders"])
    print("Late orders:", metrics["late_orders"])
    print(
        "Orders skipped due to missing or invalid dates:",
        metrics["skipped_orders"]
    )

    if metrics["delivered_orders_analyzed"] == 0:
        print("No delivered orders with valid dates were available.")
        return

    print(f"On-time delivery percentage: {metrics['on_time_percentage']:.2f}%")
    print(f"Late delivery percentage: {metrics['late_percentage']:.2f}%")
    print(
        "Average delay among late orders: "
        f"{metrics['average_delay_days']:.2f} days"
    )
    print(f"Maximum delivery delay: {metrics['maximum_delay_days']:.2f} days")

    print(
        "Orders delayed more than 3 days:",
        metrics["delayed_more_than_3_days"]
    )
    print(
        "Orders delayed more than 7 days:",
        metrics["delayed_more_than_7_days"]
    )


if __name__ == "__main__":
    from src.data_loader import open_order

    orders = open_order()
    analyze_delivery_performance(orders)
