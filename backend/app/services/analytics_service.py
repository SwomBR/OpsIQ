"""Business analytics service for the OpsIQ API.

This module is the bridge between the API and the Version 1 analytics
code in the project's src/ folder. It:
    1. Loads the CSV data.
    2. Calls the existing analytics functions.
    3. Remembers (caches) the calculated results.
    4. Returns plain dictionaries that the API can send as JSON.

It knows nothing about HTTP. Turning errors into HTTP responses is the
job of the route functions in app/api/analytics.py.

Caching
-------
Calculating delivery metrics for ~100,000 orders takes a few seconds,
and the CSV files do not change while the server runs. So each result
is calculated on the first request that needs it and then reused.

    * Only the calculated results are kept, not the raw CSV rows,
      so the server uses far less memory.
    * If loading fails (for example, a file is missing), nothing is
      cached, so the next request tries again.
    * A lock makes requests that arrive together wait for one
      calculation instead of each repeating it.
    * To pick up new CSV files, restart the server (or call
      clear_cache(), which the tests do).
"""

import logging
import sys
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache

from app.config import PROJECT_ROOT, settings

# The Version 1 analytics live in src/ at the project root. Adding the
# project root to Python's import path lets us write `from src...` here
# without hard-coding any computer's location.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.customer_analyzer import analyze_customers  # noqa: E402
from src.data_analyzer import count_orders_by_status  # noqa: E402
from src.data_loader import open_order  # noqa: E402
from src.data_validator import parse_order_date  # noqa: E402
from src.delivery_analyzer import calculate_delivery_performance  # noqa: E402
from src.delivery_exceptions import find_delivery_exceptions  # noqa: E402
from src.product_analyzer import analyze_products  # noqa: E402
from src.sales_analyzer import analyze_sales, load_csv  # noqa: E402

DATA_DIR = settings.data_dir

ORDERS_FILE = DATA_DIR / "olist_orders_dataset.csv"
ORDER_ITEMS_FILENAME = "olist_order_items_dataset.csv"
PAYMENTS_FILENAME = "olist_order_payments_dataset.csv"
PRODUCTS_FILENAME = "olist_products_dataset.csv"
CUSTOMERS_FILENAME = "olist_customers_dataset.csv"
TRANSLATIONS_FILENAME = "product_category_name_translation.csv"

logger = logging.getLogger(__name__)

# Only one thread may calculate (or read) a cached result at a time.
_cache_lock = threading.Lock()


@dataclass(frozen=True)
class OrderMetrics:
    """Every order-level result, calculated once from the orders file."""

    total_orders: int
    status_counts: dict[str, int]
    delivery_performance: dict
    # All late-delivered orders, longest delay first.
    delivery_exceptions: list[dict]
    first_purchase_date: str | None
    last_purchase_date: str | None
    # When these results were calculated (UTC), shown on the dashboard.
    calculated_at: datetime


def _purchase_date_range(orders):
    """Return the earliest and latest valid purchase timestamps."""

    purchase_dates = [
        parsed
        for parsed in (
            parse_order_date(order.get("order_purchase_timestamp"))
            for order in orders
        )
        if parsed is not None
    ]

    if not purchase_dates:
        return None, None

    return (
        min(purchase_dates).isoformat(sep=" "),
        max(purchase_dates).isoformat(sep=" "),
    )


def calculate_order_metrics(orders):
    """Run the Version 1 order analytics once and collect the results."""

    first_purchase, last_purchase = _purchase_date_range(orders)

    return OrderMetrics(
        total_orders=len(orders),
        status_counts=count_orders_by_status(orders),
        delivery_performance=calculate_delivery_performance(orders),
        delivery_exceptions=find_delivery_exceptions(orders),
        first_purchase_date=first_purchase,
        last_purchase_date=last_purchase,
        calculated_at=datetime.now(timezone.utc),
    )


# --- Loading (cached) --------------------------------------------------


def load_orders(file_path=None):
    """Return the order records from the orders CSV file.

    Raises:
        FileNotFoundError: If the orders CSV file does not exist.
    """

    return open_order(file_path or ORDERS_FILE)


def load_order_metrics():
    """Return the order metrics, calculating them on the first call."""

    with _cache_lock:
        return _order_metrics_for(ORDERS_FILE)


@lru_cache(maxsize=1)
def _order_metrics_for(orders_file):
    """Calculate and remember the order metrics for one orders file.

    lru_cache stores the returned result, keyed by orders_file. Errors
    are not stored, so a missing file is checked again next time. The
    raw order rows are not kept once the metrics are calculated.
    """

    return calculate_order_metrics(load_orders(orders_file))


def load_sales_report():
    """Return the Version 1 sales report, calculating it once."""

    with _cache_lock:
        return _sales_report_for(DATA_DIR)


@lru_cache(maxsize=1)
def _sales_report_for(data_dir):
    return analyze_sales(
        load_csv(data_dir / ORDER_ITEMS_FILENAME),
        load_csv(data_dir / PAYMENTS_FILENAME),
    )


def load_product_report():
    """Return the Version 1 product report, calculating it once."""

    with _cache_lock:
        return _product_report_for(DATA_DIR)


