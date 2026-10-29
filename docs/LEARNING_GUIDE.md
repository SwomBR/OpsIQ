# OpsIQ Learning Guide

Each section explains one concept using real code from this project. Open the file, find the example, and try the exercise. The goal is that you can explain every part of OpsIQ in your own words.

**Contents:** [Explaining OpsIQ](#explaining-opsiq) · [What each part is for](#what-each-part-is-for) · [Study order](#study-order) · [Part 1 — Python](#part-1--python) · [Part 2 — API](#part-2--the-api-backend) · [Part 3 — Dashboard](#part-3--the-dashboard-frontend) · [Part 4 — SQL](#part-4--sql) · [Part 5 — Quality and delivery](#part-5--quality-and-delivery) · [Part 6 — Deployment](#part-6--deployment-concepts) · [Real code vs only mentioned](#concepts-in-real-code-vs-only-mentioned) · [Before you change code](#before-you-change-code) · [Interview questions](#interview-questions-about-opsiq) · [What to learn next](#what-to-learn-next)

---

## Explaining OpsIQ

Three versions of the same story. They describe only what exists today (29 Oct 2026).

### Short (interview, about 30 seconds)

> OpsIQ is an operations analytics platform I built on a real public dataset of about 100,000 Brazilian e-commerce orders. A Python engine calculates delivery punctuality, late-order exceptions, sales, product, and customer metrics; a FastAPI backend serves them as a cached REST API; and a React dashboard displays them. There's also an optional SQLite layer whose SQL results are checked against the Python results. It has 191 automated tests and runs CI on GitHub Actions.

### Technical (about 2 minutes)

> The business rules live in one place, a set of plain Python modules using only the standard library. They read the CSV files with `csv.DictReader`, parse timestamps with `datetime`, and return dictionaries. I kept calculation and printing separate, so the original command-line report and the API call the same functions and can't disagree; a backend test checks that.
>
> The FastAPI backend adds the project root to the import path and calls those functions through a service layer. Results are cached in memory with `lru_cache` and a lock, so concurrent first requests do one calculation. A background thread warms the cache at startup: about 11 seconds, then responses take around 5 ms. Routes get their data through `Depends`, which also lets tests inject sample data. Pydantic response models define every field, which is how I guarantee customer-level data never leaves the API. Errors are mapped deliberately: a missing file is a 503 that names only the file, bad data is a 500 with no stack trace, and invalid parameters are a 422. CORS allows only the dashboard's origin and only GET.
>
> The React dashboard has seven independent sections. Each uses a custom `useApi` hook that tracks loading, error, and data, cancels stale requests with `AbortController`, and offers a retry, so one failing endpoint doesn't blank the page. The charts are accessible HTML rather than a chart library.
>
> For SQL, I load the CSVs into SQLite with primary and foreign keys, inside one transaction written to a temporary file, so a failed build never corrupts the old database. A `verify` command compares 33 SQL results with the Python results, and they all match.
>
> Testing is `unittest` for Python and the API, and Vitest with Testing Library for React: 89, 61, and 41 tests. None of them need the real dataset, so GitHub Actions runs them all without downloading anything. Deployment to Render is configured but not live yet, and the "AI" part is planned, not built.

### Non-technical (for someone outside IT)

> Online shops collect a lot of data about orders, but it's just huge spreadsheets. I built a tool that reads about 100,000 real orders and answers practical questions: how many arrived on time, which ones were very late and need checking, which product types make the most money, and how many customers come back. It shows the answers on a web page with clear numbers and charts, and I wrote automatic checks to make sure the numbers are right.

**Be honest about the gaps if asked:** there is no AI yet; it is not deployed yet; it uses SQLite, not a production database server; and the data is static (2016–2018).

---

## What each part is for

| Part | In one sentence |
|---|---|
| `src/` analytics engine | The "brain": turns CSV rows into numbers using business rules. |
| `business_report.py` | Prints all the numbers in the terminal. |
| `data_validator.py` | Checks the data for problems before we trust it. |
| `backend/` API | Lets other programs (like the dashboard) ask for the numbers over the web. |
| `analytics_service.py` | Loads the data once, remembers the results, and hands them to the API. |
| `schemas.py` | Describes exactly what each API answer looks like. |
| `frontend/` dashboard | The web page managers would look at. |
| `useApi.js` | Fetches data for one section and remembers if it is loading, finished, or failed. |
| `sql/` + `database.py` | The same data in a real database, so it can be queried with SQL. |
| `download_data.py` | Fetches the dataset so a new computer or server can get it. |
| `tests/`, `backend/tests/`, `*.test.js*` | Automatic checks that the code still gives the right answers. |
| `.github/workflows/ci.yml` | Runs every test on GitHub after each push. |
| `render.yaml` | Instructions for a hosting company to run the app online. |

---

## Study order

From beginner to more advanced. Study each file with the matching section of this guide open.

| Step | Study | Files | You are ready to move on when you can… |
|---|---|---|---|
| 1 | Reading data | `src/data_loader.py` | explain `PROJECT_ROOT` and what `DictReader` returns |
| 2 | A simple metric | `src/data_analyzer.py` | count statuses by hand for 3 sample rows |
| 3 | Dates and rules | `src/delivery_analyzer.py`, `src/delivery_exceptions.py` | explain why 8 orders are skipped and what "late" means |
| 4 | Grouping | `src/sales_analyzer.py`, `src/product_analyzer.py`, `src/customer_analyzer.py` | explain `defaultdict` and `customer_id` vs `customer_unique_id` |
| 5 | Data quality | `src/data_validator.py` | name the seven checks |
| 6 | Putting it together | `src/business_report.py` | trace one number from the CSV file to the printed line |
| 7 | Python tests | `tests/test_delivery_analyzer.py` | write a new test with your own sample rows |
| 8 | SQL basics | `sql/schema.sql`, `sql/queries/orders_by_status.sql` | explain primary vs foreign key |
| 9 | SQL joins and CTEs | `sql/queries/repeat_customers.sql`, `revenue_by_category.sql` | explain `LEFT JOIN` and `WITH` |
| 10 | Database code | `src/database.py` (`build_database`, `find_late_orders`) | explain transactions and `?` parameters |
| 11 | API basics | `backend/app/main.py`, `api/routes.py` | explain a route and a status code |
| 12 | API data and errors | `api/analytics.py`, `services/analytics_service.py`, `schemas.py` | explain `Depends`, the cache, and 503 vs 500 |
| 13 | API tests | `backend/tests/test_analytics_api.py` | explain `dependency_overrides` |
| 14 | React basics | `frontend/src/App.jsx`, `components/StatTile.jsx`, `sections/SummarySection.jsx` | explain components and props |
| 15 | React data | `api/client.js`, `hooks/useApi.js`, `components/AsyncContent.jsx` | explain `useEffect`, `useState`, and loading/error states |
| 16 | Interaction | `sections/ExceptionsSection.jsx` | explain why `useCallback` is needed |
| 17 | Frontend tests | `src/utils/transform.test.js`, `src/App.test.jsx` | explain mocking `fetch` |
| 18 | CI and deployment | `.github/workflows/ci.yml`, `render.yaml`, `docs/DEPLOYMENT.md` | explain build vs start command, and why CI needs no data |

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

---

## Part 6 — Deployment concepts

These are **configured** in OpsIQ but not yet used on a real host.

- **Web service vs static site.** The API is a program that must keep running (a web service). The dashboard, after `npm run build`, is just files (a static site) that any web server can send.
- **Build command vs start command.** The build runs once per deploy (install packages, download data, build files). The start command runs the program. See [render.yaml](../render.yaml).
- **Environment variables in production.** The same code runs locally and online; only settings change (`OPSIQ_CORS_ORIGINS`, `VITE_API_BASE_URL`).
- **Build-time vs run-time variables.** `VITE_API_BASE_URL` is copied into the JavaScript at build time, so changing it requires a rebuild. `OPSIQ_*` variables are read when the API starts.
- **Health check.** The host calls `/api/v1/health` to see whether the service is alive. It deliberately doesn't read the data, so it stays fast.
- **Try:** read [DEPLOYMENT.md](DEPLOYMENT.md) and explain why the two services need each other's URL.

---

## Concepts in real code vs only mentioned

So you know what you can show in the code and what is only an idea.

| Concept | In real code? | Where |
|---|---|---|
| Modules, packages, `python -m` | ✅ | `src/` |
| CSV reading, `datetime` parsing | ✅ | `data_loader.py`, `delivery_analyzer.py` |
| `defaultdict`, sets, sorting with `key=` | ✅ | `product_analyzer.py`, `customer_analyzer.py` |
| Dataclasses | ✅ | `analytics_service.OrderMetrics`, `config.Settings`, `database.ImportResult` |
| `argparse` command-line tools | ✅ | `database.py`, `download_data.py` |
| Threads and locks | ✅ | `main.py` (warm-up thread), `analytics_service._cache_lock` |
| Caching (`lru_cache`) | ✅ | `analytics_service.py` |
| REST, status codes, CORS, Pydantic, `Depends` | ✅ | `backend/app/` |
| React components, props, hooks, custom hook | ✅ | `frontend/src/` |
| `AbortController` (cancelling requests) | ✅ | `client.js`, `useApi.js` |
| Accessibility (ARIA labels, skip link) | ✅ | `App.jsx`, `BarList.jsx` |
| SQL DDL, keys, indexes, joins, CTEs, `GROUP BY` | ✅ | `sql/` |
| Transactions, parameterised queries | ✅ | `database.py` |
| Unit tests, API tests, mocking | ✅ | all test folders |
| CI (GitHub Actions) | ✅ (running) | `.github/workflows/ci.yml` |
| Deployment (Render) | ⚙️ Configured only | `render.yaml` |
| Authentication, rate limiting | ❌ Only mentioned | README "Limitations" |
| Redis or another external cache | ❌ Only mentioned (as "not needed") | ARCHITECTURE.md |
| PostgreSQL, Power BI, Docker | ❌ Only in the original master plan | `.docx` |
| AI / LLM / machine learning | ❌ Only planned | Roadmap |
| Browser end-to-end tests | ❌ Not in the repository | Roadmap |
| Code coverage | ❌ Not set up | TESTING_GUIDE.md |

---

## Before you change code

1. **Run all three test suites first**, so you know they passed before your change.
2. **Business rules live in `src/` only.** If a number is wrong, fix it there, not in the API or the dashboard.
3. **The CLI report, API, and SQL must agree.** After changing a rule, run `python -m src.database verify` and the backend test `TestReportsAgreeWithVersion1`.
4. **Changing an API field?** Update `schemas.py`, the service function, the frontend section, the tests, and [API_REFERENCE.md](API_REFERENCE.md).
5. **Don't put customer-level data in API responses.** The schemas are the guard.
6. **Never commit** the dataset, the `.db` file, `.env` files, `.venv`, or `node_modules`.
7. **Restart the API** after changing data or backend code (`--reload` handles code, not data).
8. **Small commits**, one idea each, with a message that says why.

---

## Interview questions about OpsIQ

Concepts you need for each answer are in brackets.

**Project and design**
1. Walk me through OpsIQ from the CSV file to the dashboard. *(data flow, layers)*
2. Why did you keep business logic out of the API? *(separation of concerns, reuse, testing)*
3. How do you know the numbers are correct? *(hand-calculated test values, CLI = API test, SQL `verify` 33/33)*
4. What is the hardest data-quality issue in the dataset, and how do you handle it? *(missing delivery dates are skipped and counted; out-of-order timestamps are reported)*
5. How do you define a "late" order? What are the weaknesses of that definition? *(timestamp comparison; 1,292 same-day cases)*
6. Why `customer_unique_id` and not `customer_id`? *(one ID per order vs per person)*
7. The name says AI-Powered. Where is the AI? *(honest: planned, not built; why data quality comes first)*

**Backend**
8. How does caching work, and how is it invalidated? *(`lru_cache`, lock, restart, errors not cached)*
9. What happens if two requests arrive while the cache is empty? *(lock, one calculation)*
10. Why 503 for a missing file but 500 for bad data? *(temporary unavailability vs server failure)*
11. What does CORS protect against? What doesn't it protect against? *(browser same-origin policy; not authentication)*
12. How do your tests avoid the real dataset? *(`dependency_overrides`, temporary CSVs)*
13. How would you scale this to millions of orders? *(database instead of CSV, pre-computed tables, pagination, multiple workers with a shared cache)*

**Frontend**
14. Why does each section load separately? *(independent failures, `useApi`)*
15. Why wrap `load` in `useCallback` in `ExceptionsSection`? *(stable function identity, avoiding endless requests)*
16. Why no chart library? *(fewer dependencies, accessibility, values as text)*
17. Why must `VITE_API_BASE_URL` never contain secrets? *(copied into public JavaScript)*

**SQL**
18. Explain your schema's keys and why products has no foreign key to translations. *(PK/FK, two untranslated categories)*
19. How do you prevent SQL injection? *(`?` parameters, a whitelist of query names)*
20. How does the build avoid leaving a broken database? *(temporary file, one transaction, `os.replace`)*

**Process**
21. What does your CI pipeline do, and why doesn't it need the dataset? *(two jobs; tests use sample data)*
22. What would you do differently, or next? *(deploy, E2E tests, remove duplicated date logic, filters, then AI with guardrails)*

---

## What to learn next

Matched to the roadmap, in a sensible order:

1. **Deployment** on Render: environment variables, logs, and debugging a failed build.
2. **Browser end-to-end testing** with Playwright.
3. **Test coverage** with `coverage.py`, and how to read a coverage report.
4. **PostgreSQL**: the same schema on a real database server (connects to the original plan).
5. **Query parameters and filtering** in FastAPI (for date and state filters).
6. **Docker basics**: packaging the API so it runs the same everywhere.
7. **Working with an LLM API safely**: keys on the server, sending only aggregates, labelling generated text, cost limits.
