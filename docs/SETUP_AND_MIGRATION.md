# OpsIQ — Setup and Migration to a New Windows PC

Follow this guide to restore OpsIQ on another Windows PC **without needing the old PC**. Everything you need is on GitHub or can be recreated with the commands below.

Checked on 29 October 2026 against commit `ac32a9d`. The dataset download step was tested into an empty folder, and it produced files byte-identical to the originals.

Every command is for **Windows PowerShell**. Each step says **which folder** to be in.

---

## 0. Quick checklist

Tick these off in order. Details follow.

- [ ] 1. Install Python 3.14, Node.js 24, Git, and VS Code
- [ ] 2. Set your Git name and email
- [ ] 3. Clone `https://github.com/SwomBR/OpsIQ.git`
- [ ] 4. Download the dataset (`python -m src.download_data --with-database-files`)
- [ ] 5. Run the Version 1 tests (expect **89 OK**) and the CLI report
- [ ] 6. Create `backend\.venv`, install `requirements.txt`, run the backend tests (expect **61 OK**)
- [ ] 7. `npm ci` in `frontend`, run `npm test` (expect **41 passed**), `npm run lint`, `npm run build`
- [ ] 8. Optional: build the SQLite database and run `verify` (expect **33 of 33**)
- [ ] 9. Start the API, then the dashboard, and compare the numbers (section 9)
- [ ] 10. `git status` shows a clean working tree

---

## 1. Required software

| Software | Version | Why | Check with |
|---|---|---|---|
| Python | **3.14** recommended (tested: 3.14.6). `.python-version` says 3.14 | Analytics, API, database | `python --version` |
| Node.js | **24** recommended (tested: 24.18.0). Must be **22.12 or newer**: Vitest 5 needs `^22.12.0 \|\| ^24.0.0 \|\| >=26` | Dashboard | `node --version` |
| npm | Comes with Node (tested: 11.16.0) | Dashboard packages | `npm --version` |
| Git | Any recent version | Get the code | `git --version` |
| VS Code | Any recent version | Editor (optional) | — |

Notes:
- The README says Python 3.10+ should work (the code uses `X | None` type syntax, which needs 3.10). **Only 3.14 has been tested.** Use 3.14 to be safe.
- When installing Python, tick **"Add python.exe to PATH"**.
- If typing `python` opens the Microsoft Store, turn off the "App execution aliases" for Python (Settings → Apps → Advanced app settings → App execution aliases), or reinstall Python from python.org.

### VS Code extensions

The project has **no `.vscode` folder and no required extensions**. These are suggestions, not requirements:

- **Python** (Microsoft) — running and debugging Python, choosing the virtual environment.
- **Mermaid preview** (any) — to see the diagrams in `docs/` (GitHub shows them automatically).

---

## 2. Git setup

**Folder:** any.

```powershell
git config --global user.name "SwomBR"
git config --global user.email "<your GitHub email>"
```

- **What it does:** labels your future commits with your name.
- **Success:** no output. `git config --global --list` shows the values.

To push from the new PC, Git will ask you to sign in to GitHub the first time (a browser window opens). **Never paste a password or token into project files.**

---

## 3. Clone the repository

**Folder:** where you keep projects, for example `C:\Users\<you>\Projects`.

```powershell
git clone https://github.com/SwomBR/OpsIQ.git
cd OpsIQ
git log -3 --oneline
```

- **What it does:** downloads the code and its full history.
- **Success:** the newest commit is the latest one on GitHub.
- **If it fails:** check your internet connection and the URL. The repository is public, so no login is needed to clone.

From here on, **"project root"** means this `OpsIQ` folder.

---

## 4. Get the dataset

The CSV files are **not in Git**. They are large and licensed CC BY-NC-SA 4.0 (non-commercial).

**Folder:** project root.

```powershell
python -m src.download_data --with-database-files
```

