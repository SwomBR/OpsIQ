
"""
OpsIQ - Business Operations Intelligence Platform

Module: test_delivery_analyzer.py

Purpose:
    Test delivery performance calculations using sample orders.

Tests included:
    1. Check on-time and late order counts.
    2. Check handling of missing delivery dates.
    3. Check that non-delivered orders are ignored.
    4. Check average and maximum delay calculations.
    5. Check orders delayed by more than 3 and 7 days.
    6. Check that delivery on the estimated date counts as on time.
"""

import unittest
from unittest.mock import patch
from io import StringIO

from src.delivery_analyzer import (
    analyze_delivery_performance,
    calculate_delivery_performance,
)


class TestDeliveryAnalyzer(unittest.TestCase):
    """Test delivery performance analysis."""

    def test_on_time_and_late_orders(self):
        """Check that on-time and late orders are counted correctly."""

        orders = [
            {
                "order_status": "delivered",
                "order_delivered_customer_date": "2026-01-10 10:00:00",
                "order_estimated_delivery_date": "2026-01-12 10:00:00",
            },
            {
                "order_status": "delivered",
                "order_delivered_customer_date": "2026-01-15 10:00:00",
                "order_estimated_delivery_date": "2026-01-12 10:00:00",
            },
        ]

        with patch("sys.stdout", new_callable=StringIO) as output:
            analyze_delivery_performance(orders)

        report = output.getvalue()

        self.assertIn("Delivered orders analyzed: 2", report)
        self.assertIn("On-time orders: 1", report)
        self.assertIn("Late orders: 1", report)
        self.assertIn("On-time delivery percentage: 50.00%", report)
        self.assertIn("Late delivery percentage: 50.00%", report)

    def test_missing_delivery_date(self):
        """Check that an order with a missing date is skipped."""

        orders = [
            {
                "order_status": "delivered",
                "order_delivered_customer_date": "",
                "order_estimated_delivery_date": "2026-01-12 10:00:00",
            }
        ]

        with patch("sys.stdout", new_callable=StringIO) as output:
            analyze_delivery_performance(orders)

        report = output.getvalue()

        self.assertIn("Delivered orders analyzed: 0", report)
        self.assertIn(
            "Orders skipped due to missing or invalid dates: 1",
            report,
        )

    def test_non_delivered_order_is_ignored(self):
        """Check that orders not marked delivered are not analyzed."""

        orders = [
            {
                "order_status": "shipped",
                "order_delivered_customer_date": "",
                "order_estimated_delivery_date": "2026-01-12 10:00:00",
            }
        ]

        with patch("sys.stdout", new_callable=StringIO) as output:
            analyze_delivery_performance(orders)

        report = output.getvalue()

        self.assertIn("Delivered orders analyzed: 0", report)
        self.assertIn("On-time orders: 0", report)
        self.assertIn("Late orders: 0", report)

    def test_delay_duration_metrics(self):
        """Check average, maximum, and long-delay calculations."""

        orders = [
            {
                "order_status": "delivered",
                "order_delivered_customer_date": "2026-01-13 10:00:00",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            },
            {
                "order_status": "delivered",
                "order_delivered_customer_date": "2026-01-20 10:00:00",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            },
            {
                "order_status": "delivered",
                "order_delivered_customer_date": "2026-01-11 10:00:00",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            },
        ]

        with patch("sys.stdout", new_callable=StringIO) as output:
            analyze_delivery_performance(orders)

        report = output.getvalue()

        self.assertIn("Average delay among late orders: 4.67 days", report)
        self.assertIn("Maximum delivery delay: 10.00 days", report)
        self.assertIn("Orders delayed more than 3 days: 1", report)
        self.assertIn("Orders delayed more than 7 days: 1", report)

    def test_delivery_on_estimated_date_is_on_time(self):
        """Check that delivery exactly on the estimated date is on time."""

        orders = [
            {
                "order_status": "delivered",
                "order_delivered_customer_date": "2026-01-10 10:00:00",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            }
        ]

        with patch("sys.stdout", new_callable=StringIO) as output:
            analyze_delivery_performance(orders)

        report = output.getvalue()

        self.assertIn("On-time orders: 1", report)
        self.assertIn("Late orders: 0", report)
        self.assertIn("On-time delivery percentage: 100.00%", report)


class TestCalculateDeliveryPerformance(unittest.TestCase):
    """Test the calculate_delivery_performance helper."""

    def test_returns_all_metrics(self):
        """Check every metric returned for a mix of orders."""

        orders = [
            {
                "order_status": "delivered",
                "order_delivered_customer_date": "2026-01-10 10:00:00",
                "order_estimated_delivery_date": "2026-01-12 10:00:00",
            },
            {
                "order_status": "delivered",
                "order_delivered_customer_date": "2026-01-14 10:00:00",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            },
            {
                "order_status": "delivered",
                "order_delivered_customer_date": "2026-01-20 10:00:00",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            },
            {
                "order_status": "delivered",
                "order_delivered_customer_date": "",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            },
            {
                "order_status": "shipped",
                "order_delivered_customer_date": "",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            },
        ]

        metrics = calculate_delivery_performance(orders)

        self.assertEqual(metrics["delivered_orders_analyzed"], 3)
        self.assertEqual(metrics["on_time_orders"], 1)
        self.assertEqual(metrics["late_orders"], 2)
        self.assertEqual(metrics["skipped_orders"], 1)
        self.assertAlmostEqual(metrics["on_time_percentage"], 100 / 3)
        self.assertAlmostEqual(metrics["late_percentage"], 200 / 3)
        self.assertAlmostEqual(metrics["average_delay_days"], 7.0)
        self.assertAlmostEqual(metrics["maximum_delay_days"], 10.0)
        self.assertEqual(metrics["delayed_more_than_3_days"], 2)
        self.assertEqual(metrics["delayed_more_than_7_days"], 1)

    def test_no_late_orders_gives_zero_delays(self):
        """Check that delays are zero when every order is on time."""

        orders = [
            {
                "order_status": "delivered",
                "order_delivered_customer_date": "2026-01-10 10:00:00",
                "order_estimated_delivery_date": "2026-01-12 10:00:00",
            }
        ]

        metrics = calculate_delivery_performance(orders)

        self.assertEqual(metrics["late_percentage"], 0.0)
        self.assertEqual(metrics["average_delay_days"], 0.0)
        self.assertEqual(metrics["maximum_delay_days"], 0.0)

    def test_empty_dataset_has_no_percentages(self):
        """Check that percentages and delays are None without data."""

        metrics = calculate_delivery_performance([])

        self.assertEqual(metrics["delivered_orders_analyzed"], 0)
        self.assertIsNone(metrics["on_time_percentage"])
        self.assertIsNone(metrics["late_percentage"])
        self.assertIsNone(metrics["average_delay_days"])
        self.assertIsNone(metrics["maximum_delay_days"])


if __name__ == "__main__":
    unittest.main()
