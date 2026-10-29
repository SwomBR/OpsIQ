# OpsIQ Learning Guide

Each section explains one concept using real code from this project. Open the file, find the example, and try the exercise. The goal is that you can explain every part of OpsIQ in your own words.

---

## Part 1 — Python

### Modules and imports

A **module** is one `.py` file. A **package** is a folder of modules (`src/`). `import` lets one file use another file's functions.

- **Example:** [src/business_report.py](../src/business_report.py) starts with `from src.delivery_exceptions import find_delivery_exceptions`.
- **Why `python -m src.business_report`?** `-m` runs the file *as part of the `src` package*, so `from src...` imports work. `python src/business_report.py` runs it as a loose file and Python cannot find `src`.
- **Try:** run `python src/business_report.py` and read the error, then run it with `-m`.

### Functions and return values

A function takes inputs (parameters) and gives back a result with `return`. Functions that **return** data are easier to reuse and test than functions that only **print**.

- **Example:** [src/delivery_analyzer.py](../src/delivery_analyzer.py) has `calculate_delivery_performance(orders)`, which *returns* a dictionary, and `analyze_delivery_performance(orders)`, which *prints* it. The API reuses the first; the CLI uses the second.
- **Try:** explain why the API could not reuse a function that only prints.

### CSV processing

`csv.DictReader` turns each CSV row into a dictionary whose keys are the header names. Every value is a string.

- **Example:** [src/data_loader.py](../src/data_loader.py) `open_order()`. `encoding="utf-8-sig"` removes an invisible marker some editors put at the start of files.
- **Try:** in a Python shell, `from src.data_loader import open_order; orders = open_order(); orders[0]`.

### Data validation

Real data has gaps and errors. Validation finds them *before* you trust the numbers.

- **Example:** [src/data_validator.py](../src/data_validator.py) checks for missing IDs, duplicates, unknown statuses, unreadable dates, and steps recorded out of order. `parse_order_date()` returns `None` for bad dates instead of crashing.
- **Try:** run `python -m src.data_validator` and explain one issue it reports.

### Business analytics

Turning a business question into a precise rule. "How many orders were late?" needs decisions: only delivered orders? What if a date is missing? Late by the date or by the minute?

