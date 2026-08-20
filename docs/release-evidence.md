# Release Evidence

## Baseline
- Branch: final-project (https://github.com/alisbeiti/task-tracker/tree/final-project)
- Date: 2026-08-12
- Local app run command: `uvicorn app.main:app --reload --port 8000`
- /health result: Ran `uvicorn app.main:app --port 8000` locally (non-Docker) and `curl http://127.0.0.1:8000/health` → `200` with `{"status":"ok","responseCode":"RC-001","timestamp":"2026-08-12T18:36:30.174536+00:00"}`.
- Frontend check: Ran `python -m http.server 5500` and `curl http://localhost:5500/frontend/index.html` → `200`. Confirmed `frontend/index.html` hardcodes `API_BASE = "http://127.0.0.1:8000"` (matches the local backend above); confirmed connectivity by hitting that same API directly — `curl http://127.0.0.1:8000/tasks` → `200 []`. Both processes stopped afterward (ports 8000/5500 confirmed free again).
- Test command: `pytest -v`
- Test result: `40 passed, 7 warnings` (most recent run, after applying the Useful triage fixes)

## CI evidence
- Workflow file: `.github/workflows/ci.yml`
- Latest run link or note: https://github.com/alisbeiti/task-tracker/actions/runs/31600348592/job/94125896842
- Test command used by CI: `pytest -v`
- Shortcut check: confirmed clean — no `continue-on-error`, no `|| true`, pytest is not skipped or made conditional anywhere in `ci.yml`.

## Docker evidence
- Build command: `docker build -t task-tracker:dev .`
- Run command: `docker run -d --name tt-dev -p 8000:8000 task-tracker:dev`
- /health check: `curl http://localhost:8000/health` → `200` with `{"status":"ok","responseCode":"RC-001","timestamp":"..."}` — verified multiple times this session, most recently after the `storage.py` cleanup.
- Non-root check, if implemented: `docker exec tt-dev whoami` → `app` (not `root`); `docker inspect` confirmed healthcheck status `healthy`.
- No-baked-secrets check: `.dockerignore` excludes `.env`, `.git`, virtualenvs, and caches; `Dockerfile` only `COPY`s `requirements.txt` (builder stage) and `app/` (runtime stage) — no credentials or `.env` file enter the image.

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| `CLAUDE.md` said "no Docker, no cloud dependencies..." and "Do not add deployment steps... (Docker, cloud hosting, CI/CD)" | `Dockerfile` and `.github/workflows/ci.yml`, both present in the same branch, read directly | Contradicted — Docker and CI existed in the branch while `CLAUDE.md` forbade them | Edited `CLAUDE.md` (commit `7fe3444`) to remove the "no Docker/no CI-CD" language |
| `README.md` said "Task status transitions are restricted" as a blanket claim | `app/main.py`: `create_task` never calls `validate_status_transition`; `update_task` only calls it when `payload.status is not None` | Overclaimed — the restriction only applies on `PATCH`, not on task creation via `POST` | Reworded `README.md` (§1 and §9) to scope the claim to update via `PATCH` only |
| FastAPI app description in code says "Module 1 Task Tracker REST API skeleton." | `app/main.py`, `FastAPI(title=..., description=..., version="0.1.0")`, read directly; compared against `README.md`/`CLAUDE.md`, both describing the project as Module 4 | Stale — code still says "Module 1" while docs describe Module 4; this text is what actually renders on the live `/docs` page | None yet — flagged as an open item in `review.md`; still needs a fix in `app/main.py` |
| The SQLAlchemy/database scaffold (`app/database.py`, `sqlalchemy` in `requirements.txt`, `DATABASE_URL` in `.env.example`/`app/core/config.py`, `init_db()` at startup) was added as part of this final-project branch | `git log --follow --diff-filter=A -- app/database.py` → created in commit `b4655d5` ("Initial commit", 2026-07-10); `git diff <main merge-base>..final-project` on `app/database.py`, `app/core/config.py`, `.env.example`, `requirements.txt` | Overclaimed — the scaffold predates this branch by ~5 weeks and received no functional change here; no ORM models are registered, `app/storage.py` remains the sole task-data store | None to `app/`; documented the finding here and in `final-ai-review.md` — already disclosed in `README.md` (lines 13, 15, 71, 155) |