- **What it does:** downloads the public Olist zip from Kaggle (about 45 MB, no account needed) and extracts the 7 files OpsIQ uses into `data\raw\`. `--with-database-files` adds the sellers file, which only the optional SQL database needs.
- **Success:** `Extracted 7 files into ...\data\raw` (about 7 seconds on 29 Oct 2026).
- **If it fails** (`Download failed: ...`):
  1. Open https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce, sign in, and click **Download**.
  2. Unzip it and copy these files into `data\raw\`:
     `olist_orders_dataset.csv`, `olist_order_items_dataset.csv`, `olist_order_payments_dataset.csv`, `olist_products_dataset.csv`, `olist_customers_dataset.csv`, `product_category_name_translation.csv`, and (for SQL only) `olist_sellers_dataset.csv`.
  3. Alternatively, copy `data\raw\` from the old PC on a USB stick.

Not needed: `olist_geolocation_dataset.csv` and `olist_order_reviews_dataset.csv` (no code uses them).

---

## 5. Version 1: tests and the CLI report

**Folder:** project root. **No packages to install**: Version 1 uses only Python's standard library.

```powershell
python -m unittest discover -s tests -v
```

- **Success:** ends with `Ran 89 tests ...` and `OK`.
- **If it fails:** read the first error. These tests do not need the dataset, so a failure means a Python version or code problem, not missing data.

```powershell
python -m src.business_report
```

- **What it does:** prints the full business report (orders, delivery, late orders, sales, products, customers).
- **Success:** a long report that starts with `OPSIQ BUSINESS SUMMARY REPORT`, shows `Total orders: 99,441`, and ends with `END OF OPSIQ REPORT`. It takes about 5 seconds.
- **If it says** `Dataset file not found: ...`, repeat step 4.
- **Always use `python -m`.** `python src\business_report.py` fails with `No module named 'src'`.

---

## 6. Backend (API)

**Folder:** `backend`.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

- **What it does:** creates a private Python environment for the API (`backend\.venv`), switches to it, and installs FastAPI, Uvicorn, and httpx2 at the exact versions in `requirements.txt`.
- **Success:** your prompt starts with `(.venv)`, and pip ends with `Successfully installed ...`.
- **If `Activate.ps1` is blocked** ("running scripts is disabled"): run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, answer `Y`, and try again.
- **Every new terminal:** run `.\.venv\Scripts\Activate.ps1` again before using the API.

```powershell
python -m unittest discover -s tests -v
```

- **Success:** `Ran 61 tests ...` and `OK`.

---

## 7. Frontend (dashboard)

**Folder:** `frontend` (in a new terminal, from the project root: `cd frontend`).

```powershell
npm ci
npm test
npm run lint
npm run build
```

| Command | What it does | Success looks like |
|---|---|---|
| `npm ci` | Installs the exact package versions from `package-lock.json` into `node_modules` | `added ... packages`; no `ERR!` |
| `npm test` | Runs the 41 frontend tests | `Tests  41 passed (41)` |
| `npm run lint` | Checks the code style with oxlint | No warnings or errors listed |
| `npm run build` | Builds the production files into `frontend\dist` | `✓ built in ...` |

- **If `npm ci` complains about the Node version:** install Node 24 and open a new terminal.
- Use `npm ci`, not `npm install`, so you get exactly the tested versions.

---

## 8. Optional: the SQL database

**Folder:** project root. Needs `olist_sellers_dataset.csv` (step 4 with `--with-database-files`).

```powershell
python -m src.database build
python -m src.database verify
```

- **What it does:** creates `data\processed\opsiq.db` (about 98 MB, about 20 seconds), then compares 33 SQL results with the Python results.
- **Success:** `Database created: ...` with row counts (for example `orders: 99,441 rows`), then `33 of 33 metrics match.`
- Other commands: `python -m src.database list`, `python -m src.database query orders_by_status`, `python -m src.database late --min-days 30 --limit 5`.
- **The API and dashboard do not need the database.**

---

## 9. Run the application

### Terminal 1 — API

**Folder:** `backend`, with `(.venv)` active.

```powershell
uvicorn app.main:app --reload
```

- **Success:** `Uvicorn running on http://127.0.0.1:8000`, then after about 10–15 seconds `Analytics cache warm-up finished.`
- **Check:** open http://127.0.0.1:8000/api/v1/health (expect `{"app":"OpsIQ","status":"healthy"}`) and http://127.0.0.1:8000/docs.
- **Stop it:** Ctrl+C.

### Terminal 2 — dashboard

**Folder:** `frontend`.

```powershell
npm run dev
```

- **Success:** `Local: http://localhost:5173/`. Open it in a browser.

### Verify the dashboard

Compare with these numbers (from the 29 Oct 2026 audit):

| Card | Expected |
|---|---|
| Total orders | 99,441 |
| Delivered orders / share | 96,478 / 97.02% |
| Late deliveries | 7,826 |
| On time / late | 91.89% / 8.11% |
| Product revenue | R$13.59M |
| Unique / repeat customers | 96,096 / 2,997 |

