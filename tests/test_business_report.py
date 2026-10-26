"""
OpsIQ - Business Operations Intelligence Platform

Module: test_business_report.py

Purpose:
    Test the combined business summary report.

Tests included:
    1. Handle an empty dataset safely.
    2. Calculate business summary metrics correctly.
"""

import unittest
from io import StringIO
from unittest.mock import patch

from src.business_report import generate_business_report


class TestBusinessReport(unittest.TestCase):
    """Test business summary report generation."""

    def test_empty_dataset(self):
        """Check that an empty dataset is handled safely."""

        with patch("sys.stdout", new_callable=StringIO) as output:
            generate_business_report([])

        self.assertIn(
            "No order data available.",
            output.getvalue(),
        )

    def test_business_summary_metrics(self):
        """Check that summary metrics are calculated correctly."""

        orders = [
            {
                "order_id": "ORDER001",
                "order_status": "delivered",
                "order_delivered_customer_date": "2026-01-15 10:00:00",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            },
            {
                "order_id": "ORDER002",
                "order_status": "delivered",
                "order_delivered_customer_date": "2026-01-08 10:00:00",
                "order_estimated_delivery_date": "2026-01-10 10:00:00",
            },
            {
                "order_id": "ORDER003",
                "order_status": "shipped",
                "order_delivered_customer_date": "",
                "order_estimated_delivery_date": "2026-01-12 10:00:00",
            },
        ]

        with patch("sys.stdout", new_callable=StringIO) as output:
            generate_business_report(orders)

        report = output.getvalue()

        self.assertIn("Total orders: 3", report)
        self.assertIn("Delivered orders: 2", report)
        self.assertIn("Delivered order percentage: 66.67%", report)
        self.assertIn("Late-delivered orders: 1", report)
        self.assertIn("Order: ORDER001 | Days late: 5.0", report)
        self.assertIn("END OF OPSIQ REPORT", report)


if __name__ == "__main__":
    unittest.main()