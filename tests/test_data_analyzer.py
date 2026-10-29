
"""
OpsIQ - Business Operations Intelligence Platform

Module: test_data_analyzer.py

Purpose:
    Test the order analysis functionality using small sample datasets.
"""

import unittest
from unittest.mock import patch
from io import StringIO

from src.data_analyzer import analyze_orders, count_orders_by_status


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


class TestCountOrdersByStatus(unittest.TestCase):
    """Test the count_orders_by_status helper."""

    def test_counts_each_status(self):
        """Check that every status is counted separately."""

        orders = [
            {"order_id": "A001", "order_status": "delivered"},
            {"order_id": "A002", "order_status": "shipped"},
            {"order_id": "A003", "order_status": "delivered"},
            {"order_id": "A004", "order_status": "canceled"},
        ]

        self.assertEqual(
            count_orders_by_status(orders),
            {"delivered": 2, "shipped": 1, "canceled": 1},
        )

    def test_missing_status_counts_as_unknown(self):
        """Check that a record without a status is counted as unknown."""

        orders = [{"order_id": "A001"}]

        self.assertEqual(count_orders_by_status(orders), {"unknown": 1})

    def test_empty_dataset_returns_empty_counts(self):
        """Check that an empty list produces no status counts."""

        self.assertEqual(count_orders_by_status([]), {})


if __name__ == "__main__":
    unittest.main()