No section should say "This section could not be loaded". For the full manual check (phone layout, dark mode, stopping the API), see [TESTING_GUIDE.md §6](TESTING_GUIDE.md#6-manual-dashboard-check-5-minutes).

---

## 10. Environment variables (optional)

**No secrets are needed.** The defaults work locally.

| Variable | Where | Default | When to change |
|---|---|---|---|
| `OPSIQ_DATA_DIR` | API (shell) | `data/raw` | Data stored elsewhere |
| `OPSIQ_CORS_ORIGINS` | API (shell) | `http://localhost:5173,http://127.0.0.1:5173` | The dashboard runs on a different address or port |
| `OPSIQ_LOG_LEVEL` | API (shell) | `INFO` | `DEBUG` for more detail |
| `OPSIQ_PRELOAD_DATA` | API (shell) | `true` | `false` to skip the startup calculation |
| `OPSIQ_ENV` | API (shell) | `development` | Label only |
| `VITE_API_BASE_URL` | `frontend\.env.local` | `http://127.0.0.1:8000` | API on another address or port |

```powershell
# API, in the backend terminal before starting uvicorn
$env:OPSIQ_LOG_LEVEL = "DEBUG"

# Dashboard: copy the example file and edit it (frontend folder)
Copy-Item .env.example .env.local
```

`$env:` values last only for that terminal. `.env.local` is ignored by Git. **Never put secrets in `VITE_` variables**, because they are copied into the public JavaScript.

---

## 11. What is not in Git (and how to recreate it)

| Item | Path | Size (old PC) | Recreate with | Copy from old PC? |
|---|---|---|---|---|
| Dataset | `data\raw\*.csv` | ~126 MB for all 9 files; ~50 MB for the 7 that are used | Step 4 | Only if the download fails |
| SQLite database | `data\processed\opsiq.db` | ~98 MB | Step 8 | No |
| Backend virtual environment | `backend\.venv\` | — | Step 6 | **No** (it only works on the PC that created it) |
| Frontend packages | `frontend\node_modules\` | — | `npm ci` | No |
| Frontend build | `frontend\dist\` | — | `npm run build` | No |
| Python caches | `__pycache__\` | — | Automatic | No |
| Local settings | `.env`, `frontend\.env.local` | none exist on the old PC | Copy `.env.example` | No |
| Editor settings | `.vscode\` | none exist | — | No |

On the old PC (checked 29 Oct 2026) there were **no uncommitted changes** and **no `.env` files**. Nothing else needs copying.

---

## 12. Common errors and fixes

| Error | Cause | Fix |
|---|---|---|
| `python` opens the Microsoft Store or "not recognized" | Python not on PATH | Reinstall Python and tick "Add to PATH"; turn off the App execution alias |
| `No module named 'src'` | Ran a file directly, or from the wrong folder | From the project root: `python -m src.business_report` |
| `No module named 'fastapi'` | Virtual environment not active | `cd backend`, then `.\.venv\Scripts\Activate.ps1` |
| `uvicorn : The term 'uvicorn' is not recognized` | Virtual environment not active | Activate it, or run `python -m uvicorn app.main:app --reload` |
| `running scripts is disabled on this system` | PowerShell policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `[Errno 10048]` / address already in use | Port 8000 is taken | `uvicorn app.main:app --port 8001`, and set `VITE_API_BASE_URL=http://127.0.0.1:8001` in `frontend\.env.local` |
| Dashboard: "Could not reach the OpsIQ API" | API not running, still starting, or wrong URL | Start the API, wait ~15 s, press "Try again"; check `VITE_API_BASE_URL` |
| Browser console: CORS error | The dashboard's address is not allowed | Set `$env:OPSIQ_CORS_ORIGINS` to the exact dashboard address, then restart the API |
| API returns 503 "dataset is not available" | CSV files missing | Step 4, then restart the API |
| `Dataset file not found` (CLI) | CSV files missing | Step 4 |
| `npm ERR! engine` / Vitest will not start | Node too old | Install Node 24 |
| `Download failed` | Kaggle refused or no internet | Manual download (step 4) |
| `LF will be replaced by CRLF` | Windows line endings | Harmless; ignore |
| Numbers don't change after replacing CSV files | API cache | Restart the API |

---

## 13. Final check

**Folder:** project root.

```powershell
git status
```

**Success:** `nothing to commit, working tree clean`. The downloaded data, database, `.venv`, `node_modules`, and `dist` should **not** appear, because Git ignores them. If any of them do appear, do not commit them; check `.gitignore`.

Next: [PAUSE_AND_RESUME.md](PAUSE_AND_RESUME.md) for day-to-day work, and [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) for what to build next.