- **Example:** `find_delivery_exceptions()` in [src/delivery_exceptions.py](../src/delivery_exceptions.py): delivered status only, both dates present and valid, delay greater than zero seconds.
- **Try:** read [Metric definitions](../README.md#key-results) and explain why 1,292 orders count as late even though they arrived on the estimated day.

---

## Part 2 — The API (backend)

### REST APIs, HTTP methods, and JSON

An **API** lets programs ask another program for data. A **REST** API uses web addresses (URLs) for things and HTTP **methods** for actions: `GET` reads, `POST` creates, `PUT` updates, `DELETE` removes. OpsIQ only reads, so it only uses `GET`. **JSON** is the text format of the answers: `{"total_orders": 99441}`.

- **Try:** start the API and open http://127.0.0.1:8000/api/v1/analytics/summary in your browser.

### HTTP status codes

A number that says how the request went.

| Code | Meaning | OpsIQ example |
|---|---|---|
| 200 | OK | Any successful request |
| 404 | Not found | `/api/v1/analytics/nothing` |
| 422 | Your input is invalid | `delivery-exceptions?limit=0` |
| 500 | The server failed | A CSV file with a broken number |
| 503 | Temporarily unavailable | A CSV file is missing |

- **Example:** `_load()` in [backend/app/api/analytics.py](../backend/app/api/analytics.py) chooses 503 or 500.
- **Try:** request `?limit=abc` and read the 422 explanation.

### FastAPI routes and dependencies

A **route** connects a URL to a Python function. A **dependency** is something a route needs, supplied by FastAPI.

- **Example:** `@router.get("/summary")` above `get_business_summary(metrics: OrderMetrics)`. The type `OrderMetrics` is `Annotated[..., Depends(get_order_metrics)]`, so FastAPI calls `get_order_metrics()` first and passes the result in.
- **Why dependencies?** Tests can swap them: `app.dependency_overrides[get_order_metrics] = ...` in [backend/tests/test_analytics_api.py](../backend/tests/test_analytics_api.py) serves sample data instead of the real files.
- **Try:** explain how a test checks `/summary` without the Olist files.

### Pydantic response schemas

A **schema** describes the exact shape of a response. FastAPI uses it to check the data, drop any field not listed, and generate `/docs`.

- **Example:** `class Customers(BaseModel)` in [backend/app/schemas.py](../backend/app/schemas.py) has no `top_customers` field, so individual customers can never appear in the response even though the Version 1 report calculates them.
- **Try:** open http://127.0.0.1:8000/docs and find the `Customers` schema.

### Environment variables and configuration

Settings that change between computers (local vs hosted) are read from **environment variables** instead of being written in the code.

- **Example:** [backend/app/config.py](../backend/app/config.py) reads `OPSIQ_CORS_ORIGINS`, `OPSIQ_DATA_DIR`, and others, with safe defaults. `load_settings(environ)` takes a dictionary so tests can try different values.
- **Try:** in PowerShell, `$env:OPSIQ_LOG_LEVEL = "DEBUG"`, start the server, and compare the log.

### CORS

Browsers block a web page from reading responses from a *different* address (origin) unless that server says it is allowed. The dashboard (`localhost:5173`) and the API (`127.0.0.1:8000`) are different origins. **CORS** headers are the API's permission slip.

- **Example:** `CORSMiddleware` in [backend/app/main.py](../backend/app/main.py) allows only the origins in `OPSIQ_CORS_ORIGINS`, and only `GET`.
- **Important:** CORS protects *browser users*; it is not authentication. `curl` ignores it.
- **Try:** read `TestCors` in [backend/tests/test_config.py](../backend/tests/test_config.py).

### Caching

Remembering a result so it does not have to be calculated again.

- **Example:** `@lru_cache(maxsize=1)` on `_order_metrics_for()` in [backend/app/services/analytics_service.py](../backend/app/services/analytics_service.py). First request: a few seconds. Later requests: ~5 ms. The `_cache_lock` makes simultaneous first requests share one calculation.
- **The hard part is invalidation** — knowing when the cached value is out of date. OpsIQ's rule is simple: the data only changes when the files change, so restart the server.
- **Try:** explain why errors must not be cached (see `test_failed_load_is_not_cached`).

---

## Part 3 — The dashboard (frontend)

### React components and props

A **component** is a function that returns what to show (JSX, which looks like HTML). **Props** are its inputs.

- **Example:** [frontend/src/components/StatTile.jsx](../frontend/src/components/StatTile.jsx): `StatTile({ label, value, note })`. `SummarySection` uses it four times with different props.
- **Try:** add a fifth tile to `SummarySection` showing "Not delivered" (`total_orders - delivered_orders`).

### State and hooks

**State** is data that can change and re-draw the component. **Hooks** (`useState`, `useEffect`, `useCallback`) are React functions for state and side effects.

- **Example:** [frontend/src/hooks/useApi.js](../frontend/src/hooks/useApi.js) is a custom hook. `useEffect` starts the request; `useState` stores the result; it returns `{ status, data, error, retry }`.
- **Example:** `ExceptionsSection` keeps the selected limit in `useState`. Changing it creates a new `load` function (`useCallback(..., [limit])`), which makes `useApi` fetch again.
- **Try:** explain why `load` must be wrapped in `useCallback` (hint: a new function on every render would start a new request on every render).

### API requests from the frontend

- **Example:** [frontend/src/api/client.js](../frontend/src/api/client.js). All requests go through `fetchJson()`, which builds the URL from `VITE_API_BASE_URL`, turns failures into readable `ApiError`s, and supports cancelling with an `AbortController`.
- **Why one file?** If the API address or error format changes, there is one place to fix.

### Loading, error, and empty states

Every request can be slow, fail, or return nothing. Each needs its own screen.

- **Example:** [frontend/src/components/AsyncContent.jsx](../frontend/src/components/AsyncContent.jsx). `ExceptionsTable` shows "No late deliveries were found." for an empty list.
- **Try:** stop the API while the dashboard is open, reload, then press "Try again" after restarting it.

---

## Part 4 — SQL

### Tables, keys, and relationships

A **table** stores one kind of thing. A **primary key** identifies each row uniquely. A **foreign key** says "this value must exist in that other table".

- **Example:** in [sql/schema.sql](../sql/schema.sql), `orders.customer_id REFERENCES customers (customer_id)`. `order_items` has a two-column primary key `(order_id, order_item_id)`.
- **Try:** build the database and run `python -m src.database query orders_per_customer`. Explain why it joins `orders` to `customers`.

### Queries, joins, and parameters

- **Example:** [sql/queries/revenue_by_category.sql](../sql/queries/revenue_by_category.sql) uses `LEFT JOIN`, `COALESCE`, `GROUP BY`, and `ORDER BY`.
- **SQL injection:** `find_late_orders()` in [src/database.py](../src/database.py) passes user values as `?` parameters. If values were pasted into the SQL text, input like `0; DROP TABLE orders` could become a command.
- **Try:** `python -m src.database late --min-days 100 --limit 3`.

---

## Part 5 — Quality and delivery

### Automated testing

A test runs code with known input and checks the output. Tests let you change code without fear.

- **Unit test:** one function — the test "splits late orders into bands that add up to the total" in [frontend/src/utils/transform.test.js](../frontend/src/utils/transform.test.js).
- **API test:** a full request — `TestSalesEndpoint` in [backend/tests/test_reports_api.py](../backend/tests/test_reports_api.py).
- **Regression test across interfaces:** `TestReportsAgreeWithVersion1` checks that the API and the CLI report print the same numbers.
- **Mocking:** replacing something real with a fake — `mockFetch()` in [frontend/src/test/mockApi.js](../frontend/src/test/mockApi.js) replaces the network.
- **Try:** change a number in a test, run it, and read the failure message. Then undo it.

### Git and GitHub

Git records versions of your files (**commits**). GitHub stores them online and runs CI.

- [.gitignore](../.gitignore) keeps out what must never be committed: the dataset, virtual environments, `node_modules`, the generated database, and `.env` files.
- **Try:** `git status`, then `git check-ignore -v data/processed/opsiq.db`.

### CI/CD

**Continuous integration** runs every test automatically on every push. **Continuous deployment** publishes automatically after the tests pass.

- **Example:** [.github/workflows/ci.yml](../.github/workflows/ci.yml) has two jobs (Python and frontend). Render can redeploy on every push to `main` (see [DEPLOYMENT.md](DEPLOYMENT.md)).
- **Try:** after pushing, open the **Actions** tab on GitHub and read a job's log.

---

## Practise explaining

Say these out loud, in two or three sentences each, without notes:

1. What happens, step by step, between opening the dashboard and seeing "99,441"?
2. Why does the API reuse `src/` instead of having its own calculations?
3. Why are there both a 503 and a 500 error?
4. Why does the dashboard leave delivered orders out of the status chart?
5. What does CORS protect against, and what does it *not* protect against?
6. What is cached, when is it refreshed, and what would go wrong if errors were cached?
7. Why is the database optional, and how do you know its numbers are right?
8. What would you need to change before adding private company data?
