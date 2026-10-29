"""Tests for the sales, products, customers, and dataset-info endpoints,
and for the cache that sits behind every analytics endpoint.

Each test writes a few small CSV files into a temporary folder and points
the service at that folder, so the real loading code runs without the
Olist dataset. The expected numbers are worked out by hand below.
"""

import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services import analytics_service

from src.business_report import generate_business_report  # noqa: E402

SALES_URL = "/api/v1/analytics/sales"
PRODUCTS_URL = "/api/v1/analytics/products"
CUSTOMERS_URL = "/api/v1/analytics/customers"
DATASET_INFO_URL = "/api/v1/analytics/dataset-info"
SUMMARY_URL = "/api/v1/analytics/summary"
PERFORMANCE_URL = "/api/v1/analytics/delivery-performance"

REPORT_URLS = [SALES_URL, PRODUCTS_URL, CUSTOMERS_URL]

# 3 orders. Customers C1 and C2 are the same person (unique ID U1),
# so U1 is a repeat customer. C3 (U2) has one shipped order.
ORDERS_CSV = (
    "order_id,customer_id,order_status,order_purchase_timestamp,"
    "order_approved_at,order_delivered_carrier_date,"
    "order_delivered_customer_date,order_estimated_delivery_date\n"
    "O1,C1,delivered,2026-01-01 08:00:00,,,"
    "2026-01-05 10:00:00,2026-01-10 00:00:00\n"
    "O2,C2,delivered,2026-01-02 09:00:00,,,"
    "2026-01-15 00:00:00,2026-01-12 00:00:00\n"
    "O3,C3,shipped,2026-02-01 12:30:00,,,,2026-02-10 00:00:00\n"
)

CUSTOMERS_CSV = (
    "customer_id,customer_unique_id,customer_zip_code_prefix,"
    "customer_city,customer_state\n"
    "C1,U1,01000,sao paulo,SP\n"
    "C2,U1,01000,sao paulo,SP\n"
    "C3,U2,20000,rio de janeiro,RJ\n"
)

# Revenue 100 + 50 + 100 = 250. Freight 10 + 5 + 10 = 25.
# 2 orders have items, so the average product value is 125.
ORDER_ITEMS_CSV = (
    "order_id,order_item_id,product_id,seller_id,shipping_limit_date,"
    "price,freight_value\n"
    "O1,1,P1,S1,2026-01-02 00:00:00,100.00,10.00\n"
    "O1,2,P2,S1,2026-01-02 00:00:00,50.00,5.00\n"
    "O2,1,P1,S1,2026-01-03 00:00:00,100.00,10.00\n"
)

PAYMENTS_CSV = (
    "order_id,payment_sequential,payment_type,payment_installments,"
    "payment_value\n"
    "O1,1,credit_card,1,165.00\n"
    "O2,1,boleto,1,110.00\n"
)

# P2 has no category. P3 is in the catalog but was never sold.
PRODUCTS_CSV = (
    "product_id,product_category_name,product_name_lenght,"
    "product_description_lenght,product_photos_qty,product_weight_g,"
    "product_length_cm,product_height_cm,product_width_cm\n"
    "P1,beleza_saude,10,100,1,200,10,10,10\n"
    "P2,,10,100,1,200,10,10,10\n"
    "P3,beleza_saude,10,100,1,200,10,10,10\n"
)

TRANSLATIONS_CSV = (
    "product_category_name,product_category_name_english\n"
    "beleza_saude,health_beauty\n"
)

DATASET_FILES = {
    "olist_orders_dataset.csv": ORDERS_CSV,
    "olist_customers_dataset.csv": CUSTOMERS_CSV,
    "olist_order_items_dataset.csv": ORDER_ITEMS_CSV,
    "olist_order_payments_dataset.csv": PAYMENTS_CSV,
    "olist_products_dataset.csv": PRODUCTS_CSV,
    "product_category_name_translation.csv": TRANSLATIONS_CSV,
}


