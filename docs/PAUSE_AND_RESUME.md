# OpsIQ — Pause and Resume

A short checklist for stopping work safely and picking it up again, on the same PC or a new one.

---

## Pausing (any time you stop for more than a day)

**Folder:** project root, PowerShell.

1. **Stop the running servers:** press Ctrl+C in the API terminal and in the dashboard terminal.
2. **Run all tests** so you know the state you are leaving:
   ```powershell
   python -m unittest discover -s tests              # expect OK (89)
   cd backend; .\.venv\Scripts\Activate.ps1; python -m unittest discover -s tests; deactivate; cd ..   # expect OK (61)
   cd frontend; npm test; cd ..                       # expect 41 passed
   ```
3. **See what changed:** `git status`
4. **Commit the work** (small, clear message):
   ```powershell
   git add <the files you changed>
   git commit -m "Describe what changed and why"
   ```
   Check that no data, `.env`, `.venv`, `node_modules`, `dist`, or `.db` files are listed before committing. `.gitignore` should already keep them out.
5. **Push:** `git push`, then check the **Actions** tab on GitHub turns green.
6. **Write one line of notes** in [PROJECT_HANDOVER.md](PROJECT_HANDOVER.md) ("Where I stopped"): what you were doing and the next step. Commit and push it.
7. **Confirm:** `git status` shows `nothing to commit, working tree clean` and `Your branch is up to date with 'origin/main'`.

If you must stop in the middle of something that doesn't work yet, commit it to a **branch** instead of `main`:

```powershell
git switch -c wip/<short-name>
git add <files>; git commit -m "WIP: <what and why>"
git push -u origin wip/<short-name>
```

Never force-push, and never commit secrets.

---

## Resuming on the same PC

**Folder:** project root.

```powershell
git switch main
git pull
python -m unittest discover -s tests
```

Then start the app:

```powershell
# Terminal 1
cd backend; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload
# Terminal 2
cd frontend; npm run dev
```

If `git pull` changed `backend/requirements.txt` or `frontend/package-lock.json`, reinstall first: `python -m pip install -r requirements.txt` (backend, venv active) or `npm ci` (frontend).

## Resuming on a new PC

Follow [SETUP_AND_MIGRATION.md](SETUP_AND_MIGRATION.md) from the top. Nothing needs to be copied from the old PC: the dataset is downloaded again (`python -m src.download_data --with-database-files`).

## After resuming

1. Read "Where I stopped" in [PROJECT_HANDOVER.md](PROJECT_HANDOVER.md).
2. Pick the next item from [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md).
3. Make one small change at a time, run the tests, commit, and push.

---

## Current state at the last pause (29 October 2026)

- Repository: in sync with GitHub. The audit's documentation was committed and pushed as `docs: add comprehensive OpsIQ project handover and reference` (the commit after `ac32a9d`).
- Tests: 89 + 61 + 41 = 191 passing; CI green.
- Not deployed.
- Next action: set up on the new PC, then deploy.
