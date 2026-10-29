# OpsIQ Architecture

How OpsIQ is put together: which part does what, how data moves through it, and why it was designed this way. Every diagram here was checked against the code on **29 October 2026** (commit `ac32a9d`).

Related: [Master reference](PROJECT_MASTER_REFERENCE.md) (every module in detail) · [API reference](API_REFERENCE.md) · [Testing guide](TESTING_GUIDE.md) · [Deployment](DEPLOYMENT.md)

## Contents

1. [System architecture](#1-system-architecture)
2. [Data flow: three processing paths](#2-data-flow-three-processing-paths)
3. [Dataset relationships](#3-dataset-relationships)
4. [Backend / API architecture](#4-backend--api-architecture)
5. [Caching strategy](#5-caching-strategy)
6. [Error-handling strategy](#6-error-handling-strategy)
7. [Frontend architecture](#7-frontend-architecture)
8. [Database architecture](#8-database-architecture)
9. [Testing and CI/CD architecture](#9-testing-and-cicd-architecture)
10. [Deployment architecture (planned)](#10-deployment-architecture-planned)

---

## 1. System architecture

```mermaid
flowchart TB
    subgraph Data["Data — data/raw/ (not in Git)"]
        CSV[("Olist CSV files")]
    end

    subgraph Engine["Analytics engine — src/ (Python standard library only)"]
        LOAD["data_loader.open_order<br/>sales_analyzer.load_csv"]
        CALC["data_analyzer · delivery_analyzer<br/>delivery_exceptions · sales_analyzer<br/>product_analyzer · customer_analyzer"]
        VAL["data_validator"]
        REPORT["business_report (CLI)"]
    end

    subgraph Backend["API — backend/ (FastAPI)"]
        ROUTES["app/api/routes.py<br/>app/api/analytics.py"]
        SERVICE["app/services/analytics_service.py<br/>loading + cache + response shapes"]
        SCHEMAS["app/schemas.py"]
        CONFIG["app/config.py"]
    end

    subgraph Frontend["Dashboard — frontend/ (React + Vite)"]
        CLIENT["api/client.js"]
        HOOK["hooks/useApi.js"]
        UI["components/sections/*"]
    end

    subgraph Optional["Optional tools"]
        DL["src/download_data.py"]
        DBPY["src/database.py"]
        SQL["sql/schema.sql<br/>sql/queries/*.sql"]
        DB[("SQLite<br/>data/processed/opsiq.db")]
    end

    KAGGLE[("Kaggle<br/>public dataset")] -. download .-> DL -.-> CSV
    CSV --> LOAD --> CALC --> REPORT
    LOAD --> VAL
    SERVICE --> LOAD
    SERVICE --> CALC
    SERVICE --> VAL
    ROUTES --> SERVICE
    ROUTES --> SCHEMAS
    SERVICE --> CONFIG
    UI --> HOOK --> CLIENT -- "HTTP GET, JSON" --> ROUTES
    CSV --> DBPY --> DB
    SQL --> DBPY
    DBPY -. "verify: compares with" .-> CALC
```

(The `SERVICE --> VAL` arrow is real: the API uses `data_validator.parse_order_date` to find the first and last purchase dates.)

| Component | Required? | Responsibility |
|---|---|---|
| CSV files | Yes | The source of truth. OpsIQ never changes them. |
| `src/` analytics engine | Yes | Every business rule. Functions take lists of row dictionaries and return dictionaries. No third-party packages. |
| CLI report | No (kept from Version 1) | Prints every metric to the terminal. |
| `backend/` API | For the dashboard | Turns the analytics into HTTP endpoints. Has no business rules of its own; it calls `src/`. |
| `frontend/` dashboard | No | Displays API results. Never calculates business metrics (it only does display maths such as "late minus over-3-days"). |
| SQLite database | No | A relational copy of the data for SQL practice. **Neither the API nor the CLI nor the dashboard reads it.** |
| `download_data.py` | No | Downloads the public dataset (used on a new PC and during deployment). |

---

## 2. Data flow: three processing paths

OpsIQ has **three separate paths** from the CSV files. They share the same `src/` functions, which is why their numbers agree.

```mermaid
flowchart LR
    CSV[("CSV files")]

    subgraph P1["Path 1 — CLI report"]
        A1["open_order / load_csv"] --> B1["analyze_* functions"] --> C1["print to terminal"]
    end

    subgraph P2["Path 2 — API and dashboard"]
        A2["open_order / load_csv"] --> B2["analyze_* / calculate_*"] --> C2["lru_cache in memory"] --> D2["route + Pydantic schema"] --> E2["JSON"] --> F2["React section"]
    end

    subgraph P3["Path 3 — SQL (optional)"]
        A3["database.py build"] --> B3[("opsiq.db")] --> C3["sql/queries/*.sql"] --> D3["printed table"]
    end

    CSV --> A1
    CSV --> A2
    CSV --> A3
```

### Path 1 — CLI report (`python -m src.business_report`)

1. `open_order()` reads `olist_orders_dataset.csv`; `load_csv()` reads the items, payments, products, customers, and translation files. Every row becomes a dictionary of strings.
2. `analyze_sales`, `analyze_products`, and `analyze_customers` build their reports.
3. `generate_business_report()` counts orders, calls `find_delivery_exceptions()` and `analyze_delivery_performance()`, and prints everything.
4. Nothing is stored. Each run reads the files again (about 5 seconds on the full data).

### Path 2 — API and dashboard

Using "late deliveries" (7,826) as the example:

1. **CSV → rows.** The first request (or the startup warm-up thread) calls `load_order_metrics()`, which calls `open_order()`.
2. **Rows → metrics.** `calculate_order_metrics()` runs `count_orders_by_status`, `calculate_delivery_performance`, and `find_delivery_exceptions` once, and stores the results in a frozen `OrderMetrics` object. The raw rows are then released.
3. **Metrics → cache.** `lru_cache` keeps the `OrderMetrics` object in memory for the life of the server process.
4. **Cache → JSON.** `/api/v1/analytics/summary` receives the object through `Depends(get_order_metrics)`. `get_business_summary()` picks the fields, and the `BusinessSummary` schema checks and serialises them.
5. **JSON → screen.** `SummarySection` calls `useApi(api.getSummary)`. `fetchJson()` sends the request; `useApi` tracks loading/error/data; `StatTile` shows `formatNumber(7826)` → `7,826`.

### Path 3 — SQL (`python -m src.database …`)

1. `build` runs `sql/schema.sql` in a new temporary file, then imports seven CSV files in one transaction, converting empty strings to `NULL` and text to `INTEGER`/`REAL` where the schema says so.
2. If every table imports, the temporary file replaces `data/processed/opsiq.db`.
3. `query NAME` runs one file from `sql/queries/`; `late` runs a parameterised query; `verify` runs the SQL queries **and** the Python functions and compares 33 values.

---

## 3. Dataset relationships

This diagram shows only the relationships **that the code actually uses** (Python joins in `src/`, or foreign keys in `sql/schema.sql`).

```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS : "customer_id"
    ORDERS ||--o{ ORDER_ITEMS : "order_id"
    ORDERS ||--o{ ORDER_PAYMENTS : "order_id"
    PRODUCTS ||--o{ ORDER_ITEMS : "product_id"
    SELLERS ||--o{ ORDER_ITEMS : "seller_id (SQL only)"
    CATEGORY_TRANSLATION |o--o{ PRODUCTS : "product_category_name (lookup, no FK)"

    CUSTOMERS {
        string customer_id PK "one per order"
        string customer_unique_id "one per person"
        string customer_state
    }
    ORDERS {
        string order_id PK
        string customer_id FK
        string order_status
        string order_purchase_timestamp
        string order_delivered_customer_date
        string order_estimated_delivery_date
    }
    ORDER_ITEMS {
        string order_id FK
        int order_item_id "PK with order_id"
        string product_id FK
        string seller_id FK
        float price
        float freight_value
    }
    ORDER_PAYMENTS {
        string order_id FK
        int payment_sequential "PK with order_id"
        string payment_type
        float payment_value
    }
    PRODUCTS {
        string product_id PK
        string product_category_name
    }
    SELLERS {
        string seller_id PK
    }
    CATEGORY_TRANSLATION {
        string product_category_name PK
        string product_category_name_english
    }
```

Where each relationship is used:

| Relationship | Python (`src/`) | SQL |
|---|---|---|
| orders → customers (`customer_id`) | `customer_analyzer` maps each order to a person (`customer_unique_id`) | FK; `repeat_customers.sql`, `orders_per_customer.sql` |
| order_items → orders (`order_id`) | `sales_analyzer` (orders with items), `customer_analyzer` (spending per person) | FK |
| order_items → products (`product_id`) | `product_analyzer` (category of each item) | FK; `revenue_by_category.sql` |
| products → translations | `product_analyzer` (English names) | `LEFT JOIN` only — two categories have no translation |
| order_payments → orders | **Not joined in Python**: payments are only summed by `payment_type` | FK |
| order_items → sellers | Not used in Python | FK only |

Checked on the real data (29 Oct 2026): every item's `product_id` exists in products, and every order's `customer_id` exists in customers.

---

## 4. Backend / API architecture

```mermaid
flowchart TB
    REQ["HTTP GET /api/v1/analytics/sales"] --> CORS["CORSMiddleware<br/>(main.py)"]
    CORS --> ROUTER["analytics router<br/>(api/analytics.py)"]
    ROUTER --> DEP["Depends(get_sales_report)<br/>→ _load(): 503 / 500 on failure"]
    DEP --> SVC["analytics_service.load_sales_report()<br/>lock + lru_cache"]
    SVC --> SRC["src.sales_analyzer.analyze_sales()"]
    ROUTER --> BUILD["analytics_service.get_sales(report)"]
    BUILD --> SCHEMA["schemas.Sales<br/>(validates + filters fields)"]
    SCHEMA --> RESP["JSON response"]
    ERR["Global exception handler<br/>→ 500 generic message"] -.-> RESP
```

| Layer | File | Knows about |
|---|---|---|
| App setup | `app/main.py` | Logging, CORS, startup warm-up thread, global error handler, router prefixes |
| Settings | `app/config.py` | Environment variables → a frozen `Settings` object |
| Routes | `app/api/routes.py`, `app/api/analytics.py` | URLs, query parameters, HTTP status codes |
| Service | `app/services/analytics_service.py` | Loading files, caching, choosing response fields. **No HTTP.** |
| Schemas | `app/schemas.py` | The exact shape of every JSON response |
| Business rules | `src/*.py` (project root) | The calculations. **No HTTP, no caching.** |

Design choices:

- **Versioned paths** (`/api/v1/...`) so a future incompatible version can live alongside this one.
- **Read-only:** every endpoint is `GET`; CORS only allows `GET`.
- **One endpoint per dashboard section**, so one failing section does not blank the whole page.
- **Dependencies for data:** routes declare the data they need with `Depends(...)`; tests replace these with sample data.
- **Response schemas** guarantee that unlisted fields (for example, top customers) can never appear in a response.
- **`null` instead of fake zeros:** a percentage of zero orders is `null`.
- **Import path:** `analytics_service.py` adds the project root to `sys.path` so it can `import src...`. That is why the API must run with the full repository present, from the `backend/` folder.

All endpoints: [API_REFERENCE.md](API_REFERENCE.md).

---

## 5. Caching strategy

| Question | Answer |
|---|---|
| What is cached? | The calculated results: one `OrderMetrics` object and the sales, product, and customer reports. Not the raw CSV rows. |
| Where? | In the API process's memory, using `functools.lru_cache(maxsize=1)` in `analytics_service.py`. |
| When is it filled? | In a background thread at startup (`OPSIQ_PRELOAD_DATA=true`), or by the first request that needs it. Measured on 29 Oct 2026: warm-up finished about 11 seconds after start. |
| Two requests before it is filled? | A lock (`_cache_lock`) makes the second wait for the first calculation instead of repeating it. |
| What if loading fails? | `lru_cache` does not store exceptions, so the next request tries again. |
| How is it refreshed? | Restart the server. Tests call `clear_cache()`. |
| How many times is each file read? | Once per cached report: orders twice (order metrics and customer report), order items three times (sales, products, customers). |
| Multiple server processes? | Each process has its own cache and does its own warm-up. The project runs one process. |
| Why not Redis? | One process, read-only data that only changes when the files change. An external cache would add a service with no benefit. |
| Measured cost | Cached responses ~5 ms (measured 29 Oct 2026). About 165 MB of memory after warm-up (measured in earlier work; **not re-measured** in this audit). |

Trade-off: the calculations are CPU-bound, and Python runs one thread at a time (the GIL). So during the warm-up, even `/health` can be slow to answer.

---

## 6. Error-handling strategy

| Layer | Strategy |
|---|---|
| `src/` | Raises normal Python exceptions (`FileNotFoundError`, `ValueError`). Skips orders with missing or unreadable dates and counts them. |
| CLI report | Catches `FileNotFoundError` for the six data files and prints which file is missing and where to put it. Other module CLIs (for example `python -m src.sales_analyzer`) do **not** catch it and show a traceback. |
| Service | No HTTP knowledge. Lets exceptions through, so they are never cached. |
| Routes (`_load`) | `FileNotFoundError` → **503** naming only the missing file. Any other loading error → **500** with a short message. Full details go to the log. |
| FastAPI | Invalid query parameters → **422**. Unknown paths → **404**. Wrong method → **405**. |
| Global handler (`main.py`) | Any other exception → **500** `{"detail": "An unexpected server error occurred."}`; stack trace only in the log. |
| Frontend client | Network failure → "Could not reach the OpsIQ API at …". HTTP error → the API's `detail` message. |
| Frontend UI | Each section shows its own error and a "Try again" button; other sections keep working. |

Observed on 29 Oct 2026 with an empty data folder: `/health` → 200, analytics → 503 with the file name, and no folder paths in the response. One quirk: with **no data**, `?limit=0` also returns 503 (not 422), because the data dependency fails before the parameter is checked. With data present, it correctly returns 422.

---

## 7. Frontend architecture

```mermaid
flowchart TB
    MAIN["main.jsx<br/>createRoot + StrictMode"] --> APP["App.jsx"]
    APP --> HEADER["Header<br/>(+ DataPeriod → /dataset-info)"]
    APP --> S1["SummarySection → /summary"]
    APP --> S2["DeliverySection → /delivery-performance"]
    APP --> S3["OrderStatusSection → /orders-by-status"]
    APP --> S4["ExceptionsSection → /delivery-exceptions?limit="]
    APP --> S5["SalesSection → /sales"]
    APP --> S6["ProductsSection → /products"]
    APP --> S7["CustomersSection → /customers"]

    S1 & S2 & S3 & S4 & S5 & S6 & S7 --> HOOK["useApi(load)<br/>loading / success / error + retry"]
    HOOK --> CLIENT["api/client.js<br/>fetchJson + ApiError"]
    CLIENT --> API["FastAPI backend"]

    S1 & S2 & S3 & S4 & S5 & S6 & S7 --> SHARED["Shared components:<br/>Section · AsyncContent · StatTile/StatGrid<br/>BarList · ProportionBar"]
    S2 & S3 & S5 & S6 & S7 --> UTILS["utils/transform.js<br/>utils/format.js"]
```

- **One page**, no router. The header nav links jump to sections (`#summary`, `#delivery`, …).
- **Each section fetches its own data** through `useApi`, so sections load and fail independently.
- **No chart library.** Charts are HTML lists and `<span>` bars (`BarList`, `ProportionBar`) with the values printed as text.
- **Styling:** one CSS file (`src/index.css`) with CSS variables (colour tokens). Dark colours switch automatically with the operating system setting (`prefers-color-scheme`); there is no manual toggle.
- **Configuration:** `VITE_API_BASE_URL` (default `http://127.0.0.1:8000`).

Section-by-section detail: [PROJECT_MASTER_REFERENCE.md §8](PROJECT_MASTER_REFERENCE.md#8-frontend-and-dashboard).

---

## 8. Database architecture

- **Engine:** SQLite (Python's built-in `sqlite3`). One file: `data/processed/opsiq.db` (about 98 MB). **Not in Git**; rebuild with `python -m src.database build`.
- **Tables:** `customers`, `sellers`, `category_translations`, `products`, `orders`, `order_items`, `order_payments`.
- **Not imported:** geolocation (no unique key) and reviews (duplicate `review_id`s, not used by any metric).

```mermaid
erDiagram
    customers ||--o{ orders : places
    orders ||--o{ order_items : contains
    orders ||--o{ order_payments : "paid by"
    products ||--o{ order_items : "sold as"
    sellers ||--o{ order_items : sells
    category_translations |o..o{ products : "translates (no FK)"
```

Design decisions:

- **Column names match the CSV headers** (including Olist's spelling `product_name_lenght`), so every value is traceable.
- **Timestamps are `TEXT`** in `YYYY-MM-DD HH:MM:SS`; `julianday()` turns them into days for date maths.
- **No foreign key from products to translations:** two categories have no translation.
- **Indexes** on the join and filter columns: `orders.customer_id`, `orders.order_status`, `order_items.product_id`, `order_items.seller_id`, `customers.customer_unique_id`, `order_payments.payment_type`.
- **Repeatable build:** written to `opsiq.db.building` in one transaction and swapped in only on success.
- **Manual, not automatic:** nothing builds the database for you.

Every column and query: [PROJECT_MASTER_REFERENCE.md §7](PROJECT_MASTER_REFERENCE.md#7-sql-and-database).

---

## 9. Testing and CI/CD architecture

```mermaid
flowchart LR
    DEV["git push / pull request"] --> GHA["GitHub Actions<br/>.github/workflows/ci.yml"]
    GHA --> J1["Job: Python analytics, database, and API<br/>ubuntu · Python 3.14"]
    GHA --> J2["Job: React dashboard<br/>ubuntu · Node 24"]
    J1 --> T1["root tests/ — 89<br/>(no pip install needed)"]
    J1 --> I1["pip install backend/requirements.txt"] --> T2["backend/tests/ — 61"]
    J2 --> I2["npm ci"] --> L["npm run lint (oxlint)"] --> T3["npm test (Vitest) — 41"] --> B["npm run build"]
```

| Suite | Tests | What it covers | Data |
|---|---:|---|---|
| `tests/` | 89 | Analytics modules, validation, CLI report, SQLite build and queries, download helper | Hand-written rows and temporary CSV files |
| `backend/tests/` | 61 | Every endpoint, empty data, missing/broken files, 404/422/500/503, no leaked paths or customer data, caching, CORS, settings, agreement with the CLI report | Sample orders and temporary CSV folders |
| `frontend/src/**/*.test.*` | 41 | Formatting, chart transforms, API client, components, loading/error/empty states, retry, the limit selector, the whole page with a mocked API | Mocked `fetch` |

- **No test needs the real dataset**, so CI downloads nothing.
- **CI status:** runs #1 and #2 on GitHub both **passed** (29 Oct 2026).
- **Not automated:** browser end-to-end tests, code coverage, and SQL-vs-Python verification on the full data (`verify` is run by hand).

Earlier work (before this audit) reports a manual Playwright check of the dashboard at 1440 px and 390 px and in dark mode. That script is **not in the repository**, and this audit could not repeat the mobile and dark-mode checks. See [TESTING_GUIDE.md](TESTING_GUIDE.md).

---

## 10. Deployment architecture (planned)

**Status: configured, not deployed.**

```mermaid
flowchart LR
    U["Browser"] -- "HTML, JS, CSS" --> S["Static site<br/>(frontend/dist)"]
    U -- "GET /api/v1/... (CORS)" --> A["Web service<br/>Uvicorn + FastAPI"]
    K[("Kaggle<br/>public dataset")] -- "downloaded during build" --> A
```

- The **dashboard** is static files (`npm run build`).
- The **API** is one Python process. At build time it installs `backend/requirements.txt` and runs `python -m src.download_data`; at startup it warms its cache.
- The two connect only through configuration: `VITE_API_BASE_URL` (dashboard build) and `OPSIQ_CORS_ORIGINS` (API).
- No database server and no persistent disk.

Steps: [DEPLOYMENT.md](DEPLOYMENT.md).
