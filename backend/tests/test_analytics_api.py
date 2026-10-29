"""Tests for the business analytics endpoints.

Most tests replace the real dataset with the small SAMPLE_ORDERS list
below, so they do not need the Olist CSV files. The expected numbers
are worked out by hand from that list.
"""

import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.analytics import MAX_EXCEPTION_LIMIT, get_order_metrics
from app.main import app
from app.services import analytics_service

# Importing analytics_service above adds the project root to the
# import path, so the Version 1 report can be imported here.
from src.business_report import generate_business_report  # noqa: E402

SUMMARY_URL = "/api/v1/analytics/summary"
STATUS_URL = "/api/v1/analytics/orders-by-status"
PERFORMANCE_URL = "/api/v1/analytics/delivery-performance"
EXCEPTIONS_URL = "/api/v1/analytics/delivery-exceptions"

ANALYTICS_URLS = [SUMMARY_URL, STATUS_URL, PERFORMANCE_URL, EXCEPTIONS_URL]

ORDER_HEADER = (
    "order_id,customer_id,order_status,order_purchase_timestamp,"
    "order_approved_at,order_delivered_carrier_date,"
    "order_delivered_customer_date,order_estimated_delivery_date\n"
)


def make_order(order_id, order_status, delivered="", estimated=""):
    """Build one order record in the same shape as the CSV rows."""
    return {
        "order_id": order_id,
        "customer_id": f"CUSTOMER-{order_id}",
        "order_status": order_status,
        "order_delivered_customer_date": delivered,
        "order_estimated_delivery_date": estimated,
    }


# 6 orders: 4 delivered (1 on time, 2 late, 1 missing its delivery date),
# 1 shipped, and 1 canceled.
SAMPLE_ORDERS = [
    make_order("ON-TIME", "delivered",
               "2026-01-08 10:00:00", "2026-01-10 10:00:00"),
    make_order("LATE-5", "delivered",
               "2026-01-15 10:00:00", "2026-01-10 10:00:00"),
    make_order("LATE-10", "delivered",
               "2026-01-20 10:00:00", "2026-01-10 10:00:00"),
    make_order("NO-DATE", "delivered",
               "", "2026-01-10 10:00:00"),
    make_order("SHIPPED", "shipped",
               "", "2026-01-10 10:00:00"),
    make_order("CANCELED", "canceled"),
]


class AnalyticsTestCase(unittest.TestCase):
    """Base class: serves SAMPLE_ORDERS instead of the real dataset."""

    orders = SAMPLE_ORDERS

    def setUp(self):
        metrics = analytics_service.calculate_order_metrics(self.orders)
        app.dependency_overrides[get_order_metrics] = lambda: metrics
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()


class TestBusinessSummary(AnalyticsTestCase):

    def test_summary_returns_expected_metrics(self):
        response = self.client.get(SUMMARY_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "total_orders": 6,
                "delivered_orders": 4,
                "delivered_percentage": 66.67,
                "late_delivered_orders": 2,
            },
        )

    def test_summary_agrees_with_version_1_business_report(self):
        body = self.client.get(SUMMARY_URL).json()

        output = StringIO()

        with redirect_stdout(output):
            generate_business_report(self.orders)

        report = output.getvalue()

        self.assertIn(f"Total orders: {body['total_orders']:,}", report)
        self.assertIn(
            f"Delivered orders: {body['delivered_orders']:,}", report
        )
        self.assertIn(
            "Delivered order percentage: "
            f"{body['delivered_percentage']:.2f}%",
            report,
        )
        self.assertIn(
            f"Late-delivered orders: {body['late_delivered_orders']:,}",
            report,
        )


class TestOrdersByStatus(AnalyticsTestCase):

    def test_counts_each_status(self):
        response = self.client.get(STATUS_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "total_orders": 6,
                "orders_by_status": {
                    "canceled": 1,
                    "delivered": 4,
                    "shipped": 1,
                },
            },
        )

    def test_status_counts_add_up_to_total(self):
        body = self.client.get(STATUS_URL).json()

        self.assertEqual(
            sum(body["orders_by_status"].values()), body["total_orders"]
        )


class TestDeliveryPerformance(AnalyticsTestCase):

    def test_returns_expected_metrics(self):
        response = self.client.get(PERFORMANCE_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "delivered_orders_analyzed": 3,
                "on_time_orders": 1,
                "late_orders": 2,
                "skipped_orders": 1,
                "on_time_percentage": 33.33,
                "late_percentage": 66.67,
                "average_delay_days": 7.5,
                "maximum_delay_days": 10.0,
                "delayed_more_than_3_days": 2,
                "delayed_more_than_7_days": 1,
            },
        )


