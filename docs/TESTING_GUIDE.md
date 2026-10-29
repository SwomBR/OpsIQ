# OpsIQ Testing Guide

How OpsIQ is tested, how to run each suite, the **actual** results, and what is not tested.

## Results at a glance

### New test run — 29 October 2026 (this audit)

Machine: Windows 11, Python 3.14.6, Node.js 24.18.0, npm 11.16.0. Commit `ac32a9d`.

| Suite | Framework | Discovered | Passed | Failed | Skipped |
|---|---|---:|---:|---:|---:|
| Version 1 + database + download (`tests/`) | `unittest` | 89 | 89 | 0 | 0 |
| Backend API (`backend/tests/`) | `unittest` + FastAPI `TestClient` | 61 | 61 | 0 | 0 |
| Frontend (`frontend/src/**/*.test.*`) | Vitest 5.0.5 + Testing Library | 41 | 41 | 0 | 0 |
| **Total** | | **191** | **191** | **0** | **0** |
| Frontend lint | oxlint | — | no problems | — | — |
| Frontend production build | Vite 8.3.5 | — | built | — | — |

### On GitHub (CI)

| Run | Commit | Result |
|---|---|---|
| #1 | `e2c2357` | ✅ success (both jobs) |
| #2 | `ac32a9d` | ✅ success |

### Earlier reports (historical, not from this run)

| Source | Claim | Status now |
|---|---|---|
| Early Version 1 notes | 54 tests | Superseded; the root suite now has 89 |
| Earlier progress report | "89 tests across backend and Version 1" | **Wrong split.** 89 is the root `tests/` suite alone; the backend adds 61 |
| README (before this audit) | 89 + 61 + 41 = 191 | ✅ Reproduced exactly |

**Coverage:** not measured. The `coverage` package is not installed, and no coverage settings exist.

---

## How to run the tests

### Everything (three terminals or one after another)

```powershell
# 1. Project root
python -m unittest discover -s tests -v

# 2. backend folder, virtual environment active
cd backend
.\.venv\Scripts\Activate.ps1
python -m unittest discover -s tests -v
cd ..

# 3. frontend folder
cd frontend
npm test
npm run lint
npm run build
cd ..
```

Success looks like `Ran 89 tests ... OK`, `Ran 61 tests ... OK`, and `Tests 41 passed (41)`.

**No test needs the Olist dataset.** Every test creates its own small sample data. That is also why CI works without the CSV files.

### One file or one test

```powershell
# project root
python -m unittest tests.test_delivery_analyzer -v
python -m unittest tests.test_delivery_analyzer.TestDeliveryAnalyzer -v   # one class (check the class name in the file)

# backend folder (venv active)
python -m unittest tests.test_reports_api -v

# frontend folder
npx vitest run src/utils/format.test.js
npm run test:watch          # re-runs tests when you save a file
```

---

## 1. Version 1 tests (`tests/`, 89)

Runs with the standard library only; no `pip install` needed.

| File | Tests | What it covers |
|---|---:|---|
| `test_data_validator.py` | 20 | Missing values, missing/duplicate IDs, invalid statuses, unreadable dates, out-of-order timestamps, delivered orders without delivery dates |
| `test_database.py` | 24 | SQLite build, type conversion, duplicates skipped, bad values reported with file/line, failed build keeps the old database, queries, parameterised `late` query, SQL vs Python agreement on sample data |
| `test_delivery_analyzer.py` | 8 | On-time/late counts, percentages, delays, skipped orders, empty input |
| `test_data_analyzer.py` | 6 | Status counts and the printed order report |
| `test_customer_analyzer.py` | 6 | Unique and repeat customers, spending, states |
| `test_product_analyzer.py` | 6 | Category revenue, translations, top products, missing categories |
| `test_delivery_exceptions.py` | 5 | Late orders found and sorted, invalid dates skipped |
| `test_sales_analyzer.py` | 5 | Revenue, freight, average, payment totals |
| `test_download_data.py` | 5 | Zip extraction (only requested files, nothing written outside the folder), incomplete archive, no download when files exist, failure exit code. The network call is mocked |
| `test_business_report.py` | 2 | Summary metrics in the combined report; empty dataset |
| `test_data_loader.py` | 2 | CSV loading; default path is inside the project |

## 2. Backend API tests (`backend/tests/`, 61)

Uses FastAPI's `TestClient` (needs `httpx2`, installed from `requirements.txt`). Real data files are replaced with sample data through `app.dependency_overrides` or temporary CSV folders.

