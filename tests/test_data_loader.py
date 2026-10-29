"""
OpsIQ - Business Operations Intelligence Platform

Module: test_data_loader.py

Purpose:
    Test that order data is loaded from the correct location.

Tests included:
    1. The default dataset path is inside the project folder.
    2. Order records are read from a CSV file as dictionaries.
"""

import tempfile
import unittest
from pathlib import Path

from src.data_loader import ORDERS_FILE, PROJECT_ROOT, open_order


class TestDataLoader(unittest.TestCase):
    """Test order data loading."""

    def test_default_path_is_inside_project(self):
        """Check that the dataset path does not depend on one computer."""

        expected = (
            Path(__file__).resolve().parent.parent
            / "data" / "raw" / "olist_orders_dataset.csv"
        )

        self.assertEqual(ORDERS_FILE, expected)
        self.assertEqual(ORDERS_FILE.parents[2], PROJECT_ROOT)

    def test_loads_records_from_csv(self):
        """Check that each CSV row becomes one dictionary."""

        with tempfile.TemporaryDirectory() as folder:
            file_path = Path(folder) / "orders.csv"
            file_path.write_text(
                "order_id,order_status\n"
                "ORD001,delivered\n"
                "ORD002,shipped\n",
                encoding="utf-8",
            )

            orders = open_order(file_path)

        self.assertEqual(len(orders), 2)
        self.assertEqual(
            orders[0],
            {"order_id": "ORD001", "order_status": "delivered"},
        )


if __name__ == "__main__":
    unittest.main()
