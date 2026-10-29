"""Business analytics endpoints for OpsIQ.

Every route here is served under the /api/v1/analytics prefix
(set in app/main.py). The calculations themselves live in
app/services/analytics_service.py.
"""

import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app import schemas
from app.services import analytics_service

# The largest number of delivery exceptions one request may ask for.
MAX_EXCEPTION_LIMIT = 100

logger = logging.getLogger(__name__)

router = APIRouter()


def _load(loader, dataset_name):
    """Call loader(), or stop the request with a clear error.

    The error messages never include folder paths or stack traces;
    the full details are written to the server log instead. Only the
    missing file's name is shared, so the person running the server
    knows which file to add.
    """

    try:
        return loader()
    except FileNotFoundError as error:
        file_name = Path(error.filename or "").name or "a dataset file"
        logger.error("%s dataset file not found: %s", dataset_name, file_name)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"The {dataset_name} dataset is not available "
                f"({file_name} is missing). "
                "Add the Olist CSV files to the data folder and "
                "restart the server."
            ),
        )
    except Exception:
        logger.exception("%s dataset could not be loaded.", dataset_name)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"The {dataset_name} dataset could not be loaded.",
        )


def get_order_metrics():
    """Return the order metrics for the current request.

    Each order endpoint receives them through Depends(get_order_metrics).
    Tests can replace this function to serve sample data instead.
    """

    return _load(analytics_service.load_order_metrics, "order")


def get_sales_report():
    return _load(analytics_service.load_sales_report, "sales")


def get_product_report():
    return _load(analytics_service.load_product_report, "product")


def get_customer_report():
    return _load(analytics_service.load_customer_report, "customer")


OrderMetrics = Annotated[
    analytics_service.OrderMetrics, Depends(get_order_metrics)
]
SalesReport = Annotated[dict, Depends(get_sales_report)]
ProductReport = Annotated[dict, Depends(get_product_report)]
CustomerReport = Annotated[dict, Depends(get_customer_report)]


@router.get("/summary", response_model=schemas.BusinessSummary)
def get_business_summary(metrics: OrderMetrics):
    """Return the headline order metrics from the business report."""
    return analytics_service.get_business_summary(metrics)


@router.get("/orders-by-status", response_model=schemas.OrdersByStatus)
def get_orders_by_status(metrics: OrderMetrics):
    """Return the number of orders in each status."""
    return analytics_service.get_orders_by_status(metrics)


@router.get(
    "/delivery-performance",
    response_model=schemas.DeliveryPerformance,
)
def get_delivery_performance(metrics: OrderMetrics):
    """Return on-time and late delivery counts, percentages, and delays."""
    return analytics_service.get_delivery_performance(metrics)


@router.get(
    "/delivery-exceptions",
    response_model=schemas.DeliveryExceptions,
)
def get_delivery_exceptions(
    metrics: OrderMetrics,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=MAX_EXCEPTION_LIMIT,
            description="How many of the most delayed orders to return.",
        ),
    ] = 10,
):
    """Return late-delivered orders, longest delay first."""
    return analytics_service.get_delivery_exceptions(metrics, limit)


@router.get("/dataset-info", response_model=schemas.DatasetInfo)
def get_dataset_info(metrics: OrderMetrics):
    """Return the period the orders cover and when they were analysed."""
    return analytics_service.get_dataset_info(metrics)


@router.get("/sales", response_model=schemas.Sales)
def get_sales(report: SalesReport):
    """Return product revenue, freight, and payment totals by method."""
    return analytics_service.get_sales(report)


@router.get("/products", response_model=schemas.Products)
def get_products(report: ProductReport):
    """Return catalog size and the best-selling categories and products."""
    return analytics_service.get_products(report)


@router.get("/customers", response_model=schemas.Customers)
def get_customers(report: CustomerReport):
    """Return unique and repeat customer counts and customers by state.

    Only totals are returned, never details about individual customers.
    """
    return analytics_service.get_customers(report)