| File / class | Tests | What it covers |
|---|---:|---|
| `test_api.py` · `TestApiEndpoints` | 7 | `/`, `/health`, 404, docs |
| `test_analytics_api.py` · `TestDataLoading` | 5 | Missing file → 503 without paths, broken file → 500 |
| · `TestDeliveryExceptions` | 6 | Sorting, `limit` defaults and 422 validation |
| · `TestEmptyDataset` | 4 | `null` percentages when there is no data |
| · `TestBusinessSummary`, `TestOrdersByStatus`, `TestAnalyticsRoutes`, `TestDeliveryPerformance` | 7 | Field values and shapes |
| `test_reports_api.py` · `TestCache` | 8 | Files read once, lock, failures not cached, `clear_cache()` |
| · `TestCustomersEndpoint` | 3 | Aggregates only, no individual customers |
| · `TestReportErrors` | 3 | Error handling for the sales/product/customer reports |
| · `TestSalesEndpoint`, `TestProductsEndpoint`, `TestDatasetInfoEndpoint` | 6 | Field values |
| · `TestReportsAgreeWithVersion1` | 1 | API numbers equal the CLI report's numbers |
| · `TestNewRoutesAreDocumented` | 1 | Routes appear in the OpenAPI schema |
| `test_config.py` · `TestLoadSettings` | 6 | Environment variables and defaults |
| · `TestCors` | 4 | Allowed and blocked origins |

## 3. Frontend tests (`frontend/src`, 41)

Vitest runs in a simulated browser (`jsdom`). `fetch` is mocked (`src/test/mockApi.js`), so no API is needed. Settings: `frontend/vite.config.js`.

| File | Tests | What it covers |
|---|---:|---|
| `utils/format.test.js` | 10 | Numbers, percentages, currency, days, dates, labels |
| `utils/transform.test.js` | 9 | Status items, delay bands, "Other" grouping, payments, categories, severity |
| `components/components.test.jsx` | 9 | StatTile, BarList, ProportionBar, AsyncContent states, exceptions table |
| `api/client.test.js` | 7 | Success, HTTP errors with `detail`, network failure, abort |
| `App.test.jsx` | 6 | Whole dashboard with a mocked API; error in one section; retry; limit selector |

## 4. Checks that are not unit tests

| Check | Command | Result on 29 Oct 2026 |
|---|---|---|
| SQL vs Python on the full data | `python -m src.database verify` (project root, after `build`) | ✅ 33 of 33 metrics match |
| CLI report on the full data | `python -m src.business_report` | ✅ Ran to `END OF OPSIQ REPORT` |
| Dataset download | `python -m src.download_data --data-dir <empty folder> --with-database-files` | ✅ 7 files in ~7 s, byte-identical to the local copies |
| Live API (all 10 routes) | `uvicorn` + `curl` | ✅ 200 with real data; 422/404/405 checked |
| API with an empty data folder | `OPSIQ_DATA_DIR=<empty>` | ✅ health 200, analytics 503 naming the file |
| Dashboard in a real browser | Edge (headless), 1400 px wide, real API | ✅ All 7 sections and the header showed real figures; 0 error messages |
| Dashboard on a phone-sized screen | Edge (headless), 390 px | ⚠️ **Not verified.** The screenshot was cut off on the right. Headless Edge has a minimum window width, so this may be a tool limit, not a bug. Check by hand (section 6). |
| Dark mode | — | ⚠️ Not verified in this audit |

---

## 5. Known gaps (untested or only manually tested)

| Gap | Risk | Suggested action |
|---|---|---|
| No browser end-to-end tests in the repository | A broken page could still pass unit tests | Add Playwright tests for the main page and run them in CI |
| No coverage measurement | Unknown untested lines | `pip install coverage`, then `python -m coverage run -m unittest discover -s tests` and `python -m coverage report` |
| `verify` (SQL vs Python on the full data) is manual | A change could make SQL and Python disagree unnoticed on real data | Run it before each release |
| Module CLIs (`python -m src.sales_analyzer`, and so on) are not tested | They use relative paths and only work from the project root | Use `RAW_DATA_DIR` like `business_report.py` |
| Real Kaggle download not in CI | Kaggle could change the endpoint | Keep the manual check; the fallback is a manual download |
| Mobile layout and dark mode not re-checked | Layout bugs on phones | Manual check (section 6) |
| No performance or memory tests | Free hosting has little memory | Measure memory after warm-up before deploying |
| Data-dependent quirk: invalid `limit` with missing data → 503 | Harmless | Optional: document or reorder the checks |

## 6. Manual dashboard check (5 minutes)

1. Start the API (`backend`: `uvicorn app.main:app --reload`) and wait about 15 seconds.
2. Start the dashboard (`frontend`: `npm run dev`) and open http://localhost:5173.
3. Compare with the expected figures: total orders **99,441**, delivered **96,478 (97.02%)**, late **7,826**, on time **91.89%**, revenue **R$13.59M**, unique customers **96,096**.
4. Change "Show 10 orders" to 25 in Delivery exceptions; the table should grow to 25 rows.
5. Press F12 → Console: there should be no red errors.
6. Press F12 → device toolbar (Ctrl+Shift+M) → choose a phone. Nothing should be cut off, and there should be no sideways scrolling.
7. Switch Windows to dark mode (Settings → Personalisation → Colours) and reload the page.
8. Stop the API and reload: every section should show "Could not reach the OpsIQ API…" with a "Try again" button.

## 7. Rules

- Never delete or weaken a test to make it pass. Find out why it fails.
- Expected values in tests are worked out by hand, not copied from the program's output.
- Run all three suites before every commit. CI runs them again on GitHub.
