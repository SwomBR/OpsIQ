"""Response shapes for the OpsIQ API.

Each class describes the JSON that an endpoint returns. FastAPI uses
them to check responses, to leave out any field not listed here, and
to document the responses at /docs.
"""

from datetime import datetime

from pydantic import BaseModel


class BusinessSummary(BaseModel):
    total_orders: int
    delivered_orders: int
    # None when there are no orders to calculate a percentage from.
    delivered_percentage: float | None
    late_delivered_orders: int


class OrdersByStatus(BaseModel):
    total_orders: int
    orders_by_status: dict[str, int]


class DeliveryPerformance(BaseModel):
    delivered_orders_analyzed: int
    on_time_orders: int
    late_orders: int
    skipped_orders: int
    # These four are None when no delivered orders have valid dates.
    on_time_percentage: float | None
    late_percentage: float | None
    average_delay_days: float | None
    maximum_delay_days: float | None
    delayed_more_than_3_days: int
    delayed_more_than_7_days: int


class DeliveryException(BaseModel):
    order_id: str
    estimated_delivery: str
    actual_delivery: str
    days_late: float


class DeliveryExceptions(BaseModel):
    total_exceptions: int
    limit: int
    exceptions: list[DeliveryException]


class DatasetInfo(BaseModel):
    # The earliest and latest order purchase timestamps in the data.
    first_purchase_date: str | None
    last_purchase_date: str | None
    # When the server calculated the order metrics (UTC).
    calculated_at: datetime


class Sales(BaseModel):
    # Sum of item prices. Freight is reported separately.
    total_product_revenue: float
    total_freight_value: float
    orders_with_items: int
    # None when there are no orders with items.
    average_product_value_per_order: float | None
    payment_totals_by_method: dict[str, float]


class CategoryPerformance(BaseModel):
    category: str
    revenue: float
    quantity_sold: int


class ProductPerformance(BaseModel):
    product_id: str
    quantity_sold: int
    revenue: float


class Products(BaseModel):
    total_products: int
    products_missing_category: int
    # The 10 categories with the highest revenue, highest first.
    top_categories: list[CategoryPerformance]
    # The 10 products with the most items sold, most first.
    top_products: list[ProductPerformance]


class Customers(BaseModel):
    total_unique_customers: int
    repeat_customers: int
    # None when there are no customers.
    repeat_customer_percentage: float | None
    # Unique customers in each state, largest first.
    customers_by_state: dict[str, int]
