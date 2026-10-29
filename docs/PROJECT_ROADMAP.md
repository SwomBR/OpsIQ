# OpsIQ Roadmap

The current status of every area, and the remaining work in priority order. Based on the audit of 29 October 2026 (commit `ac32a9d`). Evidence details: [PROJECT_HANDOVER.md](PROJECT_HANDOVER.md) and [TESTING_GUIDE.md](TESTING_GUIDE.md).

**Rule:** do not add new features until the existing application is set up and checked on the new PC (stages 1–2).

---

## 1. Project status

Status labels: **Complete and verified** · **Implemented but not fully verified** · **Partially complete** · **Configured but not deployed** · **Not started** · **Blocked** · **Unknown**.

| Feature or Task | Status | Evidence | Remaining Work | Priority |
|---|---|---|---|---|
| Data ingestion (CSV loading) | Complete and verified | `open_order`/`load_csv`; CLI and API ran on the full data | Merge the two identical loaders; check columns on load | Low |
| Dataset download | Complete and verified | `download_data` fetched 7 byte-identical files (29 Oct) | Keep the manual fallback documented | Low |
| Data validation | Complete and verified | `python -m src.data_validator` ran; 20 tests | Optional: show data-quality results in the API/dashboard | Low |
| Analytics (orders, delivery, sales, products, customers) | Complete and verified | 89 tests; CLI = API = SQL (33/33) | Remove duplicate date logic; clearer names | Low |
| Python CLI reporting | Complete and verified | `python -m src.business_report` ran | Fix relative paths in the module CLIs | Low |
| SQL queries | Complete and verified | All 7 queries and `late` ran; `verify` 33/33 | Optional: more queries (sellers, states) | Low |
| Database (SQLite) | Complete and verified (optional, local-only) | Built DB has 7 tables with expected row counts | Not used by the API (by design) | Low |
| Backend (FastAPI app) | Complete and verified | Server ran; warm-up ~11 s; 61 tests | — | — |
| API endpoints (10) | Complete and verified | Every route returned 200 with real data; 422/404/405/503 checked | Optional: filters (date/state) | Medium (later) |
| Caching | Complete and verified | ~5 ms cached responses; 8 cache tests | — | — |
| CORS | Complete and verified | Allowed/blocked origins checked live | Set the production origin when deploying | With deployment |
| Frontend (React app) | Complete and verified (desktop) | 41 tests, lint, build; real-browser render at 1400 px | — | — |
| Dashboard (7 sections) | Implemented but not fully verified | Desktop verified 29 Oct; phone layout and dark mode **not** re-checked | Manual phone and dark-mode check; add "Orders not delivered" to the header nav | High (quick) |
| Testing | Implemented but not fully verified | 191/191 pass; no coverage; no browser E2E | Coverage report; Playwright E2E | Medium |
| GitHub | Complete and verified | `main` = `origin/main`; public repo; audit documentation pushed | Push after every work session | Ongoing |
| CI/CD | Partially complete | CI runs #1 and #2 passed; no automatic deployment | CD comes with deployment | Medium |
| Deployment | Configured but not deployed | `render.yaml`; no live URLs | Create the Render Blueprint (owner's account) | **High** |
| AI features | Not started | No AI code or packages | See stage 5 | Low (after deployment) |
| Documentation | Complete and verified | This document set, checked against the code on 29 Oct | Keep it updated with each change | Ongoing |
| Migration readiness | Complete and verified | Clean repo; data downloadable; setup guide | Follow `SETUP_AND_MIGRATION.md` on the new PC | **High** |
| Original master-plan items (PostgreSQL, Power BI, run audit trail, Docker) | Not started | See [master reference §14](PROJECT_MASTER_REFERENCE.md#14-original-plan-vs-what-was-built) | Decide whether they still matter | Low |

Nothing is **Blocked**. Deployment needs only the owner's Render account.

---

## 2. Roadmap

### Stage 1 — Continue on the new PC (immediate)

1. Follow [SETUP_AND_MIGRATION.md](SETUP_AND_MIGRATION.md): clone, download the data, install, and run all three test suites (89 / 61 / 41).
2. Start the API and dashboard and compare the numbers with the expected values.

### Stage 2 — Verify the current application

1. Do the 5-minute manual dashboard check, including the phone layout and dark mode ([TESTING_GUIDE.md §6](TESTING_GUIDE.md#6-manual-dashboard-check-5-minutes)).
2. Run `python -m src.database build` and `verify` (expect 33/33).
3. Optional: measure test coverage and note the weakest files.

### Stage 3 — Deploy

1. Check that Render supports Python 3.14 (otherwise choose 3.13, run the tests, and update `.python-version` and CI).
2. Create the Render Blueprint and connect the two URLs ([DEPLOYMENT.md](DEPLOYMENT.md)).
3. Run the checks in DEPLOYMENT.md §3 step 4, then add the live URL and "deployed" status to the README.

### Stage 4 — Production readiness (small, safe improvements)

1. Shared delivery-delay helper (removes the duplicated logic in `delivery_analyzer` and `delivery_exceptions`).
2. Use `RAW_DATA_DIR` in the module CLIs; check CSV columns on load.
3. Playwright end-to-end test of the dashboard, run in CI.
4. Split `httpx2` into a `requirements-dev.txt`; consider a lock file.
5. Date-range and state filters (API query parameters + dashboard controls).
6. Delay causes: late rate by seller, state, and category (data that is already loaded).
7. Optional: serve the API from SQLite for faster startup.
8. Authentication, but **only** if private data is ever added.

### Stage 5 — Future AI functionality (proposals)

In this order, each with tests:

1. Rule-based anomaly flags (no AI needed), for example months with an unusually high late rate.
2. A simple order-volume forecast, compared against a naive baseline.
3. An AI management briefing: the backend sends **only aggregate metrics** to a language model, labels the result as generated, and shows the facts beside it. The API key lives in a backend environment variable, never in Git or the frontend. It costs money per request, so it needs a spending limit.
4. Natural-language questions mapped to fixed, tested queries (never arbitrary SQL).

Details: [master reference §12](PROJECT_MASTER_REFERENCE.md#12-ai-functionality).

### Stage 6 — Portfolio and interview preparation

1. After deploying: put the live link, screenshots, and a 3-sentence summary at the top of the README.
2. Record a 2-minute demo video (dashboard → API docs → CLI → tests).
3. Practise the explanations and questions in [LEARNING_GUIDE.md](LEARNING_GUIDE.md#explaining-opsiq).
4. Be ready to explain the honest gaps: no AI yet, SQLite rather than PostgreSQL, and why.
5. Pin the repository on your GitHub profile.
