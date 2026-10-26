"""
OpsIQ - Business Operations Intelligence Platform

Module: test_delivery_exceptions.py

Purpose:
    Test the delivery exception detection feature.

Tests included:
    1. Identify late-delivered orders.
    2. Ignore orders delivered early or on time.
    3. Ignore orders that have not been delivered.
    4. Skip orders with missing or invalid dates.
    5. Sort exceptions from longest delay to shortest.
"""

import unittest

from src.delivery_exceptions import find_delivery_exceptions


class TestDeliveryExceptions(unittest.TestCase):
    """Test delivery exception detection."""

    def test_identifies_late_orders(self):
        """Check that a late order is identified correctly."""

        orders = [
            {
                "order_id": "ORDER001",
                "order_status": "delivered",
                "order_delivered_customer_date": "2026-01-15 10:00:00",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            }
        ]

        exceptions = find_delivery_exceptions(orders)

        self.assertEqual(len(exceptions), 1)
        self.assertEqual(exceptions[0]["order_id"], "ORDER001")
        self.assertEqual(exceptions[0]["days_late"], 5.0)

    def test_ignores_early_and_on_time_orders(self):
        """Check that early and on-time orders are not exceptions."""

        orders = [
            {
                "order_id": "ORDER001",
                "order_status": "delivered",
                "order_delivered_customer_date": "2026-01-08 10:00:00",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            },
            {
                "order_id": "ORDER002",
                "order_status": "delivered",
                "order_delivered_customer_date": "2026-01-10 10:00:00",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            },
        ]

        exceptions = find_delivery_exceptions(orders)

        self.assertEqual(len(exceptions), 0)

    def test_ignores_orders_not_delivered(self):
        """Check that shipped orders are not included."""

        orders = [
            {
                "order_id": "ORDER003",
                "order_status": "shipped",
                "order_delivered_customer_date": "",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            }
        ]

        exceptions = find_delivery_exceptions(orders)

        self.assertEqual(len(exceptions), 0)

    def test_skips_missing_or_invalid_dates(self):
        """Check that missing or incorrectly formatted dates are skipped."""

        orders = [
            {
                "order_id": "ORDER004",
                "order_status": "delivered",
                "order_delivered_customer_date": "",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            },
            {
                "order_id": "ORDER005",
                "order_status": "delivered",
                "order_delivered_customer_date": "not-a-date",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            },
        ]

        exceptions = find_delivery_exceptions(orders)

        self.assertEqual(len(exceptions), 0)

    def test_sorts_longest_delay_first(self):
        """Check that the most delayed order appears first."""

        orders = [
            {
                "order_id": "ORDER001",
                "order_status": "delivered",
                "order_delivered_customer_date": "2026-01-12 10:00:00",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            },
            {
                "order_id": "ORDER002",
                "order_status": "delivered",
                "order_delivered_customer_date": "2026-01-20 10:00:00",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            },
            {
                "order_id": "ORDER003",
                "order_status": "delivered",
                "order_delivered_customer_date": "2026-01-15 10:00:00",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            },
        ]

        exceptions = find_delivery_exceptions(orders)

        self.assertEqual(len(exceptions), 3)
        self.assertEqual(exceptions[0]["order_id"], "ORDER002")
        self.assertEqual(exceptions[1]["order_id"], "ORDER003")
        self.assertEqual(exceptions[2]["order_id"], "ORDER001")

        self.assertEqual(
            [item["days_late"] for item in exceptions],
            [10.0, 5.0, 2.0],
        )


if __name__ == "__main__":
    unittest.main()
    