class DataFolderTestCase(unittest.TestCase):
    """Base class: points the service at a temporary data folder."""

    def setUp(self):
        analytics_service.clear_cache()
        self.addCleanup(analytics_service.clear_cache)

        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.data_dir = Path(temp_dir.name)

        for target, value in [
            ("DATA_DIR", self.data_dir),
            ("ORDERS_FILE", self.data_dir / "olist_orders_dataset.csv"),
        ]:
            patcher = patch.object(analytics_service, target, value)
            patcher.start()
            self.addCleanup(patcher.stop)

        self.client = TestClient(app)

    def write_files(self, files=None):
        """Write the dataset files (all of them by default)."""
        for name, content in (files or DATASET_FILES).items():
            (self.data_dir / name).write_text(content, encoding="utf-8")

    def write_header_only_files(self):
        """Write every dataset file with its header row and no records."""
        self.write_files({
            name: content.splitlines()[0] + "\n"
            for name, content in DATASET_FILES.items()
        })


class TestSalesEndpoint(DataFolderTestCase):

    def test_returns_expected_metrics(self):
        self.write_files()

        response = self.client.get(SALES_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "total_product_revenue": 250.0,
                "total_freight_value": 25.0,
                "orders_with_items": 2,
                "average_product_value_per_order": 125.0,
                "payment_totals_by_method": {
                    "boleto": 110.0,
                    "credit_card": 165.0,
                },
            },
        )

    def test_empty_files_have_no_average(self):
        self.write_header_only_files()

        body = self.client.get(SALES_URL).json()

        self.assertEqual(body["total_product_revenue"], 0)
        self.assertEqual(body["orders_with_items"], 0)
        self.assertIsNone(body["average_product_value_per_order"])
        self.assertEqual(body["payment_totals_by_method"], {})


class TestProductsEndpoint(DataFolderTestCase):

    def test_returns_expected_metrics(self):
        self.write_files()

        response = self.client.get(PRODUCTS_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "total_products": 3,
                "products_missing_category": 1,
                "top_categories": [
                    {
                        "category": "health_beauty",
                        "revenue": 200.0,
                        "quantity_sold": 2,
                    },
                    {
                        "category": "unknown",
                        "revenue": 50.0,
                        "quantity_sold": 1,
                    },
                ],
                "top_products": [
                    {"product_id": "P1", "quantity_sold": 2, "revenue": 200.0},
                    {"product_id": "P2", "quantity_sold": 1, "revenue": 50.0},
                ],
            },
        )

    def test_empty_files_return_zero_and_empty_lists(self):
        self.write_header_only_files()

        body = self.client.get(PRODUCTS_URL).json()

        self.assertEqual(body["total_products"], 0)
        self.assertEqual(body["top_categories"], [])
        self.assertEqual(body["top_products"], [])


class TestCustomersEndpoint(DataFolderTestCase):

    def test_returns_expected_metrics(self):
        self.write_files()

        response = self.client.get(CUSTOMERS_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "total_unique_customers": 2,
                "repeat_customers": 1,
                "repeat_customer_percentage": 50.0,
                "customers_by_state": {"RJ": 1, "SP": 1},
            },
        )

    def test_individual_customers_are_not_exposed(self):
        self.write_files()

        response = self.client.get(CUSTOMERS_URL)

        self.assertNotIn("top_customers", response.json())
        self.assertNotIn("U1", response.text)
        self.assertNotIn("C1", response.text)

    def test_empty_files_have_no_percentage(self):
        self.write_header_only_files()

        body = self.client.get(CUSTOMERS_URL).json()

        self.assertEqual(body["total_unique_customers"], 0)
        self.assertIsNone(body["repeat_customer_percentage"])
        self.assertEqual(body["customers_by_state"], {})


