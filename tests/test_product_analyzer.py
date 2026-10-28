"""Automated tests for OpsIQ product analytics."""

import unittest

from src.product_analyzer import analyze_products


class TestProductAnalyzer(unittest.TestCase):

    def setUp(self):
        self.products = [
            {
                "product_id": "P001",
                "product_category_name": "electronics",
            },
            {
                "product_id": "P002",
                "product_category_name": "books",
            },
            {
                "product_id": "P003",
                "product_category_name": "",
            },
        ]

        self.order_items = [
            {
                "order_id": "O001",
                "order_item_id": "1",
                "product_id": "P001",
                "price": "100.00",
            },
            {
                "order_id": "O002",
                "order_item_id": "1",
                "product_id": "P001",
                "price": "50.00",
            },
            {
                "order_id": "O003",
                "order_item_id": "1",
                "product_id": "P002",
                "price": "25.00",
            },
        ]

    def test_total_products(self):
        report = analyze_products(self.order_items, self.products)
        self.assertEqual(report["total_products"], 3)

    def test_missing_product_categories(self):
        report = analyze_products(self.order_items, self.products)
        self.assertEqual(report["products_missing_category"], 1)

    def test_category_revenue(self):
        report = analyze_products(self.order_items, self.products)

        categories = {
            item["category"]: item
            for item in report["top_categories"]
        }

        self.assertEqual(categories["electronics"]["revenue"], 150.00)
        self.assertEqual(categories["books"]["revenue"], 25.00)

    def test_category_quantity(self):
        report = analyze_products(self.order_items, self.products)

        categories = {
            item["category"]: item
            for item in report["top_categories"]
        }

        self.assertEqual(categories["electronics"]["quantity_sold"], 2)
        self.assertEqual(categories["books"]["quantity_sold"], 1)

    def test_top_product_quantity(self):
        report = analyze_products(self.order_items, self.products)

        self.assertEqual(
            report["top_products"][0]["product_id"],
            "P001",
        )

        self.assertEqual(
            report["top_products"][0]["quantity_sold"],
            2,
        )

    def test_category_translation(self):
        translations = {"electronics": "Electronics"}

        report = analyze_products(
            self.order_items,
            self.products,
            translations,
        )

        categories = [
            item["category"]
            for item in report["top_categories"]
        ]

        self.assertIn("Electronics", categories)


if __name__ == "__main__":
    unittest.main()