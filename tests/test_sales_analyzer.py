"""Tests for the OpsIQ sales analyzer."""

import unittest

from src.sales_analyzer import analyze_sales


class TestSalesAnalyzer(unittest.TestCase):

    def setUp(self):
        """Prepare small sample datasets for testing."""

        self.order_items = [
            {
                "order_id": "order_1",
                "price": "100.00",
                "freight_value": "10.00",
            },
            {
                "order_id": "order_1",
                "price": "50.00",
                "freight_value": "5.00",
            },
            {
                "order_id": "order_2",
                "price": "200.00",
                "freight_value": "20.00",
            },
        ]

        self.payments = [
            {
                "order_id": "order_1",
                "payment_type": "credit_card",
                "payment_value": "150.00",
            },
            {
                "order_id": "order_2",
                "payment_type": "boleto",
                "payment_value": "220.00",
            },
            {
                "order_id": "order_2",
                "payment_type": "credit_card",
                "payment_value": "0.00",
            },
        ]

    def test_total_product_revenue(self):
        report = analyze_sales(self.order_items, self.payments)
        self.assertEqual(report["total_product_revenue"], 350.00)

    def test_total_freight_charges(self):
        report = analyze_sales(self.order_items, self.payments)
        self.assertEqual(report["total_freight_charges"], 35.00)

    def test_total_orders_counted_once(self):
        report = analyze_sales(self.order_items, self.payments)
        self.assertEqual(report["total_orders"], 2)

    def test_average_product_value_per_order(self):
        report = analyze_sales(self.order_items, self.payments)
        self.assertEqual(report["average_order_value"], 175.00)

    def test_payment_totals_by_method(self):
        report = analyze_sales(self.order_items, self.payments)

        self.assertEqual(
            report["payment_method_totals"],
            {
                "boleto": 220.00,
                "credit_card": 150.00,
            },
        )


if __name__ == "__main__":
    unittest.main()