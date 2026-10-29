# OpsIQ — Project Handover

**Written:** 29 October 2026, when development was paused.
**Purpose:** let you (or another developer) pick OpsIQ up again after weeks or months, on any computer, without guessing.

Everything marked **Verified** below was checked on 29 October 2026 by running the code, not by reading old notes.

---

## A. Project overview

**What OpsIQ is.** A business operations intelligence platform for an online marketplace. It reads about 100,000 real (anonymised) e-commerce orders from the public Olist dataset and turns them into metrics an operations manager cares about: how many orders were delivered, how many were late, which late orders to look at first, where revenue comes from, and how many customers come back.

**What it is for.** It is a learning and portfolio project. It shows practical skills across Python, data analysis, REST APIs, React, SQL, automated testing, CI, and deployment preparation.

**About "AI-Powered".** This is the long-term goal, not the current state. **No AI or machine learning is used today.** Every number is calculated by plain, rule-based Python and SQL. See section E.

**How the parts fit together.**

```text
Olist CSV files (data/raw/)
        │
        ▼
Analytics engine (src/, pure Python)  ──►  CLI report  (python -m src.business_report)
        │
        ▼
FastAPI backend (backend/)  ── JSON ──►  React dashboard (frontend/)

CSV files ──► optional SQLite database (src/database.py, sql/)
```

The most important design rule: **business calculations live in one place, `src/`.** The CLI report and the API call the same functions, so they always give the same numbers. The dashboard only displays what the API returns.

---

## B. Current status at a glance

| Part | Status | Evidence |
|---|---|---|
| Version 1 — Python analytics + CLI report | **Done, working** | 89 tests pass; report runs on the full dataset |
| Version 2 — FastAPI backend | **Done, working** | 61 tests pass; all 10 routes returned real data |
| React dashboard | **Done, working** (was further along than the old notes said) | 41 tests pass; lint and production build pass |
| SQL database (SQLite) | **Done, optional** | `verify`: 33 of 33 metrics match Python |
| CORS and caching | **Done** | CORS header checked live; cached responses ~5 ms |
| CI (GitHub Actions) | **Done, passing on GitHub** | First run passed on 29 Oct 2026 (run 40829727852) |
| Deployment (Render) | **Prepared, not deployed** | `render.yaml`, `docs/DEPLOYMENT.md` |
| AI business insights | **Not started** (idea only) | No AI code anywhere in the project |

---

## C. Verification results (29 October 2026)

Machine: Windows 11, Python 3.14.6, Node.js 24.18.0, npm 11.16.0.

| Check | Folder | Command | Result |
|---|---|---|---|
| Version 1 + database + download tests | project root | `python -m unittest discover -s tests -v` | **89 passed** |
| Backend API tests | `backend` (venv active) | `python -m unittest discover -s tests -v` | **61 passed** |
| Frontend tests | `frontend` | `npm test` | **41 passed** (5 files) |
| Frontend lint | `frontend` | `npm run lint` | **No problems** |
| Frontend production build | `frontend` | `npm run build` | **Built** (JS 238 kB, 74 kB gzipped) |
| CLI report on full data | project root | `python -m src.business_report` | **Ran to the end** |
| SQL check against Python | project root | `python -m src.database verify` | **33 of 33 match** |
| Live API | `backend` | `uvicorn app.main:app` + requests | **All 10 routes returned 200** with real values |

**Total: 191 automated tests, all passing.** None of the tests need the Olist CSV files; they create their own small sample data.

**Numbers produced by both the CLI report and the API (they matched exactly):**

| Metric | Value |
|---|---:|
| Total orders | 99,441 |
| Delivered orders | 96,478 (97.02%) |
| Delivered orders analysed (valid dates) | 96,470 (8 skipped) |
| On time / late | 88,644 (91.89%) / 7,826 (8.11%) |
| Average / longest delay | 9.55 / 188.98 days |
| Product revenue | 13,591,643.70 |
| Unique / repeat customers | 96,096 / 2,997 (3.12%) |

**Not re-checked this time:** the dashboard was not opened in a real browser during this handover. It is covered by automated tests and a successful build, and screenshots from earlier work are in `docs/screenshots/`.

### Corrections to the earlier progress notes

The old notes were partly out of date. What the files actually show:

- **"89 tests across backend and Version 1"** — wrong split. 89 is the **root `tests/` folder alone** (Version 1, database, and download helper). The backend has another **61**, and the frontend **41**.
- **"Four analytics endpoints"** — there are now **eight** analytics endpoints plus `/` and `/health` (10 routes in total). The extra ones are `dataset-info`, `sales`, `products`, and `customers`.
- **"Frontend is the next milestone"** — the frontend is **already built**, with every planned section.
- **"SQL is a possible extension"** — SQLite integration is **already built** (schema, 7 queries, build/verify tool).
- **"No commit or push"** — true until this handover: the backend, frontend, SQL, CI, and docs were all **uncommitted**. They are committed and pushed as part of this handover (see section J).

