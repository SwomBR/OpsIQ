
"""Tests for the OpsIQ customer analyzer."""

import unittest

from src.customer_analyzer import analyze_customers


class TestCustomerAnalyzer(unittest.TestCase):

    def setUp(self):
        """Create a small dataset for testing."""

        self.customers = [
            {
                "customer_id": "C1",
                "customer_unique_id": "U1",
                "customer_state": "SP",
            },
            {
                "customer_id": "C2",
                "customer_unique_id": "U1",
                "customer_state": "SP",
            },
            {
                "customer_id": "C3",
                "customer_unique_id": "U2",
                "customer_state": "RJ",
            },
        ]

        self.orders = [
            {"order_id": "O1", "customer_id": "C1"},
            {"order_id": "O2", "customer_id": "C2"},
            {"order_id": "O3", "customer_id": "C3"},
        ]

        self.order_items = [
            {"order_id": "O1", "price": "100.00"},
            {"order_id": "O2", "price": "50.00"},
            {"order_id": "O3", "price": "200.00"},
        ]

    def test_counts_unique_customers(self):
        report = analyze_customers(
            self.orders, self.customers, self.order_items
        )
        self.assertEqual(report["total_unique_customers"], 2)

    def test_counts_repeat_customers(self):
        report = analyze_customers(
            self.orders, self.customers, self.order_items
        )
        self.assertEqual(report["repeat_customers"], 1)

    def test_calculates_repeat_percentage(self):
        report = analyze_customers(
            self.orders, self.customers, self.order_items
        )
        self.assertEqual(report["repeat_customer_percentage"], 50.0)

    def test_combines_spending_for_same_customer(self):
        report = analyze_customers(
            self.orders, self.customers, self.order_items
        )
        spending = dict(report["top_customers"])
        self.assertEqual(spending["U1"], 150.0)
        self.assertEqual(spending["U2"], 200.0)

    def test_counts_unique_customers_by_state(self):
        report = analyze_customers(
            self.orders, self.customers, self.order_items
        )
        self.assertEqual(report["customers_by_state"]["SP"], 1)
        self.assertEqual(report["customers_by_state"]["RJ"], 1)

    def test_handles_no_orders(self):
        report = analyze_customers([], self.customers, self.order_items)

        self.assertEqual(report["total_unique_customers"], 0)
        self.assertEqual(report["repeat_customers"], 0)
        self.assertEqual(report["repeat_customer_percentage"], 0)
        self.assertEqual(report["top_customers"], [])
        self.assertEqual(report["customers_by_state"], {})


if __name__ == "__main__":
    unittest.main()
