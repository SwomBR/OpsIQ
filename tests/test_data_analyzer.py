
"""
OpsIQ - Business Operations Intelligence Platform

Module: test_data_analyzer.py

Purpose:
    Test the order analysis functionality using small sample datasets.
"""

import unittest
from unittest.mock import patch
from io import StringIO

from src.data_analyzer import analyze_orders


class TestAnalyzeOrders(unittest.TestCase):
    """Test the analyze_orders function."""

    def test_total_order_count(self):
        """Check whether the analyzer reports the correct total."""

        orders = [
            {"order_id": "A001", "order_status": "delivered"},
            {"order_id": "A002", "order_status": "shipped"},
            {"order_id": "A003", "order_status": "delivered"},
        ]

        with patch("sys.stdout", new_callable=StringIO) as output:
            analyze_orders(orders)

        self.assertIn("Total orders: 3", output.getvalue())

    def test_delivered_order_count(self):
        """Check whether delivered orders are counted correctly."""

        orders = [
            {"order_id": "A001", "order_status": "delivered"},
            {"order_id": "A002", "order_status": "shipped"},
            {"order_id": "A003", "order_status": "delivered"},
        ]

        with patch("sys.stdout", new_callable=StringIO) as output:
            analyze_orders(orders)

        self.assertIn("Delivered orders: 2", output.getvalue())

    def test_empty_dataset(self):
        """Check whether the analyzer handles an empty list."""

        with patch("sys.stdout", new_callable=StringIO) as output:
            analyze_orders([])

        self.assertIn(
            "No order data available to analyze.",
            output.getvalue()
        )


if __name__ == "__main__":
    unittest.main()