---

## D. What is completed

### Version 1 — analytics engine (`src/`)

Uses only the Python standard library (no `pip install` needed).

| File | What it does |
|---|---|
| `business_report.py` | The full CLI report. Main entry point. |
| `data_loader.py` | Loads the orders CSV; defines `PROJECT_ROOT` and `RAW_DATA_DIR`. |
| `data_validator.py` | Data-quality checks: missing, duplicate, invalid, out-of-order values. |
| `data_analyzer.py` | Orders by status (`count_orders_by_status`). |
| `delivery_analyzer.py` | On-time vs late and delays (`calculate_delivery_performance`). |
| `delivery_exceptions.py` | Late orders, longest delay first. |
| `sales_analyzer.py` | Revenue, freight, payment totals. |
| `product_analyzer.py` | Category and product performance. |
| `customer_analyzer.py` | Unique and repeat customers, customers per state. |
| `database.py` | Optional SQLite build, queries, and verify tool. |
| `download_data.py` | Downloads the dataset from Kaggle (no login needed). |

During Version 2, `data_analyzer.py` and `delivery_analyzer.py` were split into a **calculate** function (returns a dictionary) and a **print** function (the old report). This let the API reuse the calculations without copying them.

### Version 2 — FastAPI backend (`backend/`)

| File | What it does |
|---|---|
| `app/main.py` | Creates the app, adds CORS, error handlers, and background preloading. |
| `app/config.py` | Reads settings from environment variables (section H). |
| `app/api/routes.py` | `/` and `/health`. |
| `app/api/analytics.py` | The eight analytics routes. |
| `app/services/analytics_service.py` | Calls the `src/` functions; caches results. |
| `app/schemas.py` | Pydantic response schemas (the shape of every JSON reply). |
| `tests/` | 61 tests: API, analytics, reports, config. |

**Endpoints** (all `GET`, under `/api/v1`):

| Endpoint | Returns |
|---|---|
| `/health` | `{"app": "OpsIQ", "status": "healthy"}` |
| `/` | Welcome message |
| `/analytics/summary` | Totals, delivered %, late orders |
| `/analytics/orders-by-status` | Count per status |
| `/analytics/delivery-performance` | On-time/late, delays |
| `/analytics/delivery-exceptions?limit=10` | Most delayed orders (limit 1–100) |
| `/analytics/dataset-info` | First/last order date, when metrics were calculated |
| `/analytics/sales` | Revenue, freight, payments |
| `/analytics/products` | Top categories and products |
| `/analytics/customers` | Unique/repeat customers, per state |

Interactive docs: http://127.0.0.1:8000/docs (checked: returns 200).

**Implemented and verified:** routes, service layer, response schemas, tests, data loading, safe error handling (missing file → 503, bad data → 500 without file paths, bad `limit` → 422), **caching** (`functools.lru_cache` plus a `threading.Lock`; first request ~1–2 s, later ones ~5 ms), and **CORS** (only the dashboard addresses are allowed).

### React dashboard (`frontend/`)

React 19 + Vite 8, plain CSS, no chart library (bars are accessible HTML).

- Sections in `src/components/sections/`: Summary, Delivery, Order status, Exceptions, Sales, Products, Customers.
- Shared pieces: `StatTile`, `BarList`, `ProportionBar`, `Section`, `AsyncContent` (loading/error/empty states), `Header`.
- `src/api/client.js` talks to the API; `src/hooks/useApi.js` manages loading state.
- Light and dark themes, responsive layout, keyboard accessible.
- 41 tests with Vitest and Testing Library.

### SQL (`sql/`, `src/database.py`)

- `sql/schema.sql`: 7 tables with primary keys, foreign keys, and indexes.
- `sql/queries/`: 7 example queries (orders by status, delivery performance, late deliveries, late deliveries by month, revenue by category, repeat customers, orders per customer).
- `python -m src.database verify` compares SQL answers with the Python ones: 33 of 33 match.
- The database is **optional**. The report and the API still read the CSV files.

### Quality and delivery

- `.github/workflows/ci.yml`: runs all three test suites, lint, and the build on every push to `main` and every pull request.
- `render.yaml` + `docs/DEPLOYMENT.md`: a ready plan for hosting on Render's free tier.
- Documentation: `README.md`, `docs/ARCHITECTURE.md`, `docs/DEPLOYMENT.md`, `docs/LEARNING_GUIDE.md`, and this file.