class TestDeliveryExceptions(AnalyticsTestCase):

    def test_returns_longest_delay_first(self):
        response = self.client.get(EXCEPTIONS_URL)
        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["total_exceptions"], 2)
        self.assertEqual(
            [exception["order_id"] for exception in body["exceptions"]],
            ["LATE-10", "LATE-5"],
        )

        days_late = [exception["days_late"] for exception in body["exceptions"]]
        self.assertEqual(days_late, sorted(days_late, reverse=True))

    def test_exception_contains_only_order_and_delivery_fields(self):
        exception = self.client.get(EXCEPTIONS_URL).json()["exceptions"][0]

        self.assertEqual(
            exception,
            {
                "order_id": "LATE-10",
                "estimated_delivery": "2026-01-10 10:00:00",
                "actual_delivery": "2026-01-20 10:00:00",
                "days_late": 10.0,
            },
        )

    def test_default_limit_is_10(self):
        body = self.client.get(EXCEPTIONS_URL).json()

        self.assertEqual(body["limit"], 10)

    def test_limit_controls_number_returned(self):
        body = self.client.get(EXCEPTIONS_URL, params={"limit": 1}).json()

        self.assertEqual(body["limit"], 1)
        self.assertEqual(len(body["exceptions"]), 1)
        self.assertEqual(body["exceptions"][0]["order_id"], "LATE-10")
        # The total still counts every late order, not just those returned.
        self.assertEqual(body["total_exceptions"], 2)

    def test_maximum_limit_is_accepted(self):
        response = self.client.get(
            EXCEPTIONS_URL, params={"limit": MAX_EXCEPTION_LIMIT}
        )

        self.assertEqual(response.status_code, 200)

    def test_invalid_limits_return_422(self):
        for limit in [0, -5, MAX_EXCEPTION_LIMIT + 1, "abc", 2.5]:
            with self.subTest(limit=limit):
                response = self.client.get(
                    EXCEPTIONS_URL, params={"limit": limit}
                )

                self.assertEqual(response.status_code, 422)


class TestEmptyDataset(AnalyticsTestCase):

    orders = []

    def test_summary_is_zero(self):
        response = self.client.get(SUMMARY_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "total_orders": 0,
                "delivered_orders": 0,
                "delivered_percentage": None,
                "late_delivered_orders": 0,
            },
        )

    def test_orders_by_status_is_empty(self):
        self.assertEqual(
            self.client.get(STATUS_URL).json(),
            {"total_orders": 0, "orders_by_status": {}},
        )

    def test_delivery_performance_has_no_percentages(self):
        body = self.client.get(PERFORMANCE_URL).json()

        self.assertEqual(body["delivered_orders_analyzed"], 0)
        self.assertIsNone(body["on_time_percentage"])
        self.assertIsNone(body["late_percentage"])
        self.assertIsNone(body["average_delay_days"])
        self.assertIsNone(body["maximum_delay_days"])

    def test_delivery_exceptions_is_empty(self):
        body = self.client.get(EXCEPTIONS_URL).json()

        self.assertEqual(body["total_exceptions"], 0)
        self.assertEqual(body["exceptions"], [])


class TestDataLoading(unittest.TestCase):
    """Tests that use the real loader with temporary files."""

    def setUp(self):
        # Start every test with an empty cache, and leave one behind.
        analytics_service.clear_cache()
        self.addCleanup(analytics_service.clear_cache)
        self.client = TestClient(app)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def use_orders_file(self, file_path):
        """Point the service at file_path for the rest of the test."""
        patcher = patch.object(analytics_service, "ORDERS_FILE", file_path)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_missing_file_returns_503_without_path(self):
        self.use_orders_file(self.temp_path / "missing.csv")

        for url in ANALYTICS_URLS:
            with self.subTest(url=url):
                with self.assertLogs("app.api.analytics", level="ERROR"):
                    response = self.client.get(url)

                self.assertEqual(response.status_code, 503)
                self.assertIn("not available", response.json()["detail"])
                self.assertNotIn(self.temp_dir.name, response.text)

    def test_health_works_when_dataset_is_missing(self):
        self.use_orders_file(self.temp_path / "missing.csv")

        response = self.client.get("/api/v1/health")

        self.assertEqual(response.status_code, 200)

    def test_csv_with_header_only_is_handled(self):
        orders_file = self.temp_path / "orders.csv"
        orders_file.write_text(ORDER_HEADER, encoding="utf-8")
        self.use_orders_file(orders_file)

        response = self.client.get(SUMMARY_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_orders"], 0)

    def test_orders_are_read_from_csv_file(self):
        orders_file = self.temp_path / "orders.csv"
        orders_file.write_text(
            ORDER_HEADER
            + "A1,C1,delivered,,,,2026-01-15 10:00:00,2026-01-10 10:00:00\n"
            + "A2,C2,shipped,,,,,2026-01-10 10:00:00\n",
            encoding="utf-8",
        )
        self.use_orders_file(orders_file)

        body = self.client.get(SUMMARY_URL).json()

        self.assertEqual(body["total_orders"], 2)
        self.assertEqual(body["delivered_orders"], 1)
        self.assertEqual(body["late_delivered_orders"], 1)

    def test_unexpected_loading_error_returns_500_without_details(self):
        error = RuntimeError("secret details from C:\\private\\folder")

        with patch.object(
            analytics_service, "load_orders", side_effect=error
        ):
            with self.assertLogs("app.api.analytics", level="ERROR"):
                response = self.client.get(SUMMARY_URL)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json(),
            {"detail": "The order dataset could not be loaded."},
        )


class TestAnalyticsRoutes(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_unknown_analytics_path_returns_404(self):
        response = self.client.get("/api/v1/analytics/does-not-exist")

        self.assertEqual(response.status_code, 404)

    def test_analytics_endpoints_are_listed_in_docs(self):
        paths = self.client.get("/openapi.json").json()["paths"]

        for url in ANALYTICS_URLS:
            self.assertIn(url, paths)


if __name__ == "__main__":
    unittest.main()