@lru_cache(maxsize=1)
def _product_report_for(data_dir):
    translations = load_csv(data_dir / TRANSLATIONS_FILENAME)

    category_translations = {
        row["product_category_name"]: row["product_category_name_english"]
        for row in translations
    }

    return analyze_products(
        load_csv(data_dir / ORDER_ITEMS_FILENAME),
        load_csv(data_dir / PRODUCTS_FILENAME),
        category_translations,
    )


def load_customer_report():
    """Return the Version 1 customer report, calculating it once."""

    with _cache_lock:
        return _customer_report_for(ORDERS_FILE, DATA_DIR)


@lru_cache(maxsize=1)
def _customer_report_for(orders_file, data_dir):
    return analyze_customers(
        load_orders(orders_file),
        load_csv(data_dir / CUSTOMERS_FILENAME),
        load_csv(data_dir / ORDER_ITEMS_FILENAME),
    )


def clear_cache():
    """Forget every cached result, so the next request reloads the data."""

    with _cache_lock:
        _order_metrics_for.cache_clear()
        _sales_report_for.cache_clear()
        _product_report_for.cache_clear()
        _customer_report_for.cache_clear()


def warm_cache():
    """Calculate every result in advance, so the first visitor to the
    dashboard does not wait. Errors are logged, not raised: the API still
    starts, and the endpoints report the problem when they are called.
    """

    for loader in (
        load_order_metrics,
        load_sales_report,
        load_product_report,
        load_customer_report,
    ):
        try:
            loader()
        except Exception as error:
            logger.warning(
                "Could not preload %s: %s",
                loader.__name__,
                type(error).__name__,
            )

    logger.info("Analytics cache warm-up finished.")


# --- Response builders -------------------------------------------------


def _round_or_none(value):
    """Round a number to 2 decimal places, keeping None as None."""

    if value is None:
        return None

    return round(value, 2)


def _percentage_or_none(part, whole):
    """Return part as a percentage of whole, or None when whole is 0."""

    if whole == 0:
        return None

    return _round_or_none(part / whole * 100)


def get_business_summary(metrics):
    """Return the headline order metrics from the business report."""

    delivered_orders = metrics.status_counts.get("delivered", 0)

    return {
        "total_orders": metrics.total_orders,
        "delivered_orders": delivered_orders,
        # A percentage of zero orders has no meaning, so it is None.
        "delivered_percentage": _percentage_or_none(
            delivered_orders, metrics.total_orders
        ),
        "late_delivered_orders": len(metrics.delivery_exceptions),
    }


def get_orders_by_status(metrics):
    """Return the number of orders in each status, sorted by status."""

    return {
        "total_orders": metrics.total_orders,
        "orders_by_status": dict(sorted(metrics.status_counts.items())),
    }


def get_delivery_performance(metrics):
    """Return delivery timeliness and delay metrics."""

    # Copy, so rounding never changes the cached result.
    performance = dict(metrics.delivery_performance)

    for key in (
        "on_time_percentage",
        "late_percentage",
        "average_delay_days",
        "maximum_delay_days",
    ):
        performance[key] = _round_or_none(performance[key])

    return performance


def get_delivery_exceptions(metrics, limit):
    """Return the most delayed orders, longest delay first.

    Args:
        metrics: The order metrics.
        limit: The maximum number of exceptions to include.
    """

    return {
        "total_exceptions": len(metrics.delivery_exceptions),
        "limit": limit,
        "exceptions": metrics.delivery_exceptions[:limit],
    }


def get_dataset_info(metrics):
    """Return the period the orders cover and when they were analysed."""

    return {
        "first_purchase_date": metrics.first_purchase_date,
        "last_purchase_date": metrics.last_purchase_date,
        "calculated_at": metrics.calculated_at,
    }


def get_sales(report):
    """Return the sales metrics from the Version 1 sales report."""

    orders_with_items = report["total_orders"]

    return {
        "total_product_revenue": report["total_product_revenue"],
        "total_freight_value": report["total_freight_charges"],
        "orders_with_items": orders_with_items,
        # Version 1 reports 0 for no orders; the API uses None instead,
        # like every other average or percentage it returns.
        "average_product_value_per_order": (
            report["average_order_value"] if orders_with_items else None
        ),
        "payment_totals_by_method": report["payment_method_totals"],
    }


def get_products(report):
    """Return catalog size and the best-selling categories and products."""

    return {
        "total_products": report["total_products"],
        "products_missing_category": report["products_missing_category"],
        "top_categories": report["top_categories"],
        "top_products": report["top_products"],
    }


def get_customers(report):
    """Return aggregate customer metrics.

    The Version 1 report also lists the top individual customers by
    spending. That list is left out on purpose: the API only shares
    totals, never data about one customer.
    """

    total_customers = report["total_unique_customers"]

    return {
        "total_unique_customers": total_customers,
        "repeat_customers": report["repeat_customers"],
        "repeat_customer_percentage": _percentage_or_none(
            report["repeat_customers"], total_customers
        ),
        "customers_by_state": dict(
            sorted(
                report["customers_by_state"].items(),
                key=lambda item: (-item[1], item[0]),
            )
        ),
    }