class TestDatasetInfoEndpoint(DataFolderTestCase):

    def test_returns_purchase_date_range(self):
        self.write_files()

        response = self.client.get(DATASET_INFO_URL)
        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["first_purchase_date"], "2026-01-01 08:00:00")
        self.assertEqual(body["last_purchase_date"], "2026-02-01 12:30:00")
        self.assertIn("calculated_at", body)

    def test_empty_orders_have_no_date_range(self):
        self.write_header_only_files()

        body = self.client.get(DATASET_INFO_URL).json()

        self.assertIsNone(body["first_purchase_date"])
        self.assertIsNone(body["last_purchase_date"])


class TestReportErrors(DataFolderTestCase):

    def test_missing_file_returns_503_naming_only_the_file(self):
        files = dict(DATASET_FILES)
        del files["olist_order_items_dataset.csv"]
        self.write_files(files)

        for url in REPORT_URLS:
            with self.subTest(url=url):
                with self.assertLogs("app.api.analytics", level="ERROR"):
                    response = self.client.get(url)

                self.assertEqual(response.status_code, 503)
                self.assertIn(
                    "olist_order_items_dataset.csv is missing",
                    response.json()["detail"],
                )
                self.assertNotIn(str(self.data_dir), response.text)

    def test_unreadable_values_return_500_without_details(self):
        files = dict(DATASET_FILES)
        files["olist_order_items_dataset.csv"] = ORDER_ITEMS_CSV.replace(
            "100.00", "not-a-number"
        )
        self.write_files(files)

        with self.assertLogs("app.api.analytics", level="ERROR"):
            response = self.client.get(SALES_URL)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json(),
            {"detail": "The sales dataset could not be loaded."},
        )

    def test_unexpected_route_error_returns_generic_500(self):
        error = RuntimeError("secret details from C:\\private\\folder")
        client = TestClient(app, raise_server_exceptions=False)
        self.write_files()

        with patch.object(
            analytics_service, "get_business_summary", side_effect=error
        ):
            with self.assertLogs("app.main", level="ERROR"):
                response = client.get(SUMMARY_URL)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json(),
            {"detail": "An unexpected server error occurred."},
        )