---

## E. What is pending

| Item | Type | Notes |
|---|---|---|
| Keep CI green | Ongoing | The first GitHub run passed (29 Oct 2026). Check the **Actions** tab after each push. |
| Deploy to Render | **Pending** (needs your Render account) | Follow `docs/DEPLOYMENT.md`. Nothing has been deployed. |
| Date and state filters | Optional feature | API query parameters + dashboard controls. |
| Delay causes (by seller, state, category) | Optional feature | Shows *why* orders are late, not just which. |
| Serve the API from SQLite | Optional improvement | Faster startup than reading CSVs. |
| AI management briefing | Optional, **not started** | Send only the aggregate metrics (never customer data) to a language model; label the text as generated; keep the API key on the backend only. Has a cost per request. |
| Browser end-to-end tests | Optional | For example Playwright, in CI. |

Nothing is half-finished. There is no broken or partly written code waiting to be completed.

---

## F. Project structure

```text
OpsIQ/
├── src/                 Version 1 analytics (pure Python) + database + download tools
├── tests/               89 tests for src/
├── backend/
│   ├── app/             FastAPI application
│   ├── tests/           61 API tests
│   ├── requirements.txt fastapi, uvicorn, httpx2 (exact versions)
│   └── .venv/           virtual environment (NOT in Git — recreate it)
├── frontend/
│   ├── src/             React components, API client, tests
│   ├── package.json     npm scripts: dev, build, test, lint
│   ├── package-lock.json exact dependency versions
│   ├── .env.example     template for the API address
│   ├── node_modules/    (NOT in Git — run npm install)
│   └── dist/            build output (NOT in Git — run npm run build)
├── sql/                 schema.sql + queries/
├── data/
│   ├── raw/             Olist CSV files (NOT in Git — download them)
│   └── processed/       opsiq.db (NOT in Git — rebuild it)
├── docs/                guides, screenshots, master plan (.docx), this handover
├── .github/workflows/   CI
├── render.yaml          deployment plan
├── .python-version      3.14
└── README.md
```

---

## G. Data

The CSV files are **not in Git**, on purpose: they are large (about 140 MB in total) and the licence is CC BY-NC-SA 4.0 (non-commercial, share-alike). Get them again with one command.

**Required** (CLI report and API):

- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_products_dataset.csv`
- `olist_customers_dataset.csv`
- `product_category_name_translation.csv`

**Only for the optional SQL database:** `olist_sellers_dataset.csv`.

**Not used:** `olist_geolocation_dataset.csv`, `olist_order_reviews_dataset.csv` (they were downloaded, but no code reads them).

Note: older notes listed only four data files. The code now also needs the **payments** and **category translation** files.

Source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

---

## H. Setting up on a new computer

All commands are for Windows PowerShell.

### 1. Install the tools

- **Python 3.14** (3.10+ works; the project was developed on 3.14.6). Tick "Add Python to PATH".
- **Node.js 24** (22.12 or later is required by the test runner).
- **Git**, then set your name and email:

```powershell
git config --global user.name "SwomBR"
git config --global user.email "you@example.com"
```

### 2. Get the code and the data (project root)

```powershell
git clone https://github.com/SwomBR/OpsIQ.git
cd OpsIQ
python -m src.download_data --with-database-files
```

The last command puts the CSV files in `data/raw/`. If the download fails, download the zip manually from Kaggle and copy the files listed in section G into `data/raw/`.

### 3. Check Version 1 (project root)

```powershell
python -m unittest discover -s tests -v      # expect 89 OK
python -m src.business_report                # ends with END OF OPSIQ REPORT
```

Always use `python -m ...`. Running `python src/business_report.py` fails because Python cannot find the `src` package.

### 4. Set up the backend (`backend` folder)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v      # expect 61 OK
uvicorn app.main:app --reload
```

If PowerShell blocks `Activate.ps1`, run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

Open http://127.0.0.1:8000/docs. The server spends about 10 seconds calculating at startup.

### 5. Set up the dashboard (`frontend` folder, second terminal)

```powershell
cd frontend
npm ci              # installs exactly what package-lock.json lists
npm test            # expect 41 passed
npm run dev
```

Open http://localhost:5173 (the API must be running).

### 6. Optional: the SQL database (project root)

```powershell
python -m src.database build     # about 20 seconds, creates data/processed/opsiq.db
python -m src.database verify    # expect 33 of 33 metrics match
```

### Settings

No secrets are needed anywhere. Defaults work locally.

