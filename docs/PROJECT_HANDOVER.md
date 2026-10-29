# OpsIQ — Project Handover

**Last full audit:** 29 October 2026, commit `ac32a9d` (Windows 11, Python 3.14.6, Node 24.18.0).
**Purpose:** the current state of the project, what is proven to work, what is not, and what to do next. Written for you returning after a break, or for another developer or AI assistant.

Everything marked **Verified** was checked by running code during the audit, not by reading old notes.

| Read next | For |
|---|---|
| [SETUP_AND_MIGRATION.md](SETUP_AND_MIGRATION.md) | Restoring the project on a new PC |
| [PAUSE_AND_RESUME.md](PAUSE_AND_RESUME.md) | Stopping and restarting work safely |
| [PROJECT_MASTER_REFERENCE.md](PROJECT_MASTER_REFERENCE.md) | Every module, dataset, metric, and risk |
| [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) | Full status table and what to build next |

---

## Where I stopped

> **29 Oct 2026:** Paused after a full audit and documentation update. The app works end to end locally; CI is green; nothing is deployed. **Next step:** set up on the new PC (SETUP_AND_MIGRATION.md), then deploy (DEPLOYMENT.md).

(Add one line here every time you pause.)

---

## A. Executive summary

OpsIQ turns ~99,000 real e-commerce orders (the public Olist dataset) into operations metrics: delivery punctuality, late-order exceptions, sales, products, and customers. It has:

- a Python analytics engine with a command-line report,
- a FastAPI backend (10 routes, cached),
- a React dashboard (7 sections),
- an optional SQLite database with 7 SQL queries,
- 191 automated tests, and CI on GitHub.

Every part was run and checked on 29 Oct 2026, and the numbers agree across the CLI, API, SQL, and dashboard. **It is not deployed**, and **it contains no AI yet**, despite the "AI-Powered" name.

**Safe to pause:** yes. All code is on GitHub (`main` = `origin/main`), the dataset can be downloaded again with one command, and no secrets or local-only work exist. This audit's documentation was committed and pushed too (see section F).

---

## B. Status at a glance

| Part | Status | Evidence (29 Oct 2026) |
|---|---|---|
| Python analytics + CLI report | ✅ Complete and verified | 89 tests pass; report ran on the full data |
| Data validation | ✅ Complete and verified | Validator ran: 1,382 out-of-order timestamps, 8 delivered orders without a date |
| FastAPI backend | ✅ Complete and verified | 61 tests pass; all 10 routes returned real data; error codes checked live |
| React dashboard | ✅ Verified on desktop · ⚠️ phone and dark mode not re-checked | 41 tests, lint, build; real Edge render at 1400 px with all sections correct |
| SQLite + SQL | ✅ Complete and verified (optional) | 7 queries ran; `verify` 33/33 |
| Dataset download | ✅ Verified | 7 files, byte-identical to the local copies |
| CI (GitHub Actions) | ✅ Passing | Runs #1 and #2 succeeded |
| Deployment (Render) | ⏸ Configured, not deployed | `render.yaml`; no live URL |
| AI features | ❌ Not started | No AI code or packages |

---

## C. What was actually run (29 Oct 2026)

| Check | Result |
|---|---|
| `python -m unittest discover -s tests` | 89 passed |
| Backend tests (venv) | 61 passed |
| `npm test` / `npm run lint` / `npm run build` | 41 passed / clean / built |
| `python -m src.business_report` | Full report; 99,441 orders, 7,826 late |
| `python -m src.data_validator` | Report produced |
| `python -m src.database query` (all 7) + `late` + `verify` | All ran; 33 of 33 match |
| `python -m src.download_data` into an empty folder | 7 files in ~7 s, identical to the originals |
| Live API, full data | All 10 routes 200; invalid `limit` → 422; unknown path → 404; `POST` → 405; `/docs` → 200 |
| Live API, empty data folder | `/health` 200; analytics 503 naming the missing file; no paths leaked |
| CORS | Dashboard origin allowed; other origin blocked |
| Dashboard in Edge (headless), 1400 px, real API | Every section showed the expected numbers; no error messages |
| Dashboard at 390 px | **Not verified** (the screenshot was cut off, probably a headless-browser limit) |
| Dark mode | **Not verified** |
| GitHub sync | `main` = `origin/main`; working tree clean before the documentation changes |
| Render URLs | Default names did not respond, so not deployed |

**Numbers that matched across CLI, API, SQL, and dashboard:** 99,441 orders · 96,478 delivered (97.02%) · 96,470 analysed · 88,644 on time (91.89%) · 7,826 late (8.11%) · 9.55-day average delay · 188.98-day maximum · revenue 13,591,643.70 · 96,096 unique customers, 2,997 repeat (3.12%).

