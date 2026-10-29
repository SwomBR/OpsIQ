# OpsIQ API Reference

The OpsIQ backend is a read-only REST API built with **FastAPI 0.162.0** (Pydantic 2.14.1, Starlette 1.10.0), served by **Uvicorn 0.54.0**. Versions are from `backend/requirements.txt` and the installed packages on 29 October 2026.

- **Base URL (local):** `http://127.0.0.1:8000`
- **All paths start with** `/api/v1`
- **Interactive documentation:** http://127.0.0.1:8000/docs (checked: HTTP 200). FastAPI also creates `/redoc` and `/openapi.json` by default (not separately checked).
- **Method:** every endpoint is `GET`. Other methods return 405.
- **Format:** JSON. Percentages and days are rounded to 2 decimals. Money is Brazilian reais (BRL) as plain numbers.
- **Authentication:** none (see [Security](#7-security)).

Code: [backend/app/api/routes.py](../backend/app/api/routes.py), [backend/app/api/analytics.py](../backend/app/api/analytics.py), [backend/app/services/analytics_service.py](../backend/app/services/analytics_service.py), [backend/app/schemas.py](../backend/app/schemas.py).

---

## 1. Endpoint summary and verification status

"Manual" means a real request was sent to a running server **during the 29 Oct 2026 audit**, with the full dataset.

| # | Endpoint | Purpose | In code | Automated tests | Manual (29 Oct) | Real data |
|---|---|---|---|---|---|---|
| 1 | `GET /api/v1/` | Welcome message | ✅ routes.py | ✅ test_api.py | ✅ 200 | n/a |
| 2 | `GET /api/v1/health` | Liveness check | ✅ routes.py | ✅ test_api.py | ✅ 200 | n/a (never reads data) |
| 3 | `GET /api/v1/analytics/summary` | Headline order metrics | ✅ | ✅ test_analytics_api.py | ✅ 200 | ✅ matches CLI |
| 4 | `GET /api/v1/analytics/orders-by-status` | Orders per status | ✅ | ✅ test_analytics_api.py | ✅ 200 | ✅ matches SQL |
| 5 | `GET /api/v1/analytics/delivery-performance` | On-time vs late, delays | ✅ | ✅ test_analytics_api.py | ✅ 200 | ✅ matches CLI and SQL |
| 6 | `GET /api/v1/analytics/delivery-exceptions` | Most delayed orders | ✅ | ✅ test_analytics_api.py | ✅ 200, 422 | ✅ matches CLI and SQL |
| 7 | `GET /api/v1/analytics/dataset-info` | Data period + calculation time | ✅ | ✅ test_reports_api.py | ✅ 200 | ✅ |
| 8 | `GET /api/v1/analytics/sales` | Revenue, freight, payments | ✅ | ✅ test_reports_api.py | ✅ 200 | ✅ matches CLI |
| 9 | `GET /api/v1/analytics/products` | Catalog and top sellers | ✅ | ✅ test_reports_api.py | ✅ 200 | ✅ matches CLI and SQL (top categories) |
| 10 | `GET /api/v1/analytics/customers` | Unique/repeat customers, states | ✅ | ✅ test_reports_api.py | ✅ 200 | ✅ matches CLI and SQL |

---

## 2. Endpoints in detail

### 2.1 `GET /api/v1/`

Returns `{"message": "Welcome to the OpsIQ API.", "docs": "/docs"}`.

### 2.2 `GET /api/v1/health`

Returns `{"app": "OpsIQ", "status": "healthy"}`. It **does not read the dataset**, so it answers 200 even when the CSV files are missing. Used as the Render health check (`render.yaml`).

### 2.3 `GET /api/v1/analytics/summary`

| Field | Type | Meaning |
|---|---|---|
| `total_orders` | int | Rows in the orders file |
| `delivered_orders` | int | Orders with status `delivered` |
| `delivered_percentage` | float or null | delivered ÷ total × 100; `null` if there are no orders |
| `late_delivered_orders` | int | Delivered orders that arrived after the estimated date and time |

Data: orders file → `count_orders_by_status`, `find_delivery_exceptions`.
Real result: `{"total_orders":99441,"delivered_orders":96478,"delivered_percentage":97.02,"late_delivered_orders":7826}`

### 2.4 `GET /api/v1/analytics/orders-by-status`

| Field | Type | Meaning |
|---|---|---|
| `total_orders` | int | All orders |
| `orders_by_status` | object {status: int} | Count per status, sorted by status name |

Data: `count_orders_by_status`.
Real result: approved 2, canceled 625, created 5, delivered 96,478, invoiced 314, processing 301, shipped 1,107, unavailable 609.

### 2.5 `GET /api/v1/analytics/delivery-performance`

| Field | Type | Meaning |
|---|---|---|
| `delivered_orders_analyzed` | int | Delivered orders with two valid dates |
| `on_time_orders` | int | Delivered on or before the estimated date and time |
| `late_orders` | int | Delivered after it |
| `skipped_orders` | int | Delivered orders with a missing or unreadable date |
| `on_time_percentage` | float or null | on_time ÷ analysed × 100 |
| `late_percentage` | float or null | late ÷ analysed × 100 |
| `average_delay_days` | float or null | Mean delay of late orders (0.0 if none are late) |
| `maximum_delay_days` | float or null | Largest delay (0.0 if none are late) |
| `delayed_more_than_3_days` | int | Late by more than 3 days |
| `delayed_more_than_7_days` | int | Late by more than 7 days |

The four nullable fields are `null` when no delivered orders have valid dates.
Data: `calculate_delivery_performance`.
Real result: 96,470 analysed, 88,644 on time (91.89%), 7,826 late (8.11%), 8 skipped, average 9.55 days, maximum 188.98 days, 5,164 over 3 days, 3,345 over 7 days.

### 2.6 `GET /api/v1/analytics/delivery-exceptions?limit=10`

| Parameter | Type | Default | Allowed |
|---|---|---|---|
| `limit` | int (query) | 10 | 1–100. Anything else → 422 |

| Field | Type | Meaning |
|---|---|---|
| `total_exceptions` | int | All late-delivered orders |
| `limit` | int | The limit used |
| `exceptions` | list | The `limit` most delayed orders, longest first |
| `exceptions[].order_id` | string | Order ID (no customer data) |
| `exceptions[].estimated_delivery` | string | `YYYY-MM-DD HH:MM:SS` |
| `exceptions[].actual_delivery` | string | `YYYY-MM-DD HH:MM:SS` |
| `exceptions[].days_late` | float | Delay in days, 2 decimals |

Data: `find_delivery_exceptions`.
Real result (limit=2): total 7,826; first `1b3190b2dfa9d789e1f14c05b647a14a`, 188.98 days late.
Checked on 29 Oct 2026: `limit=0`, `limit=101`, `limit=abc` → 422 (with data present).

### 2.7 `GET /api/v1/analytics/dataset-info`

| Field | Type | Meaning |
|---|---|---|
| `first_purchase_date` | string or null | Earliest valid `order_purchase_timestamp` |
| `last_purchase_date` | string or null | Latest valid `order_purchase_timestamp` |
| `calculated_at` | datetime (ISO 8601, UTC) | When the server calculated the order metrics |

Data: `parse_order_date` (from `data_validator`).
Real result: 2016-09-04 21:15:19 → 2018-10-17 17:30:18.

### 2.8 `GET /api/v1/analytics/sales`

| Field | Type | Meaning |
|---|---|---|
| `total_product_revenue` | float | Sum of item `price` (freight excluded) |
| `total_freight_value` | float | Sum of item `freight_value` |
| `orders_with_items` | int | Distinct `order_id`s in the items file |
| `average_product_value_per_order` | float or null | revenue ÷ orders_with_items; `null` when 0 |
| `payment_totals_by_method` | object {method: float} | Sum of `payment_value` per `payment_type` |

Data: items and payments files → `analyze_sales`.
Real result: revenue 13,591,643.70; freight 2,251,909.54; 98,666 orders with items; average 137.75; credit_card 12,542,084.19, boleto 2,869,361.27, voucher 379,436.87, debit_card 217,989.79, not_defined 0.00.

### 2.9 `GET /api/v1/analytics/products`

| Field | Type | Meaning |
|---|---|---|
| `total_products` | int | Rows in the products file |
| `products_missing_category` | int | Products with an empty category |
| `top_categories` | list (max 10) | `{category, revenue, quantity_sold}`, highest revenue first. English names when a translation exists |
| `top_products` | list (max 10) | `{product_id, quantity_sold, revenue}`, most items first |

Data: items, products, translation files → `analyze_products`.
Real result: 32,951 products, 610 missing a category; top category `health_beauty` (1,258,681.34; 9,670 items).

### 2.10 `GET /api/v1/analytics/customers`

| Field | Type | Meaning |
|---|---|---|
| `total_unique_customers` | int | Distinct `customer_unique_id` with at least one order |
| `repeat_customers` | int | People with more than one order |
| `repeat_customer_percentage` | float or null | repeat ÷ unique × 100 |
| `customers_by_state` | object {state: int} | Unique people per state, largest first |

The Version 1 report also calculates "top customers by spending". The API **leaves it out on purpose**, and the `Customers` schema has no field for it.
Data: orders, customers, items files → `analyze_customers`.
Real result: 96,096 unique, 2,997 repeat (3.12%), SP 40,302. The state counts add up to 96,136 (40 more than the unique total), because some people ordered from more than one state and are counted in each.

---

## 3. Errors

| Situation | Status | Body |
|---|---|---|
| A required CSV file is missing | 503 | `{"detail": "The order dataset is not available (olist_orders_dataset.csv is missing). Add the Olist CSV files to the data folder and restart the server."}` |
| A file cannot be read or has a bad value | 500 | `{"detail": "The sales dataset could not be loaded."}` (details only in the server log) |
| Invalid `limit` | 422 | FastAPI's validation message |
| Unknown path | 404 | `{"detail": "Not Found"}` |
| Wrong method (for example `POST`) | 405 | `{"detail": "Method Not Allowed"}` |
| Any other error | 500 | `{"detail": "An unexpected server error occurred."}` |

All of these were seen live on 29 Oct 2026, except the 500 cases, which are covered only by automated tests.

**Known quirk:** when the data is missing, an invalid `limit` returns 503 instead of 422, because the data check runs before the parameter check. This is harmless, but worth knowing.

---

## 4. Caching and performance

- Results are calculated once per server process and kept in memory (`lru_cache`). See [ARCHITECTURE.md §5](ARCHITECTURE.md#5-caching-strategy).
- With `OPSIQ_PRELOAD_DATA=true` (default), a background thread calculates everything at startup. Measured 29 Oct 2026: about 11 seconds.
- Measured response times after warm-up: ~5 ms.
- **New CSV files are not picked up until the server restarts.**

## 5. CORS

- Allowed origins come from `OPSIQ_CORS_ORIGINS` (default `http://localhost:5173,http://127.0.0.1:5173`).
- Only `GET`; headers `Accept`, `Content-Type`; no credentials.
- Checked 29 Oct 2026: `Origin: http://localhost:5173` receives `access-control-allow-origin`, while `Origin: https://evil.example` receives no CORS header.

## 6. Configuration

| Variable | Default | Purpose |
|---|---|---|
| `OPSIQ_ENV` | `development` | Name shown in the startup log |
| `OPSIQ_DATA_DIR` | `data/raw` | CSV folder; relative paths start at the project root |
| `OPSIQ_CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated allowed origins (trailing `/` is removed) |
| `OPSIQ_LOG_LEVEL` | `INFO` | Log level for OpsIQ's own messages |
| `OPSIQ_PRELOAD_DATA` | `true` | Warm the cache at startup (`1/true/yes/on` = on) |

None of these are secrets. There is no `.env` loading in the backend: set them in the shell (`$env:NAME = "value"`) or in the hosting platform.

## 7. Security

- Read-only, no authentication. This is acceptable for public, anonymised, aggregate data; authentication would be required before adding private data.
- Responses never include folder paths, stack traces, customer IDs, cities, or per-customer spending.
- Only order IDs appear in `delivery-exceptions`.
- No rate limiting (not implemented).

## 8. Running the API

From the `backend` folder, with the virtual environment active:

```powershell
uvicorn app.main:app --reload
```

Full setup on a new PC: [SETUP_AND_MIGRATION.md](SETUP_AND_MIGRATION.md).

## 9. Tests

`backend/tests/` has 61 tests (all passing on 29 Oct 2026). Details: [TESTING_GUIDE.md](TESTING_GUIDE.md#2-backend-api-tests-backendtests-61).
