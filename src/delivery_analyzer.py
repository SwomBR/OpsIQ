
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


def analyze_delivery_performance(orders):
    """Analyze delivery timeliness and delay duration."""

    if not orders:
        print("No order data available to analyze.")
        return

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

    print("\n--- OpsIQ Delivery Performance Report ---")

    print("Delivered orders analyzed:", delivered_orders)
    print("On-time orders:", on_time_orders)
    print("Late orders:", late_orders)
    print("Orders skipped due to missing or invalid dates:", skipped_orders)

    if delivered_orders == 0:
        print("No delivered orders with valid dates were available.")
        return

    on_time_percentage = (on_time_orders / delivered_orders) * 100
    late_percentage = (late_orders / delivered_orders) * 100

    print(f"On-time delivery percentage: {on_time_percentage:.2f}%")
    print(f"Late delivery percentage: {late_percentage:.2f}%")

    if late_orders > 0:
        average_delay_days = (
            total_delay_seconds / late_orders / 86400
        )
        maximum_delay_days = maximum_delay_seconds / 86400

        print(f"Average delay among late orders: {average_delay_days:.2f} days")
        print(f"Maximum delivery delay: {maximum_delay_days:.2f} days")
    else:
        print("Average delay among late orders: 0.00 days")
        print("Maximum delivery delay: 0.00 days")

    print(
        "Orders delayed more than 3 days:",
        delayed_more_than_3_days
    )
    print(
        "Orders delayed more than 7 days:",
        delayed_more_than_7_days
    )


if __name__ == "__main__":
    from data_loader import open_order

    orders = open_order()
    analyze_delivery_performance(orders)