### Corrections to earlier notes

| Earlier claim | Reality |
|---|---|
| "89 tests across backend and Version 1" | 89 is the root suite alone; the backend has 61 and the frontend 41 (191 in total) |
| "Four analytics endpoints" | Eight analytics endpoints plus `/` and `/health` |
| "Frontend and SQL are future work" | Both are built |
| "Four data files" | Six required files (plus sellers for SQL) |
| "Raw data ~140 MB" (first handover) | ~126 MB for all 9 files; ~50 MB for the 7 used |
| Manual browser checks at 390 px and in dark mode (ARCHITECTURE/DEPLOYMENT, earlier work) | Historical; not reproduced in this audit; the script is not in the repository |

---

## D. Completed work

- **Version 1 (`src/`):** loading, validation, order/delivery/sales/product/customer analytics, CLI report. Standard library only.
- **Version 2 (`backend/`):** FastAPI app with settings from environment variables, CORS, a startup warm-up thread, an in-memory cache with a lock, Pydantic response schemas, safe error handling (503/500/422/404), and 61 tests.
- **Dashboard (`frontend/`):** 7 sections with KPI cards, HTML bar charts, an exceptions table with a 10/25/50/100 selector and severity badges, loading/error/empty states with retry, responsive CSS, automatic dark mode, and 41 tests.
- **SQL (`sql/`, `src/database.py`):** schema with keys and indexes, a safe repeatable build, 7 queries, a parameterised `late` query, and `verify`.
- **Tooling:** dataset downloader, CI workflow, Render Blueprint, full documentation.

Module-by-module details: [PROJECT_MASTER_REFERENCE.md §3](PROJECT_MASTER_REFERENCE.md#3-module-reference).

## E. Pending work

| Item | Type | Next step |
|---|---|---|
| Manual phone and dark-mode check | Verification | [TESTING_GUIDE.md §6](TESTING_GUIDE.md#6-manual-dashboard-check-5-minutes) |
| Deploy to Render | **Pending** (needs your account) | [DEPLOYMENT.md](DEPLOYMENT.md) |
| Coverage and browser E2E tests | Quality | [PROJECT_ROADMAP.md stage 4](PROJECT_ROADMAP.md#stage-4--production-readiness-small-safe-improvements) |
| Filters, delay causes | Optional features | Roadmap |
| AI features | Optional, **not started** | Roadmap stage 5 |

No feature is half-built. There is no broken or partly written code.

## F. Git state

- Repository: https://github.com/SwomBR/OpsIQ (**public**). Branch `main` only.
- At the start of the audit: `main` = `origin/main` = `ac32a9d`, clean working tree.
- The audit **created or updated documentation only** (`README.md` and files in `docs/`). No code or tests were changed. With your approval, they were committed and pushed to `main` as `docs: add comprehensive OpsIQ project handover and reference`.

## G. What must be transferred separately

**Nothing is required.** Everything is on GitHub or can be recreated:

| Not in Git | Recreate with |
|---|---|
| `data/raw/*.csv` | `python -m src.download_data --with-database-files` (verified). Copy by hand only if Kaggle fails |
| `data/processed/opsiq.db` | `python -m src.database build` |
| `backend/.venv/` | `python -m venv .venv` + `pip install -r requirements.txt` |
| `frontend/node_modules/`, `frontend/dist/` | `npm ci`, `npm run build` |

No `.env` files, secrets, or editor settings exist on the old PC.

## H. Critical risks

| Risk | Severity | Action |
|---|---|---|
| Not deployed, so reviewers can't try it | Medium | Deploy (stage 3 of the roadmap) |
| The dataset download relies on Kaggle's anonymous endpoint | Medium | Keep the manual download fallback; optionally keep a private copy of the CSVs |
| Dataset licence is non-commercial (CC BY-NC-SA 4.0) | Medium | Never commit or sell the data; keep the attribution |
| The name says "AI-Powered" but there is no AI | Medium | Be upfront in interviews (the README already is) |
| Python 3.14 may not be available on the host | Medium | Check before deploying; fall back to 3.13 if needed |
| No browser E2E tests or coverage | Medium | Add after deploying |

The full list of 21 items is in [PROJECT_MASTER_REFERENCE.md §13](PROJECT_MASTER_REFERENCE.md#13-risks-and-technical-debt).

## I. Next steps

1. On the new PC: [SETUP_AND_MIGRATION.md](SETUP_AND_MIGRATION.md). Confirm 89 / 61 / 41 tests and the dashboard numbers.
2. Do the manual phone and dark-mode check.
3. Deploy with [DEPLOYMENT.md](DEPLOYMENT.md).
4. Then pick from [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md).