| Variable | Where | Default |
|---|---|---|
| `OPSIQ_ENV` | backend | `development` |
| `OPSIQ_DATA_DIR` | backend | `data/raw` |
| `OPSIQ_CORS_ORIGINS` | backend | `http://localhost:5173,http://127.0.0.1:5173` |
| `OPSIQ_LOG_LEVEL` | backend | `INFO` |
| `OPSIQ_PRELOAD_DATA` | backend | `true` |
| `VITE_API_BASE_URL` | `frontend/.env.local` | `http://127.0.0.1:8000` |

To change the frontend value, copy `frontend/.env.example` to `frontend/.env.local`. Never put secrets in a `VITE_` variable: they end up in the public JavaScript.

---

## I. What is not in Git, and why

| Not in Git | Why | How to get it back |
|---|---|---|
| `data/raw/*.csv` | Large; licence | `python -m src.download_data` |
| `data/processed/opsiq.db` (~94 MB) | Generated | `python -m src.database build` |
| `backend/.venv/` | Machine-specific | `python -m venv .venv` + `pip install` |
| `frontend/node_modules/` | Machine-specific, huge | `npm ci` |
| `frontend/dist/` | Build output | `npm run build` |
| `__pycache__/` | Python's temporary files | Created automatically |
| `.env`, `.env.local` | Could hold private values | Copy from `.env.example` |
| `.vscode/` | Personal editor settings | Optional |

All of this is controlled by `.gitignore` (and `frontend/.gitignore`).

**Nothing else needs copying.** Everything you need from the old computer is on GitHub, or can be recreated with the commands above.

---

## J. Git and GitHub state

- Repository: https://github.com/SwomBR/OpsIQ (**public**, so never commit secrets or private data).
- Branch: `main` (the only branch). Remote: `origin`.
- Before this handover, the latest commit on GitHub was `8153b0f` (29 Oct 2026). The backend, frontend, SQL, CI, deployment files, and most docs were **only on the local computer**.
- The handover pushed everything in a few commits, one per area: Version 1 refactor, backend, SQL database, frontend, CI/deployment/docs, and this handover document. Run `git log --oneline` to see them.

To check you are up to date after cloning:

```powershell
git status          # "nothing to commit, working tree clean"
git log -3 --oneline
```

---

## K. Known limitations and gotchas

- **Static data.** The metrics describe 2016–2018. After replacing CSV files, **restart the API** (the cache keeps the old results).
- **"Late" compares exact timestamps.** Estimated dates are at midnight, so delivery later on the estimated day counts as late (1,292 of 7,826).
- **Data quality.** 1,382 orders have out-of-order timestamps. They are reported, not fixed.
- **No filters** on the dashboard; it shows whole-dataset totals.
- **No authentication.** Fine for public, anonymised, aggregate data. Needed before adding private data.
- **Free hosting sleeps.** On Render's free plan, the first visit after 15 minutes idle takes about a minute.
- **Line endings.** Git on Windows converts line endings (you may see "LF will be replaced by CRLF" warnings). This is harmless.
- **Exact versions.** Backend packages are pinned in `requirements.txt`, frontend packages in `package-lock.json`. Install with `pip install -r` and `npm ci` to get the same versions that were tested.

---

## L. Recommended next steps, in order

1. **Clone and set up** on the new computer (section H). Confirm 89 + 61 + 41 tests pass.
2. **Check CI** in the GitHub Actions tab after your first push from the new computer.
3. **Deploy** using `docs/DEPLOYMENT.md`, then add the live link to the README.
4. Pick **one** feature from section E. Filters or delay causes are good next steps, and they use skills you already have.
5. Only then consider the **AI briefing**. Keep the API key in a backend environment variable, never in Git or the frontend.

Habits to keep: small commits with clear messages, run all tests before every commit, update the README when something changes.

---

## M. Where to learn more

- `docs/LEARNING_GUIDE.md`: the concepts used here (modules, REST, status codes, CORS, caching, React hooks, SQL joins, testing, CI) in simple English, plus practice questions.
- `docs/ARCHITECTURE.md`: data flow, caching, error handling, database schema, and testing strategy.
- `docs/DEPLOYMENT.md`: hosting step by step.
- `docs/AI_Powered_Business_Operations_Intelligence_Platform_Master_Plan_v1.docx`: the original project plan.

---

## N. Handover checklist

- [x] Project inspected (files, Git, data, configuration)
- [x] All 191 tests run and passing
- [x] CLI report and live API checked against real data
- [x] SQL results checked against Python (33/33)
- [x] No secrets found in the project
- [x] Large/generated files confirmed ignored by Git
- [x] Handover document written
- [x] All source code and docs committed and pushed to GitHub
- [x] First CI run on GitHub passed (both jobs)
- [ ] Deployment (not started; needs your Render account)
