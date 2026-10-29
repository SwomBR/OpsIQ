"""
Automated tests for the OpsIQ data validator.

Tests cover missing values, duplicate IDs, invalid statuses,
invalid dates, inconsistent timestamps, and missing delivery dates.
"""

import unittest
from datetime import datetime
from io import StringIO
from unittest.mock import patch

from src.data_validator import (
    check_missing_values,
    check_missing_order_ids,
    check_duplicate_order_ids,
    check_invalid_order_statuses,
    parse_order_date,
    check_invalid_date_formats,
    check_inconsistent_dates,
    check_delivered_orders_missing_delivery_dates,
    validate_orders,
)


class TestDataValidator(unittest.TestCase):

    def setUp(self):
        """Create sample orders for testing."""

        self.orders = [
            {
                "order_id": "ORD001",
                "order_status": "delivered",
                "order_purchase_timestamp": "2024-01-01 10:00:00",
                "order_approved_at": "2024-01-01 10:05:00",
                "order_delivered_carrier_date": "2024-01-02 10:00:00",
                "order_delivered_customer_date": "2024-01-05 12:00:00",
                "order_estimated_delivery_date": "2024-01-06 00:00:00",
            },
            {
                "order_id": "ORD002",
                "order_status": "shipped",
                "order_purchase_timestamp": "2024-01-02 10:00:00",
                "order_approved_at": "2024-01-02 10:05:00",
                "order_delivered_carrier_date": "2024-01-02 12:00:00",
                "order_delivered_customer_date": "",
                "order_estimated_delivery_date": "2024-01-10 00:00:00",
            },
        ]

    def test_missing_values(self):
        """Check that empty values are counted."""

        result = check_missing_values(self.orders)

        self.assertEqual(
            result["order_delivered_customer_date"], 1
        )

    def test_missing_order_ids(self):
        """Check that records without IDs are counted."""

        orders = [
            {"order_id": "ORD001"},
            {"order_id": ""},
            {"order_id": None},
        ]

        self.assertEqual(check_missing_order_ids(orders), 2)

    def test_duplicate_order_ids(self):
        """Check that repeated non-empty IDs are detected."""

        orders = [
            {"order_id": "ORD001"},
            {"order_id": "ORD002"},
            {"order_id": "ORD001"},
            {"order_id": ""},
        ]

        self.assertEqual(check_duplicate_order_ids(orders), 1)

    def test_invalid_order_status(self):
        """Check that unexpected statuses are identified."""

        orders = [
            {"order_id": "ORD001", "order_status": "delivered"},
            {"order_id": "ORD002", "order_status": "unknown_status"},
        ]

        result = check_invalid_order_statuses(orders)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["order_id"], "ORD002")

    def test_valid_date_parsing(self):
        """Check that a valid timestamp is parsed correctly."""

        result = parse_order_date("2024-01-01 10:00:00")

        self.assertEqual(
            result, datetime(2024, 1, 1, 10, 0, 0)
        )

    def test_invalid_date_parsing(self):
        """Check that an invalid timestamp returns None."""

        self.assertIsNone(parse_order_date("not-a-date"))

    def test_invalid_date_format(self):
        """Check that invalid date values are identified."""

        orders = [
            {
                "order_id": "ORD001",
                "order_purchase_timestamp": "invalid-date",
            }
        ]

        result = check_invalid_date_formats(orders)

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0]["column"], "order_purchase_timestamp"
        )

    def test_inconsistent_timestamps(self):
        """Check that timestamps occurring out of sequence are detected."""

        orders = [
            {
                "order_id": "ORD001",
                "order_purchase_timestamp": "2024-01-01 10:00:00",
                "order_approved_at": "2024-01-03 10:00:00",
                "order_delivered_carrier_date": "2024-01-02 10:00:00",
                "order_delivered_customer_date": "2024-01-05 10:00:00",
            }
        ]

        result = check_inconsistent_dates(orders)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["order_id"], "ORD001")
        self.assertEqual(
            result[0]["previous_column"], "order_approved_at"
        )
        self.assertEqual(
            result[0]["current_column"],
            "order_delivered_carrier_date",
        )

    def test_consistent_timestamps(self):
        """Check that correctly ordered timestamps are accepted."""

        result = check_inconsistent_dates([self.orders[0]])

        self.assertEqual(result, [])

    def test_delivered_order_missing_delivery_date(self):
        """Check that delivered orders with missing dates are identified."""

        orders = [
            {
                "order_id": "ORD001",
                "order_status": "delivered",
                "order_delivered_customer_date": "",
            },
            {
                "order_id": "ORD002",
                "order_status": "shipped",
                "order_delivered_customer_date": "",
            },
        ]

        result = check_delivered_orders_missing_delivery_dates(orders)

        self.assertEqual(result, ["ORD001"])

    def test_empty_dataset(self):
        """Check that validation functions handle empty data safely."""

        self.assertEqual(check_missing_values([]), {})
        self.assertEqual(check_missing_order_ids([]), 0)
        self.assertEqual(check_duplicate_order_ids([]), 0)
        self.assertEqual(check_invalid_order_statuses([]), [])
        self.assertEqual(check_invalid_date_formats([]), [])
        self.assertEqual(check_inconsistent_dates([]), [])
        self.assertEqual(
            check_delivered_orders_missing_delivery_dates([]), []
        )

    def test_whitespace_only_values_are_missing(self):
        """Check that values containing only spaces count as missing."""

        orders = [
            {"order_id": "   ", "order_status": "delivered"},
            {"order_id": "ORD001", "order_status": " "},
            {"order_id": "   ", "order_status": "shipped"},
        ]

        self.assertEqual(check_missing_values(orders)["order_id"], 2)
        self.assertEqual(check_missing_values(orders)["order_status"], 1)
        self.assertEqual(check_missing_order_ids(orders), 2)
        self.assertEqual(check_duplicate_order_ids(orders), 0)

    def test_status_with_spaces_and_mixed_case_is_valid(self):
        """Check that status matching ignores case and extra spaces."""

        orders = [
            {"order_id": "ORD001", "order_status": " Delivered "},
            {"order_id": "ORD002", "order_status": "SHIPPED"},
        ]

        self.assertEqual(check_invalid_order_statuses(orders), [])

    def test_non_text_status_is_reported(self):
        """Check that a non-text status is reported instead of crashing."""

        orders = [{"order_id": "ORD001", "order_status": 5}]

        result = check_invalid_order_statuses(orders)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["order_id"], "ORD001")

    def test_delivered_status_variations_missing_date(self):
        """Check delivered-status variations with a blank delivery date."""

        orders = [
            {
                "order_id": "ORD001",
                "order_status": " Delivered ",
                "order_delivered_customer_date": "   ",
            },
        ]

        result = check_delivered_orders_missing_delivery_dates(orders)

        self.assertEqual(result, ["ORD001"])

    def test_missing_intermediate_date_is_skipped(self):
        """Check that missing middle dates do not hide later problems."""

        orders = [
            {
                "order_id": "ORD001",
                "order_purchase_timestamp": "2024-01-05 10:00:00",
                "order_approved_at": "",
                "order_delivered_carrier_date": "2024-01-03 10:00:00",
            },
            {
                "order_id": "ORD002",
                "order_purchase_timestamp": "2024-01-01 10:00:00",
                "order_approved_at": "",
                "order_delivered_carrier_date": "2024-01-03 10:00:00",
            },
        ]

        result = check_inconsistent_dates(orders)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["order_id"], "ORD001")
        self.assertEqual(
            result[0]["previous_column"], "order_purchase_timestamp"
        )
        self.assertEqual(
            result[0]["current_column"], "order_delivered_carrier_date"
        )

    def test_unreadable_date_is_reported_once(self):
        """Check that an unreadable date is a format issue only."""

        orders = [
            {
                "order_id": "ORD001",
                "order_purchase_timestamp": "2024-01-05 10:00:00",
                "order_approved_at": "05/01/2024",
                "order_delivered_carrier_date": "2024-01-03 10:00:00",
            }
        ]

        self.assertEqual(len(check_invalid_date_formats(orders)), 1)
        self.assertEqual(check_inconsistent_dates(orders), [])

    def test_missing_fields_do_not_crash(self):
        """Check that records without the expected columns are handled."""

        orders = [{"order_id": "ORD001"}, {"order_id": "ORD002"}]

        self.assertEqual(check_invalid_order_statuses(orders), [])
        self.assertEqual(check_invalid_date_formats(orders), [])
        self.assertEqual(check_inconsistent_dates(orders), [])
        self.assertEqual(
            check_delivered_orders_missing_delivery_dates(orders), []
        )

    def test_validate_orders_reports_issues(self):
        """Check the printed summary when problems are found."""

        orders = self.orders + [
            {"order_id": "ORD001", "order_status": "unknown_status"},
        ]

        with patch("sys.stdout", new_callable=StringIO) as output:
            validate_orders(orders)

        report = output.getvalue()

        self.assertIn("Total orders checked: 3", report)
        self.assertIn("Duplicate order ID occurrences: 1", report)
        self.assertIn("Invalid order statuses: 1", report)
        self.assertIn(
            "Potential data-quality issues require investigation.",
            report,
        )

    def test_validate_orders_reports_clean_data(self):
        """Check the printed summary when no problems are found."""

        with patch("sys.stdout", new_callable=StringIO) as output:
            validate_orders([self.orders[0]])

        self.assertIn(
            "No issues detected by the implemented checks.",
            output.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
