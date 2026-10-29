# OpsIQ — Project Master Reference

The complete technical reference for OpsIQ. It was written from the actual code, data, Git history, and test runs on **29 October 2026** (commit `ac32a9d`, Windows 11, Python 3.14.6, Node 24.18.0).

**Evidence labels used in this document**

- **Verified** — checked by running code, tests, or real requests during the 29 Oct 2026 audit.
- **Tested** — covered by automated tests that pass, but not checked by hand in this audit.
- **Historical** — reported by earlier work, not reproduced in this audit.
- **Not verified** — could not be checked.

| Need | Go to |
|---|---|
| Current status and next steps | [PROJECT_HANDOVER.md](PROJECT_HANDOVER.md) |
| Set up on a new PC | [SETUP_AND_MIGRATION.md](SETUP_AND_MIGRATION.md) |
| Diagrams and data flow | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Endpoints | [API_REFERENCE.md](API_REFERENCE.md) |
| Tests | [TESTING_GUIDE.md](TESTING_GUIDE.md) |
| Remaining work | [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) |
| Learning and interviews | [LEARNING_GUIDE.md](LEARNING_GUIDE.md) |
| Hosting | [DEPLOYMENT.md](DEPLOYMENT.md) |

## Contents

1. [Project overview](#1-project-overview)
2. [Directory tree](#2-directory-tree)
3. [Module reference](#3-module-reference)
4. [Datasets and data engineering](#4-datasets-and-data-engineering)
5. [Python analytics and business logic](#5-python-analytics-and-business-logic)
6. [Metric catalogue](#6-metric-catalogue)
7. [SQL and database](#7-sql-and-database)
8. [Frontend and dashboard](#8-frontend-and-dashboard)
9. [Dependencies](#9-dependencies)
10. [Git, GitHub, and CI](#10-git-github-and-ci)
11. [Deployment status](#11-deployment-status)
12. [AI functionality](#12-ai-functionality)
13. [Risks and technical debt](#13-risks-and-technical-debt)
14. [Original plan vs what was built](#14-original-plan-vs-what-was-built)

---

## 1. Project overview

| # | Question | Answer |
|---|---|---|
| 1 | Full name | **OpsIQ — AI-Powered Business Operations Intelligence Platform** |
| 2 | Main purpose | Turn raw e-commerce order data into trustworthy, tested operations metrics that a manager can read on a dashboard. |
| 3 | Business problem | Operations managers need quick answers: how many orders were delivered, how many were late and by how much, which late orders to investigate first, where revenue comes from, how customers pay, and how many customers return. Raw CSV exports cannot answer this directly. |
| 4 | Intended users | Operations/logistics managers (dashboard); analysts (CLI report, SQL); developers (API). Also portfolio reviewers and interviewers. |
| 5 | Main features (existing) | CLI business report · data-quality report · 10-route REST API with caching · React dashboard with 7 sections · optional SQLite database with 7 example queries · 191 automated tests · CI on GitHub |
| 6 | Input | The public **Olist Brazilian e-commerce dataset** (CSV files): ~99,000 orders from Sept 2016 to Oct 2018, with items, payments, products, customers, and category translations. |
| 7 | Processing | Python reads the CSVs into lists of dictionaries, filters and groups them with plain loops (`collections.defaultdict`, `datetime`), and returns dictionaries of metrics. The API calculates once and caches; the SQL path imports the CSVs into SQLite and runs queries. |
| 8 | Output | A printed text report, a data-quality report, JSON from the API, a web dashboard, and SQL query tables. |
| 9 | How a user interacts | Opens the dashboard in a browser (http://localhost:5173), or runs `python -m src.business_report`, or calls the API (http://127.0.0.1:8000/docs), or runs `python -m src.database query ...`. |
| 10 | Real business value | One set of tested rules gives the same numbers everywhere; late orders are ranked for follow-up; data problems (1,382 out-of-order timestamps, 8 delivered orders without a date) are reported rather than hidden; private customer details never leave the API. |
| 11 | Career relevance | It is a realistic full-stack data application: data engineering, analytics, back end, front end, SQL, testing, CI, and documentation. These are the skills asked for in junior data, back-end, and full-stack roles. |
| 12 | Skills shown | Python (modules, CSV, dates, dictionaries, dataclasses, argparse), data validation, analytics, SQL (DDL, keys, joins, CTEs, aggregates, parameters), FastAPI (routes, dependencies, Pydantic, CORS, error handling, caching, threading), React (components, hooks, state, async data, accessibility), automated testing in Python and JavaScript, Git, GitHub Actions, deployment configuration, technical writing. |

**Existing vs planned.** Everything in row 5 exists and works. The **"AI-Powered"** part does **not** exist yet: there is no AI or machine-learning code (see [§12](#12-ai-functionality)). Deployment is configured but **not done**. Interview explanations (short, technical, non-technical) are in [LEARNING_GUIDE.md](LEARNING_GUIDE.md#explaining-opsiq).

---

## 2. Directory tree

Generated files and folders that are not in Git are marked ⛔.

```text
OpsIQ/
├── .github/workflows/ci.yml        CI: Python + frontend jobs
├── .gitignore                      What Git must never store
├── .python-version                 3.14 (used by hosting platforms)
├── README.md                       Project front page
├── render.yaml                     Render Blueprint (not deployed)
├── src/                            Version 1 analytics engine (standard library only)
│   ├── data_loader.py              Paths + orders CSV loader
│   ├── data_validator.py           Data-quality checks + report
│   ├── data_analyzer.py            Orders by status
│   ├── delivery_analyzer.py        On-time vs late, delays
│   ├── delivery_exceptions.py      Late orders, longest first
│   ├── sales_analyzer.py           Revenue, freight, payments + generic load_csv
│   ├── product_analyzer.py         Categories and products
│   ├── customer_analyzer.py        Unique/repeat customers, states
│   ├── business_report.py          CLI report (main entry point)
│   ├── database.py                 SQLite build / query / verify CLI
│   ├── download_data.py            Kaggle dataset download CLI
│   └── __pycache__/ ⛔
├── tests/                          89 unittest tests for src/
├── backend/
│   ├── requirements.txt            fastapi, uvicorn, httpx2 (pinned)
│   ├── app/
│   │   ├── main.py                 FastAPI app, CORS, startup, error handler
│   │   ├── config.py               Settings from environment variables
│   │   ├── schemas.py              Pydantic response models
│   │   ├── api/routes.py           /  and /health
│   │   ├── api/analytics.py        8 analytics routes
│   │   └── services/analytics_service.py   Loading, caching, response shapes
│   ├── tests/                      61 API tests
│   └── .venv/ ⛔                    Virtual environment
├── frontend/
│   ├── index.html                  HTML shell
│   ├── package.json / package-lock.json
│   ├── vite.config.js              Vite + Vitest settings
│   ├── .oxlintrc.json              Lint rules
│   ├── .env.example                Template for VITE_API_BASE_URL
│   ├── public/favicon.svg
│   ├── src/
│   │   ├── main.jsx, App.jsx, index.css
│   │   ├── api/client.js           All HTTP requests
│   │   ├── hooks/useApi.js         Loading/error/data state
│   │   ├── components/             Shared UI pieces
│   │   ├── components/sections/    7 dashboard sections
│   │   ├── utils/format.js, transform.js
│   │   └── test/                   Test setup + fetch mock
│   ├── node_modules/ ⛔
│   └── dist/ ⛔                     Production build
├── sql/
│   ├── schema.sql                  7 tables, keys, indexes
│   └── queries/*.sql               7 example queries
├── data/
│   ├── raw/ ⛔                      Olist CSV files
│   └── processed/
│       ├── .gitkeep                Keeps the empty folder in Git
│       └── opsiq.db ⛔              SQLite database
└── docs/                           Documentation, screenshots, original master plan (.docx)
```

**Essential to run:** `src/`, `backend/app/`, `backend/requirements.txt`, `frontend/` (without `node_modules`/`dist`), `sql/` (for the database), and the 6 required CSV files.
**Generated automatically:** `__pycache__/`, `.venv/`, `node_modules/`, `dist/`, `opsiq.db`, `opsiq.db.building` (temporary).

---

## 3. Module reference

### 3.1 Version 1 analytics (`src/`)

| File | Purpose | Main functions | Inputs | Outputs | Uses | Used by | Status |
|---|---|---|---|---|---|---|---|
| `data_loader.py` | Locate the project and load orders | `open_order(file_path)`; constants `PROJECT_ROOT`, `RAW_DATA_DIR`, `ORDERS_FILE` | Path to orders CSV | `list[dict[str,str]]` | `csv`, `pathlib` | Almost everything: business_report, database, download_data, every module's CLI, API service | Verified |
| `data_validator.py` | Find data-quality problems | `is_missing`, `check_missing_values`, `check_missing_order_ids`, `check_duplicate_order_ids`, `check_invalid_order_statuses`, `parse_order_date`, `check_invalid_date_formats`, `check_inconsistent_dates`, `check_delivered_orders_missing_delivery_dates`, `validate_orders` | Order rows | Counts/lists; printed report | `datetime` | Own CLI; API service (`parse_order_date`) | Verified |
| `data_analyzer.py` | Orders by status | `count_orders_by_status`, `analyze_orders` (prints) | Order rows | `dict[status,int]` | — | API service, database verify. `analyze_orders` is used only by its own CLI | Verified |
| `delivery_analyzer.py` | Delivery timeliness | `calculate_delivery_performance` (returns), `analyze_delivery_performance` (prints) | Order rows | Dict of 10 metrics | `datetime` | business_report, API, database verify | Verified |
| `delivery_exceptions.py` | Late orders list | `find_delivery_exceptions`, `display_delivery_exceptions` | Order rows | List of `{order_id, estimated_delivery, actual_delivery, days_late}`, longest first | `datetime` | business_report, API | Verified |
| `sales_analyzer.py` | Revenue and payments; generic loader | `load_csv`, `analyze_sales` | Item rows, payment rows | Dict: revenue, freight, orders with items, average, payments by method | `csv`, `defaultdict` | business_report, customer_analyzer, product_analyzer CLI, API, database | Verified |
| `product_analyzer.py` | Category and product performance | `analyze_products` | Item rows, product rows, translation dict | Dict: total products, missing categories, top 10 categories, top 10 products | `defaultdict` | business_report, API, database | Verified |
| `customer_analyzer.py` | Customer behaviour | `analyze_customers` | Order, customer, item rows | Dict: unique, repeat, %, top 10 customers by spending, unique per state | `defaultdict` | business_report, API (without top customers), database | Verified |
| `business_report.py` | The Version 1 CLI report | `generate_business_report` | Order rows + three reports | Printed report | All analysers | Users | Verified |
| `database.py` | Optional SQLite layer | `connect`, `import_table`, `build_database`, `list_queries`, `run_query`, `find_late_orders`, `compare_with_python`, `main` | CSV folder, DB path | DB file; query tables; comparison | `sqlite3`, `csv`, analysers | Users | Verified |
| `download_data.py` | Get the dataset | `missing_files`, `extract_files`, `download_dataset`, `main` | Kaggle URL | CSV files in `data/raw` | `urllib`, `zipfile` | Users, `render.yaml` build | Verified (real download, 29 Oct) |

**Known issues** (details in [§13](#13-risks-and-technical-debt)):
- The `__main__` blocks of `sales_analyzer`, `product_analyzer`, and `customer_analyzer` use relative paths (`"data/raw/..."`), so they only work from the project root. They also don't catch a missing file.
- `sales_analyzer` and `product_analyzer` would crash on an empty `price`, while `customer_analyzer` treats it as 0. The real data has no empty prices.

### 3.2 Backend (`backend/app/`)

| File | Purpose | Main items | Used by | Status |
|---|---|---|---|---|
| `main.py` | Create the app | `configure_logging`, `lifespan` (starts the warm-up thread), `CORSMiddleware`, `handle_unexpected_error`, router registration | Uvicorn (`app.main:app`) | Verified |
| `config.py` | Settings | `Settings` dataclass, `load_settings(environ)`, `PROJECT_ROOT` | main, service | Verified + tested |
| `api/routes.py` | Basic routes | `api_root`, `health_check` | main | Verified |
| `api/analytics.py` | Analytics routes | `_load` (error → 503/500), `get_order_metrics` and other dependencies, 8 route functions, `MAX_EXCEPTION_LIMIT = 100` | main | Verified |
| `services/analytics_service.py` | Bridge to `src/` | `OrderMetrics` dataclass, `calculate_order_metrics`, `load_*` (cached), `clear_cache`, `warm_cache`, `get_*` response builders | routes | Verified |
| `schemas.py` | Response shapes | `BusinessSummary`, `OrdersByStatus`, `DeliveryPerformance`, `DeliveryException(s)`, `DatasetInfo`, `Sales`, `CategoryPerformance`, `ProductPerformance`, `Products`, `Customers` | routes | Verified |

### 3.3 Frontend (`frontend/src/`)

| File | Purpose | Status |
|---|---|---|
| `main.jsx` | Mounts `<App/>` in `StrictMode` | Verified (renders) |
| `App.jsx` | Page layout: skip link, header, 7 sections, footer | Verified |
| `api/client.js` | `API_BASE_URL`, `ApiError`, `fetchJson`, `api.*` (one function per endpoint) | Verified |
| `hooks/useApi.js` | `useApi(load)` → `{status, data, error, retry}` with request cancelling | Verified |
| `components/AsyncContent.jsx` | `LoadingState`, `ErrorState`, `EmptyState`, `AsyncContent` | Tested (loading/error states not seen by hand in this audit) |
| `components/Header.jsx` | Brand, title, data period (`/dataset-info`), section links | Verified |
| `components/Section.jsx` | Card with heading, description, optional actions | Verified |
| `components/StatTile.jsx` | `StatTile`, `StatGrid` (KPI cards as a description list) | Verified |
| `components/BarList.jsx` | Horizontal HTML bar chart with values and a hover/focus tooltip | Verified |
| `components/ProportionBar.jsx` | One stacked bar + legend (on time vs late) | Verified |
| `components/sections/*.jsx` | The 7 sections ([§8](#8-frontend-and-dashboard)) | Verified (desktop) |
| `utils/format.js` | `formatNumber`, `formatCompactNumber`, `formatPercent`, `formatCurrency`, `formatCompactCurrency`, `formatDays`, `formatDate`, `formatDateTime`, `humanizeLabel` | Tested |
| `utils/transform.js` | `undeliveredStatusItems`, `delayBandItems`, `topItemsWithOther`, `paymentMethodItems`, `categoryItems`, `delaySeverity` | Tested |
| `index.css` | All styles; colour tokens; dark mode via `prefers-color-scheme`; breakpoints at 1080, 860, and 760 px | Desktop verified; mobile and dark mode **not verified** in this audit |

---

## 4. Datasets and data engineering

### 4.1 Files

Source: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), Kaggle, licence **CC BY-NC-SA 4.0**. Format: UTF-8 CSV with a header row; every value is read as text. Sizes and row counts were measured on 29 Oct 2026.

| File (`data/raw/`) | Size | Rows | Used by | Key | Duplicate keys | Missing values |
|---|---:|---:|---|---|---:|---|
| `olist_orders_dataset.csv` | 17.7 MB | 99,441 | Everything | `order_id` | 0 | `order_approved_at` 160, `order_delivered_carrier_date` 1,783, `order_delivered_customer_date` 2,965 |
| `olist_order_items_dataset.csv` | 15.4 MB | 112,650 | Sales, products, customers, SQL | `order_id` + `order_item_id` | 0 | none |
| `olist_order_payments_dataset.csv` | 5.8 MB | 103,886 | Sales, SQL | `order_id` + `payment_sequential` | 0 | none |
| `olist_products_dataset.csv` | 2.4 MB | 32,951 | Products, SQL | `product_id` | 0 | category, name length, description length, photos: 610 each; weight and size: 2 each |
| `olist_customers_dataset.csv` | 9.0 MB | 99,441 | Customers, SQL | `customer_id` | 0 | none |
| `product_category_name_translation.csv` | 2.6 KB | 71 | Products, SQL | `product_category_name` | 0 | none |
| `olist_sellers_dataset.csv` | 0.2 MB | 3,095 | **SQL only** | `seller_id` | 0 | none |
| `olist_geolocation_dataset.csv` | 61.3 MB | 1,000,163 | **Not used** | none | — | none |
| `olist_order_reviews_dataset.csv` | 14.5 MB | 99,224 | **Not used** | `review_id` | 814 | comment title 87,658, comment message 58,274 |

### 4.2 Columns

| File | Columns |
|---|---|
| orders | `order_id`, `customer_id`, `order_status`, `order_purchase_timestamp`, `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`, `order_estimated_delivery_date` |
| order items | `order_id`, `order_item_id`, `product_id`, `seller_id`, `shipping_limit_date`, `price`, `freight_value` |
| payments | `order_id`, `payment_sequential`, `payment_type`, `payment_installments`, `payment_value` |
| products | `product_id`, `product_category_name`, `product_name_lenght`, `product_description_lenght`, `product_photos_qty`, `product_weight_g`, `product_length_cm`, `product_height_cm`, `product_width_cm` (the "lenght" spelling is in the source) |
| customers | `customer_id`, `customer_unique_id`, `customer_zip_code_prefix`, `customer_city`, `customer_state` |
| translation | `product_category_name`, `product_category_name_english` |
| sellers | `seller_id`, `seller_zip_code_prefix`, `seller_city`, `seller_state` |

**Types.** In Python, everything is text until a function converts it: `float(price)`, `float(freight_value)`, `float(payment_value)`, and `datetime.strptime(value, "%Y-%m-%d %H:%M:%S")` for dates. In SQLite, the types come from `sql/schema.sql` (TEXT, INTEGER, REAL; timestamps stay TEXT).

**Relationships** (checked on the real data: 0 orphan items, 0 orders without a customer):
- orders.`customer_id` → customers. One person (`customer_unique_id`) can have many `customer_id`s, one per order.
- order_items.`order_id` → orders; order_items.`product_id` → products; order_items.`seller_id` → sellers.
- payments.`order_id` → orders.
- products.`product_category_name` → translation (two categories have no translation).

Diagram: [ARCHITECTURE.md §3](ARCHITECTURE.md#3-dataset-relationships).

### 4.3 Data-quality findings (from `python -m src.data_validator`, 29 Oct 2026)

| Check | Result |
|---|---|
| Missing / duplicate order IDs | 0 / 0 |
| Invalid statuses | 0 |
| Unreadable dates | 0 |
| Out-of-order processing timestamps | **1,382** (all 10 examples shown were carrier pickup recorded before approval) |
| Delivered orders without a delivery date | **8** |

These are **reported, not corrected**.

### 4.4 The loading process

| Question | Answer |
|---|---|
| How are paths resolved? | `data_loader.PROJECT_ROOT` = the folder above `src/` (from `__file__`), so the project works anywhere. `RAW_DATA_DIR = PROJECT_ROOT/data/raw`. The API uses `OPSIQ_DATA_DIR` (default `data/raw`, relative to the project root). The CLI report always uses `RAW_DATA_DIR`; it has no setting to change it. |
| How are CSVs read? | `csv.DictReader` with `encoding="utf-8-sig"` (strips an invisible byte-order mark) and `newline=""`. `open_order()` and `load_csv()` do the same thing (two copies of the same function). |
| Missing values? | Empty strings stay empty strings. Each function decides: delivery analysis **skips and counts** orders with a missing date; products with no category become `"unknown"`; the validator counts blanks (including whitespace-only values). In SQLite, empty becomes `NULL`. |
| Dates and numbers? | Dates: `datetime.strptime(..., "%Y-%m-%d %H:%M:%S")`; a bad date is skipped (`ValueError` caught). Numbers: `float()` with no protection, so a bad number raises an error (→ 500 in the API). |
| Duplicates? | The Python analytics do **not** remove duplicates (the validator only counts them; there are none). The SQLite import skips rows whose primary key already exists and reports how many. |
| Cached? | Only in the API (in memory, per process). The CLI reads the files on every run. |
| Loaded once or repeatedly? | API: once per report (orders ×2, items ×3 in total), then cached until restart. CLI: every run. |
| Is SQLite generated from the CSVs? | Yes, manually with `python -m src.database build`. |
| A required file is missing? | CLI report: prints `Dataset file not found: <name>` and the folder, then exits with code 1. API: `/health` still works; analytics return 503 naming the file. Module CLIs: Python traceback. `database build`: `Error: ...` and exit code 1, and any old database is kept. |
| Is the full dataset required? | Tests: **no data needed**. CLI report and API: the 6 required files. Database: those 6 plus sellers. |

### 4.5 Moving to a new PC

The CSV files do **not** need to be copied: `python -m src.download_data --with-database-files` fetched byte-identical files on 29 Oct 2026. Copy `data/raw/` by hand only if the download fails. See [SETUP_AND_MIGRATION.md §4](SETUP_AND_MIGRATION.md#4-get-the-dataset).

---

## 5. Python analytics and business logic

| Module | Business question | Reads | Processing | Returns / shows | Tests |
|---|---|---|---|---|---|
| `data_analyzer` | How many orders are in each status? | orders | Count by `order_status` (missing status → `"unknown"`) | dict | `test_data_analyzer.py` (6) |
| `delivery_analyzer` | How punctual are deliveries? | orders | Delivered only → parse both dates → delay = actual − estimated → on time if ≤ 0 | 10 metrics | `test_delivery_analyzer.py` (8) |
| `delivery_exceptions` | Which orders were late, worst first? | orders | Same filter and delay → keep delay > 0 → sort by `days_late` descending | list | `test_delivery_exceptions.py` (5) |
| `sales_analyzer` | How much revenue and freight? How do people pay? | items, payments | Sum `price`, `freight_value`; distinct orders; sum `payment_value` by `payment_type` | dict | `test_sales_analyzer.py` (5) |
| `product_analyzer` | Which categories and products sell best? | items, products, translations | Item → product → category (→ English); sum price and count items per category and product | dict, top 10 each | `test_product_analyzer.py` (6) |
| `customer_analyzer` | How many real customers, how many return, where are they? | orders, customers, items | `customer_id` → `customer_unique_id`; distinct orders per person; spending per person; people per state | dict | `test_customer_analyzer.py` (6) |
| `data_validator` | Can we trust the order data? | orders | Seven checks (see §4.3) | printed report | `test_data_validator.py` (20) |
| `business_report` | Everything in one report | 6 files | Calls the above | printed report | `test_business_report.py` (2) |

### Running the CLI report

**Folder:** project root. **Command:** `python -m src.business_report`

**Output:** about 80 lines of plain text in these sections: `OPSIQ BUSINESS SUMMARY REPORT` (totals) → Delivery Performance Details → Highest-Priority Delivery Exceptions (top 5) → Sales & Payment Analytics → Product Performance Analytics (top 5 categories and products) → Customer Analytics (top 5 customers by spending, top 10 states) → `END OF OPSIQ REPORT`. It takes about 5 seconds on the full data. **Verified** 29 Oct 2026.

Other module CLIs (project root only): `python -m src.data_validator`, `python -m src.data_analyzer`, `python -m src.delivery_analyzer`, `python -m src.delivery_exceptions`, `python -m src.sales_analyzer`, `python -m src.product_analyzer`, `python -m src.customer_analyzer`.

### Duplicate logic, complexity, and gaps (not changed during the audit)

| Finding | Where | Suggested improvement |
|---|---|---|
| The "delivered + both dates + parse + delay" logic is written twice | `delivery_analyzer.calculate_delivery_performance`, `delivery_exceptions.find_delivery_exceptions` | One shared helper that returns the delay or `None` |
| A third date parser with slightly different rules (it strips spaces) | `data_validator.parse_order_date` | Use one parser everywhere |
| Delivered orders counted separately | `business_report.generate_business_report` | Use `count_orders_by_status` |
| Two identical CSV loaders | `data_loader.open_order`, `sales_analyzer.load_csv` | Keep one in `data_loader` |
| Translation dictionary built in four places | business_report, product_analyzer CLI, API service, database verify | One helper function |
| Confusing names | `analyze_sales` returns `total_orders` (really "orders with items") and `average_order_value` (really "average product value per order"); the API renames them | Rename in `src/` (and update the API and tests) |
| Missing-number handling differs | `sales`/`product` crash on an empty price; `customer` uses 0 | Pick one rule |
| Module CLIs use relative paths and don't handle a missing file | `sales_analyzer`, `product_analyzer`, `customer_analyzer` | Use `RAW_DATA_DIR`, as `business_report` does |
| A renamed CSV column gives a `KeyError` (API: generic 500) | All analysers | Check the columns on load, as `database.import_table` does |
| `analyze_orders()` (printing version) is used only by its own CLI | `data_analyzer` | Fine as is; note it is not part of the main report |

---

## 6. Metric catalogue

All values are from the full dataset; "Verified" means the API/CLI/SQL values were seen on 29 Oct 2026.

| Metric | Business meaning | Calculation | Source columns | File · function | Value | Status |
|---|---|---|---|---|---:|---|
| Total orders | Size of the business | Row count | orders.* | business_report; service `OrderMetrics.total_orders` | 99,441 | Verified (CLI = API = SQL) |
| Orders by status | Where orders are in the process | Count per status | `order_status` | data_analyzer · `count_orders_by_status` | delivered 96,478 … | Verified (API = SQL) |
| Delivered % | Share completed | delivered ÷ total × 100 | `order_status` | service · `get_business_summary` | 97.02% | Verified |
| Delivered orders analysed | Base for punctuality | Delivered with 2 valid dates | status, delivered + estimated date | delivery_analyzer | 96,470 | Verified (= SQL) |
| Skipped orders | Data gaps | Delivered with a missing/bad date | same | delivery_analyzer | 8 | Verified |
| On-time orders / % | Promise kept | delay ≤ 0 seconds | same | delivery_analyzer | 88,644 / 91.89% | Verified (= SQL) |
| Late orders / % | Promise broken | delay > 0 seconds | same | delivery_analyzer; delivery_exceptions (count) | 7,826 / 8.11% | Verified (= SQL) |
| Average delay | How bad lateness is | Mean delay of late orders, in days | same | delivery_analyzer | 9.55 days | Verified (= SQL) |
| Maximum delay | Worst case | Max delay | same | delivery_analyzer | 188.98 days | Verified (= SQL) |
| Over 3 / 7 days late | Serious lateness | Count delay > 3 / > 7 days | same | delivery_analyzer | 5,164 / 3,345 | Verified (= SQL) |
| Delivery exceptions | Orders to investigate | Late orders, sorted by days late | same + `order_id` | delivery_exceptions | 7,826 rows | Verified (= SQL top 10) |
| Product revenue | Goods sold (not total company revenue) | Σ `price` | items.`price` | sales_analyzer | 13,591,643.70 | Verified (= SQL) |
| Freight value | Shipping charged | Σ `freight_value` | items | sales_analyzer | 2,251,909.54 | Verified (= SQL) |
| Orders with items | Orders that have item rows | Distinct `order_id` in items | items | sales_analyzer (`total_orders`) | 98,666 | Verified (= SQL) |
| Average product value per order | Typical basket | revenue ÷ orders with items | items | sales_analyzer (`average_order_value`) | 137.75 | Verified |
| Payment totals by method | How customers pay | Σ `payment_value` by `payment_type` | payments | sales_analyzer | credit card 12.54M … | Verified (CLI = API) |
| Products in catalogue | Assortment size | Row count | products | product_analyzer | 32,951 | Verified |
| Products missing category | Catalogue quality | Empty `product_category_name` | products | product_analyzer | 610 | Verified |
| Revenue / items by category (top 10) | Best categories | Σ price and count items per category (English name if any) | items, products, translation | product_analyzer | health_beauty 1,258,681.34 / 9,670 | Verified (= SQL) |
| Top products by items sold (top 10) | Best sellers | Count items per product | items | product_analyzer | 527 items for the top product | Verified (CLI = API) |
| Unique customers | Real people | Distinct `customer_unique_id` with an order | orders, customers | customer_analyzer | 96,096 | Verified (= SQL) |
| Repeat customers / % | Loyalty | People with > 1 distinct order | same | customer_analyzer | 2,997 / 3.12% | Verified (= SQL) |
| Customers by state | Where demand is | Distinct people per `customer_state` | customers | customer_analyzer | SP 40,302 … (sum 96,136) | Verified (CLI = API) |
| Top customers by spending | Biggest buyers | Σ price per person | items, orders, customers | customer_analyzer | CLI only, **never in the API** | Verified (CLI) |
| Data period | Time covered | Min/max purchase timestamp | `order_purchase_timestamp` | service · `_purchase_date_range` | 2016-09-04 → 2018-10-17 | Verified |

**Definition notes**
- "Late" compares exact timestamps. Every estimated date is at midnight, so an order delivered later on the estimated day counts as late. That covers **1,292** of the 7,826 late orders (recounted 29 Oct 2026).
- Customers by state adds up to 96,136, 40 more than the unique customers, because a few people ordered from more than one state and are counted in each (40 extra state entries in total). The dashboard says so in a footnote.

---

## 7. SQL and database

| Item | Value |
|---|---|
| Engine | SQLite via Python's `sqlite3` (no server) |
| File | `data/processed/opsiq.db` (~98 MB). **Not in Git** (`.gitignore`) |
| Created by | `python -m src.database build` (manual; never automatic) |
| Schema | `sql/schema.sql` |
| Used by the API or dashboard? | **No.** The CLI only (`query`, `late`, `verify`) |
| On a new PC | Rebuild it (about 20 s). Needs the sellers CSV |

### Tables (row counts in the current database, 29 Oct 2026)

| Table | Rows | Primary key | Foreign keys | Notable columns / types |
|---|---:|---|---|---|
| `customers` | 99,441 | `customer_id` | — | `customer_unique_id` TEXT NOT NULL, `customer_state` TEXT |
| `sellers` | 3,095 | `seller_id` | — | city, state, zip TEXT |
| `category_translations` | 71 | `product_category_name` | — | English name TEXT NOT NULL |
| `products` | 32,951 | `product_id` | none (on purpose) | category TEXT; measurements INTEGER |
| `orders` | 99,441 | `order_id` | `customer_id` → customers | status TEXT NOT NULL; 5 timestamps TEXT |
| `order_items` | 112,650 | (`order_id`, `order_item_id`) | → orders, products, sellers | `price` / `freight_value` REAL NOT NULL, CHECK ≥ 0 |
| `order_payments` | 103,886 | (`order_id`, `payment_sequential`) | → orders | `payment_type` TEXT, `payment_value` REAL |

Indexes: `customers.customer_unique_id`, `orders.customer_id`, `orders.order_status`, `order_items.product_id`, `order_items.seller_id`, `order_payments.payment_type`.

### Loading (`build_database`)

1. Delete any old `opsiq.db.building`, create it, and run `schema.sql`.
2. Turn on foreign keys. In **one transaction**, import the tables in dependency order (customers, sellers, translations, products, orders, items, payments).
3. For each CSV: check every schema column exists; convert values (empty → `NULL`, `INTEGER` → `int`, `REAL` → `float`); insert with `?` parameters and `ON CONFLICT DO NOTHING` (duplicates are skipped and counted).
4. Any bad value or broken foreign key stops the build with `file, line N: error`; the temporary file is deleted and the old database is kept.
5. On success, `os.replace` swaps the new file in.

### Queries (`sql/queries/`, all run successfully on 29 Oct 2026)

| Query | What it calculates (plain English) | Result highlights | Compared with Python by `verify`? |
|---|---|---|---|
| `orders_by_status` | Count orders in each status, biggest first | delivered 96,478 | ✅ |
| `delivery_performance` | Same rules as `delivery_analyzer`, using `julianday()` to get delays in days | 96,470 / 88,644 / 7,826 … | ✅ (9 values) |
| `late_deliveries` | The 10 most delayed delivered orders | 188.98 days at the top | No (matches the API by eye) |
| `late_deliveries_by_month` | For each estimated-delivery month: delivered, late, late % | e.g. 2017-05: 7.98% late | No (no Python equivalent) |
| `revenue_by_category` | Revenue and items per category (English name, else Portuguese, else "unknown"), top 10 | health_beauty first | ✅ (10 rows) |
| `repeat_customers` | Unique people, people with > 1 order, % | 96,096 / 2,997 / 3.12 | ✅ |
| `orders_per_customer` | How many people placed 1, 2, 3 … orders | 93,099 people placed 1 order; 1 person placed 17 | No |

Plus `find_late_orders(min_days_late, limit)` (`python -m src.database late ...`): a **parameterised** query, so user input can never become SQL.

**SQL vs Python testing:** `verify` compares 33 values on the full data (**33/33 match**, 29 Oct 2026). `test_sql_agrees_with_python_analytics` does the same on sample data in the automated tests.

---

## 8. Frontend and dashboard

| Item | Value |
|---|---|
| Framework | React 19.3.1 (installed), built with Vite 8.3.5 |
| Entry point | `index.html` → `src/main.jsx` → `App.jsx` |
| Pages | **One page**; no router. The header links jump to sections |
| Styling | Plain CSS (`src/index.css`), CSS variables for colours, system fonts |
| Charts | Hand-made HTML bars (`BarList`, `ProportionBar`); **no chart library** |
| Responsive | CSS breakpoints at 1080, 860, and 760 px. Desktop verified; phone layout **not verified** in this audit |
| Dark mode | Automatic via `prefers-color-scheme`; no toggle. **Not verified** in this audit |
| Accessibility | Skip link, `aria-label`s, keyboard-focusable bar rows and tables, values printed as text, reduced-motion support |
| Environment | `VITE_API_BASE_URL` (default `http://127.0.0.1:8000`) |
| Commands (`frontend`) | `npm run dev`, `npm run build`, `npm run preview`, `npm test`, `npm run test:watch`, `npm run lint` |

### Sections

| Section (id) | Shows | Endpoint | Interaction / states |
|---|---|---|---|
| Header | Data period and "Analytics calculated …" | `/dataset-info` | Hidden until loaded |
| Order summary (`summary`) | 4 KPI cards: total, delivered, delivered share, late | `/summary` | Loading / error + retry |
| Delivery performance (`delivery`) | On-time vs late bar; 4 delay cards; late orders in 3 delay bands | `/delivery-performance` | Empty state if nothing was analysed |
| Orders not delivered (`order-status`) | Bars for every status except delivered | `/orders-by-status` | Empty state if all were delivered. **Not in the header nav** |
| Delivery exceptions (`exceptions`) | Table: rank, order ID, estimated, actual, days late, severity (Minor ≤ 3, Major > 3, Severe > 7) | `/delivery-exceptions?limit=` | **Dropdown: 10/25/50/100 rows** (the only interactive control) |
| Sales and payments (`sales`) | 4 cards (revenue, freight, orders with items, average); payments by method | `/sales` | — |
| Products and categories (`products`) | 2 cards; top 10 categories by revenue; expandable top-10 products table | `/products` | Expand/collapse (`<details>`) |
| Customers (`customers`) | 3 cards; top 10 states plus "Other states (17)" | `/customers` | Empty state |

**No filters** (date, state, category) exist. **Browser check, 29 Oct 2026:** with the real API, Edge at 1400 px showed every section with the expected numbers and no error messages.

---

## 9. Dependencies

| Area | Declared in | Packages | Pinned? |
|---|---|---|---|
| Version 1 + database + download | — | Python standard library only | n/a |
| Backend | `backend/requirements.txt` | `fastapi==0.162.0`, `uvicorn==0.54.0`, `httpx2==2.16.0` (tests only) | Top level yes; sub-dependencies (pydantic 2.14.1, starlette 1.10.0, …) are not pinned |
| Frontend | `frontend/package.json` + `package-lock.json` | react, react-dom; dev: vite, @vitejs/plugin-react, vitest, jsdom, @testing-library/*, oxlint, @types/* | Yes, through the lock file |
| Runtime | `.python-version`, CI | Python 3.14; Node 24 (CI) | — |

---

## 10. Git, GitHub, and CI

| Item | Value (29 Oct 2026) |
|---|---|
| Repository | https://github.com/SwomBR/OpsIQ (public) |
| Branches | `main` only (local and remote) |
| Current commit | `ac32a9d` "Record first passing CI run in README and handover" |
| Sync | Local `main` = `origin/main` (checked with `git fetch`) |
| Working tree before this audit's documentation | Clean; no untracked files |
| Commits | 15 in total (26–29 Oct 2026) |
| Merge conflicts | None |
| CI | `.github/workflows/ci.yml`; runs #1 and #2 **passed** |
| Ignored | `data/raw/`, `data/processed/*.db`, `.venv/`, `node_modules/`, `frontend/dist/`, `__pycache__/`, `.env*` (except `.env.example`), `.vscode/`, coverage/log files |

Recent history:

```text
ac32a9d Record first passing CI run in README and handover
e2c2357 Add project handover document
bfb13cc Add CI workflow, Render deployment plan, dataset download, and docs
f151e2e Add React dashboard with tests
bf26fc9 Add optional SQLite database, example SQL queries, and verify tool
9926a48 Add FastAPI backend with analytics endpoints, caching, and tests
13e8c68 Split order and delivery analytics into reusable calculate functions
8153b0f Make OpsIQ portable, standardize module execution, and finish docs
...
96c0de1 Initial commit: OpsIQ business operations platform
```

**Secrets:** none found. A search for keys, tokens, and passwords found only comments and test strings (for example a fake "secret details" error message in a test). No `.env` files exist.

---

## 11. Deployment status

| Item | Status | Evidence |
|---|---|---|
| Backend deployment | **Configured but not deployed** | `render.yaml` service `opsiq-api`; the default URL `opsiq-api.onrender.com` did not respond (29 Oct 2026) |
| Frontend deployment | **Configured but not deployed** | `render.yaml` static site `opsiq-dashboard`; the default URL returned 404 |
| Database hosting | **Not needed / not started** | The API reads CSVs; SQLite is local-only |
| Dataset in production | **Configured** | Build command runs `python -m src.download_data` (download verified locally) |
| Environment variables | **Configured** | `OPSIQ_ENV`, `OPSIQ_DATA_DIR`, `OPSIQ_PRELOAD_DATA`, and `OPSIQ_CORS_ORIGINS` / `VITE_API_BASE_URL` (both `sync: false`, entered in Render) |
| Build / start commands | **Configured** | In `render.yaml`; build and start were tested locally only |
| Health check | **Implemented locally** | `healthCheckPath: /api/v1/health`; the endpoint is verified |
| CORS | **Implemented locally** | Verified allowed and blocked origins |
| Public URLs | **None** | — |
| GitHub Actions | **Deployed and verified** | Runs #1 and #2 succeeded |
| Render account / Blueprint | **Not started** (needs the owner's account) | — |
| Python 3.14 on Render | **Not verified** | Render reads `.python-version`; support for 3.14 was not checked |

Steps: [DEPLOYMENT.md](DEPLOYMENT.md).

---

## 12. AI functionality

**There is no AI, machine-learning, or LLM functionality in OpsIQ today.**

Evidence: no AI or ML packages in `backend/requirements.txt` or `frontend/package.json`; no imports of model or AI client libraries anywhere in `src/`, `backend/`, or `frontend/src`; no API keys or AI settings. Every number comes from rule-based Python and SQL. The README states this openly.

"AI-Powered" is the long-term goal from the original master plan, which says: *"AI is a later capability, not a shortcut around clean data."*

**Proposals (not implemented)**, in a sensible order:

| Proposal | What it would do | Needs | Guardrails |
|---|---|---|---|
| Rule-based anomaly flags | Flag months or states whose late rate is far above normal | No AI; SQL/Python only | Show the baseline and the period |
| Simple forecast | Predict next month's order volume | A small time-series model or a naive baseline | Compare with the naive baseline (MAE) |
| AI management briefing | A short written summary of the current metrics | An LLM API, an API key on the **backend only**, a cost per request | Send aggregate metrics only (never customer rows); label it as generated; show the facts next to it |
| Natural-language questions | "Which state has the most late orders?" mapped to approved queries | An LLM + fixed query templates | Never let the model run arbitrary SQL; test with known answers |

---

## 13. Risks and technical debt

| # | Issue | Severity | Evidence | Impact | Recommended action |
|---|---|---|---|---|---|
| 1 | Not deployed | Medium | No public URL; Render not set up | Reviewers cannot try the app | Deploy with `DEPLOYMENT.md` |
| 2 | Depends on Kaggle's anonymous download | Medium | `download_data.DATASET_URL`; worked 29 Oct 2026 | New PC or deploy build fails if Kaggle changes | Keep the manual fallback; keep a private copy of the CSVs |
| 3 | Dataset licence CC BY-NC-SA 4.0 | Medium (legal) | README, footer | No commercial use; credit Olist; share-alike | Never commit the data; keep the attribution; don't sell it |
| 4 | "AI-Powered" name but no AI | Medium (credibility) | §12 | Interviewers may ask | Explain openly (the README already does); build AI only after deploying |
| 5 | Python 3.14 is very new | Medium (deployment) | `.python-version`, CI | A host may not support it yet | Check Render's supported versions; fall back to 3.12/3.13 and test |
| 6 | No browser E2E tests or coverage in CI | Medium | `TESTING_GUIDE.md` | UI regressions could pass CI | Add Playwright; measure coverage |
| 7 | Mobile layout and dark mode not re-verified | Low | This audit | Possible phone layout problems | Manual check (TESTING_GUIDE §6) |
| 8 | Duplicate date/delivery logic in 2–3 places | Low | §5 | A rule change might be made in one place only | Shared helper; tests already guard the numbers |
| 9 | Module CLIs use relative paths | Low | sales/product/customer `__main__` | Fail outside the project root | Use `RAW_DATA_DIR` |
| 10 | Inconsistent empty-price handling | Low | sales vs customer analyser | Different behaviour with bad data | One rule |
| 11 | No column check on CSV load (Python path) | Low | analysers use `row["col"]` | Renamed column → `KeyError` → generic 500 | Validate headers on load |
| 12 | Invalid `limit` returns 503 when data is missing | Low | Seen 29 Oct 2026 | Confusing only during a data outage | Optional |
| 13 | "Late" = after midnight of the estimated day | Low (interpretation) | 1,292 orders | Late rate may look higher than a "by date" rule | Documented; could add a "by calendar day" metric |
| 14 | No authentication or rate limiting | Low now / High with private data | API reference | Anyone can call a deployed API | Fine for public aggregates; add auth before private data |
| 15 | Memory and warm-up on free hosting | Low–Medium | ~11 s warm-up; ~165 MB (historical) | Slow first visit; a host with too little memory | Measure memory before deploying |
| 16 | CLI prints top customers by spending | Low | business_report | Shows person-level (anonymised) IDs | Fine for anonymised public data; remove before using real data |
| 17 | `httpx2` (test-only) is installed in production | Low | requirements.txt | Slightly bigger deploy | Optional `requirements-dev.txt` |
| 18 | Sub-dependencies not pinned (backend) | Low | requirements.txt | A future install could differ | Optional lock file (`pip freeze`) |
| 19 | No `.gitattributes`; CRLF warnings | Low | git output | Noise only | Optional `.gitattributes` |
| 20 | Header nav has no link to "Orders not delivered" | Low (UX) | `Header.jsx` | Minor | Add the link |
| 21 | Plan vs reality gap | Info | §14 | The master plan describes PostgreSQL/Power BI | Update the plan or note the decisions |

**Security summary:** no secrets in the repository; read-only API; parameterised SQL; errors don't leak paths; the API never returns customer-level data; CORS limited to known origins.

---

## 14. Original plan vs what was built

The original plan is `docs/AI_Powered_Business_Operations_Intelligence_Platform_Master_Plan_v1.docx` (15 Oct 2026, "provisional"). The project changed direction in several places:

| Master plan | Actually built | Comment |
|---|---|---|
| Synthetic operational data (tickets, SLAs, employees) | Real public Olist e-commerce data | More realistic; licence limits commercial use |
| PostgreSQL warehouse | Optional SQLite | Simpler, free, no server; PostgreSQL not started |
| Power BI dashboard | React dashboard | More engineering-focused; Power BI not started |
| Pipeline run audit trail (run ID, row counts) | Not built (database build prints counts only) | Not started |
| Docker | Not built | Not started |
| FastAPI service layer | Built | Done |
| Anomaly flags, forecasting, AI assistant | Not built | Not started (proposals in §12) |
| CI, tests, documentation | Built | Done |

Treat the master plan as a historical vision document. This reference describes the real system.
