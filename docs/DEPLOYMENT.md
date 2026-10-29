# Deploying OpsIQ

**Current status (checked 29 Oct 2026): prepared, not deployed.** Everything below has been rehearsed locally (see [§5](#5-what-has-been-verified)), but no hosting account has been used, so no public URL exists yet. The default Render addresses (`opsiq-api.onrender.com`, `opsiq-dashboard.onrender.com`) did not respond on 29 Oct 2026.

## 1. What gets deployed

| Part | Type | Build | Start |
|---|---|---|---|
| API | Python web service | `pip install -r backend/requirements.txt && python -m src.download_data` | `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Dashboard | Static site | `npm ci && npm run build` (in `frontend/`) | — (serve `frontend/dist`) |

The two only know about each other through two settings:

- `VITE_API_BASE_URL` (dashboard build) = the API's public URL.
- `OPSIQ_CORS_ORIGINS` (API) = the dashboard's public URL.

**Where the data comes from:** the CSV files are not in Git. During the API's build, `python -m src.download_data` downloads the public dataset from Kaggle (~45 MB zip, about 7 seconds in testing) and extracts the six files the API needs. No Kaggle account or key is needed: anonymous download worked on 29 Oct 2026. Kaggle could change this; if the build fails at that step, see [§6](#6-troubleshooting).

The dataset licence (CC BY-NC-SA 4.0) allows non-commercial sharing with attribution; the dashboard footer and README credit Olist. The download happens on the server from Kaggle, so this project does not redistribute the files itself.

## 2. Recommended host: Render

Render was chosen because it runs both a Python web service and a static site from one `render.yaml` file, connects to GitHub, and has free options. Terms checked on 29 Oct 2026 in [Render's free-tier documentation](https://render.com/docs/free); **check them again before you deploy, because free tiers change**:

- Free **static sites**.
- Free **web services** get 750 instance hours per workspace per month (enough for one service running all month).
- A free web service **spins down after 15 minutes without traffic**; waking it takes about a minute. For OpsIQ, add the ~10-second cache warm-up.
- Free web services have **no persistent disk**. OpsIQ does not need one: it downloads the data at build time and keeps results in memory.
- Render's docs list memory per plan on the pricing page; check it is above what OpsIQ uses (about 165 MB measured locally after warm-up).

Nothing in this guide requires a paid plan. Do not add a payment method unless you decide to.

## 3. Step by step

### Step 1 — Push the code to GitHub (you)

Done: the code is on GitHub (`main`), and CI passes there. Before deploying, make sure your latest changes are pushed (`git status` is clean and up to date), because Render deploys from GitHub.

**Check first:** Render reads the Python version from `.python-version` (3.14). Confirm in Render's documentation that 3.14 is supported. If it is not, switch to the newest supported version (for example 3.13), run all tests locally, and update `.python-version` and `ci.yml`.

### Step 2 — Create the services from the Blueprint (you; needs your Render account)

1. Sign in at <https://dashboard.render.com> with GitHub.
2. Choose **New → Blueprint**, select the `SwomBR/OpsIQ` repository. Render reads [render.yaml](../render.yaml) and proposes two services: `opsiq-api` and `opsiq-dashboard`.
3. Render asks for the two `sync: false` values. You do not know the URLs yet, so enter placeholders:
   - `OPSIQ_CORS_ORIGINS`: `https://opsiq-dashboard.onrender.com`
   - `VITE_API_BASE_URL`: `https://opsiq-api.onrender.com`
4. Create the services and wait for both builds.

### Step 3 — Connect the two services

1. Open each service and copy its real URL (Render may add a suffix if the name is taken, for example `https://opsiq-api-abcd.onrender.com`).
2. In **opsiq-api → Environment**, set `OPSIQ_CORS_ORIGINS` to the dashboard's real URL — exactly, with `https://` and **no trailing slash**. Save; the API restarts.
3. In **opsiq-dashboard → Environment**, set `VITE_API_BASE_URL` to the API's real URL. Then **Manual Deploy → Clear build cache & deploy**: Vite copies the value into the JavaScript at build time, so a rebuild is required.

### Step 4 — Check it works

PowerShell, replacing the URLs with yours:

```powershell
# 1. Health (may take ~1 minute if the service was asleep)
Invoke-RestMethod https://opsiq-api.onrender.com/api/v1/health

# 2. Real data
Invoke-RestMethod https://opsiq-api.onrender.com/api/v1/analytics/summary
# Expect total_orders 99441, delivered_orders 96478, late_delivered_orders 7826

# 3. CORS: the dashboard's address must come back in this header
(Invoke-WebRequest https://opsiq-api.onrender.com/api/v1/health `
  -Headers @{ Origin = "https://opsiq-dashboard.onrender.com" }).Headers["Access-Control-Allow-Origin"]
```

Then open the dashboard URL and compare its numbers with the [Key results](../README.md#key-results). Open the browser's developer tools (F12) → Console: there should be no red errors.

Only after these checks pass should the README say the app is deployed, with its URL.

## 4. Other hosts

The same commands work on any host that runs a Python process and serves static files. Requirements:

- Python 3.10+ (the repository's `.python-version` says 3.14), Node.js 22.12+ for the build.
- The build runs from the **repository root** (the API imports `src/`).
- Outbound internet during the build (for the Kaggle download), or upload the CSV files and set `OPSIQ_DATA_DIR`.
- At least ~300 MB of memory for the API (165 MB measured, plus headroom).

## 5. What has been verified

On 29 Oct 2026, on Windows, without any hosting account:

| Check | Result |
|---|---|
| `python -m src.download_data` into an empty folder | 6 files extracted; orders and order-items files byte-identical to the local copies |
| API with `OPSIQ_ENV=production`, the downloaded data, port 8001, and `OPSIQ_CORS_ORIGINS=http://localhost:4173` | Started; warm-up finished in ~10 s |
| CORS | Allowed origin received `Access-Control-Allow-Origin`; the development origin did not |
| Dashboard production build with `VITE_API_BASE_URL=http://127.0.0.1:8001`, served by `vite preview` | Every key figure displayed; no console errors; one request per endpoint; no horizontal scrolling at 390 px |
| API stopped while the dashboard is open | Every section shows "Could not reach the OpsIQ API…" with a retry button; no crash |
| `.github/workflows/ci.yml` | **Validated by GitHub:** runs #1 and #2 passed (29 Oct 2026) |
| `render.yaml` | Parses as valid YAML. **Not validated by Render.** |

Not verified: a real Render build, Render's Python and Node environments (including Python 3.14 support), and the public URLs.

Except for the CI row, these checks come from earlier work on the same day, before the project audit (historical). The audit re-checked the dataset download (7 files, all byte-identical), CORS, and the local API and dashboard on desktop. It did **not** repeat the production-settings rehearsal or the 390 px check.

## 6. Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| Build fails at `python -m src.download_data` | Kaggle refused the anonymous download. Create a Kaggle account and download the zip manually, or commit the six CSV files to a private copy of the repo and remove the download step. |
| Dashboard sections say "Could not reach the OpsIQ API" | `VITE_API_BASE_URL` is wrong or the dashboard was not rebuilt after changing it; or the API is still waking up — wait a minute and press "Try again". |
| Browser console shows a CORS error | `OPSIQ_CORS_ORIGINS` does not exactly match the dashboard URL (check `https://`, no trailing slash). |
| API returns 503 "dataset is not available" | The data folder is empty. Check the build log for the download step and `OPSIQ_DATA_DIR`. |
| First request is slow | Normal on a free plan after 15 minutes idle (wake-up ~1 minute, then ~10 s warm-up). |
