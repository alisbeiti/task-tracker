# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

A learning-focused Task Tracker REST API — Module 4 of the AI-Assisted Coding course. Runs entirely locally: no Docker, no cloud dependencies, no external database server (per `docs/mid-course/mini-adr.md`).

## 1. Tech Stack

- **Python** — [VERIFY] `README.md` states a minimum of Python 3.10+; the actual project virtualenvs (`.venv`, `venv`) are built against 3.12.3. No `runtime.txt`/`pyproject.toml` pin was found, so "3.11" could not be confirmed against the repo — check what your course environment actually uses.
- **FastAPI** 0.115.0 (`requirements.txt`)
- **Pydantic** 2.9.2 — v2 (`requirements.txt`)
- **Uvicorn** 0.30.6, `[standard]` extra (`requirements.txt`)
- **pytest** 9.1.1 (`requirements.txt`)
- **httpx** 0.28.1 (`requirements.txt`) — backs `fastapi.testclient.TestClient`
- **SQLAlchemy** 2.0.35 and **python-dotenv** 1.0.1 are also in `requirements.txt`, but see Architecture below — SQLAlchemy is scaffolded, not actually used for storage.
- **Frontend**: vanilla HTML/CSS/JavaScript, single file (`frontend/index.html`). No framework, no build step, no `package.json`.

## 2. Run Command

```bash
uvicorn app.main:app --reload --port 8000
```

Auto-creates `task_tracker.db` on startup. Swagger UI at `http://127.0.0.1:8000/docs`.

Frontend (separate terminal, per `README.md`):
```bash
python -m http.server 5500
# then open http://localhost:5500/frontend/index.html
```

## 3. Test Command

```bash
pytest -v
```

To scope to one file or test: `pytest -v tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body`.

`tests/verify_a.py` is a standalone manual verification script (prints PASS/FAIL), not part of the pytest suite — run directly with `python tests/verify_a.py`.

## 4. Architecture Summary

**Backend** (`app/`):
- `main.py` — FastAPI app, all routes, CORS middleware, `startup` hook calling `init_db()`.
- `models.py` — Pydantic v2 schemas (`TaskCreate`, `TaskUpdate`, `TaskResponse`, `Comment`, `TaskStatus`, `TaskPriority`). All use `ConfigDict(extra="forbid")`.
- `business_rules.py` — `validate_status_transition()`; this is where task status rules live.
- `storage.py` — in-memory persistence: a module-level dict (`_tasks`) holds all task/comment data, keyed by id. Owns CRUD, id generation (`uuid4`), and `created_at`/`updated_at` bookkeeping. Not HTTP-aware (returns `None`/`bool`, never raises `HTTPException`). `storage._reset()` clears it between tests. Comments are nested under their parent task (`TaskResponse.comments`), not a top-level resource. `get_all_tasks()` implements `GET /tasks?status=&priority=&search=&assignee=` as in-memory filtering — `search` matches title/description substrings, `assignee` matches substring, both case-insensitive.
- `database.py` — SQLAlchemy engine/session/`init_db()` against `task_tracker.db`. No ORM models are registered against `Base`, so this currently just creates an empty db file on startup; it is **not** where task data lives.
- `core/config.py` — `Settings` class loading `.env` via `python-dotenv` (`PORT`, `APP_ENV`, `DATABASE_URL`).
- `api/health.py` — `GET /health` liveness check.

**Frontend** (`frontend/`):
- `index.html` (~1165 lines) — the task board UI: fetch-based calls to the API, task list/board rendering, task form, comment panel. Hardcodes `API_BASE = "http://127.0.0.1:8000"`.

**Tests** (`tests/`):
- `conftest.py` — `client` fixture (`TestClient`), `created_task` fixture, autouse `storage._reset()` fixture.
- `test_tasks.py` — task CRUD and validation tests.
- `test_status_transition.py` — status-transition tests (`unittest.TestCase` style).
- `verify_a.py` — standalone manual Pydantic-validation script, run directly (not via pytest).

**Where task rules live**: status-transition rules are in `app/business_rules.py`; field-level validation rules (title, comment text, unknown-field rejection) are in `app/models.py`.

## 5. Business Rules

Task status values (`app/models.py`, `TaskStatus` enum):
- `ToDo`
- `InProgress`
- `Done`

Status transition rules (`app/business_rules.py`, `VALID_TRANSITIONS`), enforced in the `PATCH /tasks/{id}` route only when `status` is included in the payload:
- `ToDo → InProgress`
- `InProgress → Done`
- `Done → InProgress`
- Setting status to its current value is always allowed (no-op)
- Any other transition (e.g. `ToDo → Done`, `InProgress → ToDo`) is rejected with `HTTP 422`

Task priority values (`TaskPriority` enum) — not transition-gated, can be set/changed to any value freely: `Low`, `Medium`, `High`.

Other verified validation rules (`app/models.py`):
- `title`: required, non-blank after `.strip()`, ≤200 characters
- comment `text`: required, non-blank after `.strip()`
- all request/response schemas use `extra="forbid"` — unknown fields are rejected with `HTTP 422`

## 6. UI States and CORS

UI states (`frontend/index.html`, driven by `setState(kind, message)` on `#stateBanner`):
- `loading` — shown while the task list is being fetched (spinner visible)
- `error` — shown when a fetch/save/move request fails
- `empty` — shown when the (possibly filtered) task list has zero results
- `ready` — normal board view

Separate inline error banners exist for the task form (`#formError`) and the comment panel (`#commentError`), independent of the board-level `#stateBanner`.

CORS: `app/main.py` adds `CORSMiddleware` with `allow_origins=["*"]`, `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]` — fully permissive. This is needed because the frontend is served separately (`python -m http.server 5500`) from the API (port 8000); `frontend/index.html` calls the API via a hardcoded `API_BASE = "http://127.0.0.1:8000"`.

## 7. Do-Not Rules

- Do not add authentication/authorization.
- Do not add a database, and do not start actually wiring up the SQLAlchemy engine already scaffolded in `app/database.py` — this course intentionally uses in-memory storage (see Architecture).
- Do not add deployment steps or configuration (Docker, cloud hosting, CI/CD) — explicitly out of scope per `docs/mid-course/mini-adr.md`.
- Do not make major UI changes to `frontend/index.html`.
- Ask first before doing any of the above, rather than assuming it's wanted.