class TestCache(DataFolderTestCase):

    def test_orders_file_is_read_once_for_many_requests(self):
        self.write_files()

        with patch.object(
            analytics_service,
            "open_order",
            wraps=analytics_service.open_order,
        ) as open_order:
            for url in [SUMMARY_URL, PERFORMANCE_URL, SUMMARY_URL]:
                self.assertEqual(self.client.get(url).status_code, 200)

        self.assertEqual(open_order.call_count, 1)

    def test_report_files_are_read_once_for_many_requests(self):
        self.write_files()

        with patch.object(
            analytics_service,
            "load_csv",
            wraps=analytics_service.load_csv,
        ) as load_csv:
            self.client.get(SALES_URL)
            self.client.get(SALES_URL)

        # Order items and payments, once each.
        self.assertEqual(load_csv.call_count, 2)

    def test_failed_load_is_not_cached(self):
        files = dict(DATASET_FILES)
        del files["olist_order_payments_dataset.csv"]
        self.write_files(files)

        with self.assertLogs("app.api.analytics", level="ERROR"):
            self.assertEqual(self.client.get(SALES_URL).status_code, 503)

        # Adding the missing file fixes the next request, without a restart.
        self.write_files()

        self.assertEqual(self.client.get(SALES_URL).status_code, 200)

    def test_clear_cache_reloads_changed_data(self):
        self.write_files()
        self.assertEqual(
            self.client.get(SUMMARY_URL).json()["total_orders"], 3
        )

        self.write_files({
            "olist_orders_dataset.csv": ORDERS_CSV.rsplit("O3", 1)[0],
        })

        # Still cached until the cache is cleared.
        self.assertEqual(
            self.client.get(SUMMARY_URL).json()["total_orders"], 3
        )

        analytics_service.clear_cache()

        self.assertEqual(
            self.client.get(SUMMARY_URL).json()["total_orders"], 2
        )

    def test_rounding_does_not_change_cached_metrics(self):
        # 1 of 3 delivered orders late: 33.333...%, which needs rounding.
        metrics = analytics_service.calculate_order_metrics([
            {
                "order_id": order_id,
                "order_status": "delivered",
                "order_delivered_customer_date": delivered,
                "order_estimated_delivery_date": "2026-01-10 00:00:00",
            }
            for order_id, delivered in [
                ("A", "2026-01-09 00:00:00"),
                ("B", "2026-01-09 00:00:00"),
                ("C", "2026-01-11 00:00:00"),
            ]
        ])

        response = analytics_service.get_delivery_performance(metrics)

        self.assertEqual(response["late_percentage"], 33.33)
        # The cached value keeps full precision; only responses round.
        self.assertAlmostEqual(
            metrics.delivery_performance["late_percentage"], 100 / 3
        )

    def test_requests_arriving_together_calculate_once(self):
        self.write_files()
        results = []

        def request_summary():
            results.append(self.client.get(SUMMARY_URL).status_code)

        with patch.object(
            analytics_service,
            "calculate_order_metrics",
            wraps=analytics_service.calculate_order_metrics,
        ) as calculate:
            threads = [
                threading.Thread(target=request_summary) for _ in range(5)
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

        self.assertEqual(results, [200] * 5)
        self.assertEqual(calculate.call_count, 1)

    def test_warm_cache_fills_every_result(self):
        self.write_files()

        analytics_service.warm_cache()

        with patch.object(analytics_service, "load_csv") as load_csv,                 patch.object(analytics_service, "open_order") as open_order:
            for url in [SUMMARY_URL] + REPORT_URLS:
                self.assertEqual(self.client.get(url).status_code, 200)

        load_csv.assert_not_called()
        open_order.assert_not_called()

    def test_warm_cache_logs_missing_files_without_raising(self):
        # The data folder is empty.
        with self.assertLogs("app.services", level="WARNING") as logs:
            analytics_service.warm_cache()

        log_text = "\n".join(logs.output)
        self.assertIn("FileNotFoundError", log_text)
        self.assertNotIn(str(self.data_dir), log_text)


class TestReportsAgreeWithVersion1(DataFolderTestCase):
    """The API and the terminal report must show the same numbers."""

    def get_report_text(self):
        service = analytics_service
        output = StringIO()

        with redirect_stdout(output):
            generate_business_report(
                service.load_orders(),
                service.load_sales_report(),
                service.load_product_report(),
                service.load_customer_report(),
            )

        return output.getvalue()

    def test_sales_products_and_customers_match_report(self):
        self.write_files()
        sales = self.client.get(SALES_URL).json()
        products = self.client.get(PRODUCTS_URL).json()
        customers = self.client.get(CUSTOMERS_URL).json()

        report = self.get_report_text()

        for line in [
            "Total product revenue: "
            f"{sales['total_product_revenue']:,.2f}",
            f"Total freight charges: {sales['total_freight_value']:,.2f}",
            f"Orders with item records: {sales['orders_with_items']:,}",
            "Average product value per order: "
            f"{sales['average_product_value_per_order']:,.2f}",
            f"Products in catalog: {products['total_products']:,}",
            "Products missing category: "
            f"{products['products_missing_category']:,}",
            f"Unique customers: {customers['total_unique_customers']:,}",
            f"Repeat customers: {customers['repeat_customers']:,}",
            "Repeat customer percentage: "
            f"{customers['repeat_customer_percentage']:.2f}%",
        ]:
            with self.subTest(line=line):
                self.assertIn(line, report)


class TestNewRoutesAreDocumented(unittest.TestCase):

    def test_new_endpoints_are_listed_in_docs(self):
        paths = TestClient(app).get("/openapi.json").json()["paths"]

        for url in REPORT_URLS + [DATASET_INFO_URL]:
            self.assertIn(url, paths)


if __name__ == "__main__":
    unittest.main()
