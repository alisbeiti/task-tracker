# Task Tracker API

A learning-focused REST API for managing tasks — Module 4 of the AI-Assisted Coding course. Built with **Python**, **FastAPI**, and **Pydantic**, with a small vanilla **HTML/CSS/JS** frontend.

## 1. Project Overview

The Task Tracker API supports creating, listing (with filters and search), updating, and deleting tasks, plus adding, listing, and deleting comments on a task. When a task's status is changed via `PATCH`, the transition is restricted to a fixed set of valid moves (see [Project Conventions and Current Limitations](#9-project-conventions-and-current-limitations)); this check does not apply to the initial status set at creation time.

Storage is currently **in-memory** (a module-level dict in `app/storage.py`) — task data does not persist across restarts. SQLAlchemy/SQLite are scaffolded in `app/database.py` but not wired to task storage; see [Project Conventions and Current Limitations](#9-project-conventions-and-current-limitations).

This is a local learning project. It does not claim deployment, authentication, a production database, or production readiness.

## 2. Prerequisites

- Python — **[VERIFY]**: no version pin file (`runtime.txt`/`pyproject.toml`) exists in this repo. CI (`.github/workflows/ci.yml`) and the `Dockerfile` both use **3.11**, but the local `.venv`/`venv` folders in this repo were built against **3.12.3**, and an earlier version of this README said "3.10+". Confirm the version your course setup actually expects.
- `pip`
- Git (to clone the repo)
- Docker Desktop or Docker Engine — only needed for [Run with Docker](#6-run-with-docker); not required to run the app locally.

## 3. Local Setup

Run from the repo root.

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
# Windows (cmd.exe or Git Bash)
venv\Scripts\activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy the example environment file:

```bash
# macOS/Linux/Git Bash
cp .env.example .env

# Windows (cmd.exe)
copy .env.example .env
```

## 4. Run the App Locally

With the virtual environment activated, from the repo root:

```bash
uvicorn app.main:app --reload --port 8000
```

- API base URL: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- On startup, the app creates a local `task_tracker.db` SQLite file. **[VERIFY]**: no ORM models are currently registered against `Base`, so this file has no tables — task data actually lives in-memory (see [Project Conventions and Current Limitations](#9-project-conventions-and-current-limitations)), not in this file.

Verify it's up:

```bash
curl http://127.0.0.1:8000/health
```

Expected response shape:

```json
{
  "status": "ok",
  "responseCode": "RC-001",
  "timestamp": "2026-07-09T12:00:00.000000+00:00"
}
```
(The actual `timestamp` value reflects the current time when the request is made.)

### Frontend (optional, separate terminal)

The frontend is a static single-page file that calls the API at a hardcoded `http://127.0.0.1:8000`, so the backend above must already be running.

```bash
python -m http.server 5500
```

Then open `http://localhost:5500/frontend/index.html`.

## 5. Run Tests

With the virtual environment activated, from the repo root:

```bash
pytest -v
```

To run a single file or test:

```bash
pytest -v tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body
```

`tests/verify_a.py` is a standalone manual verification script (prints PASS/FAIL) — it is not part of the pytest suite:

```bash
python tests/verify_a.py
```

## 6. Run with Docker

From the repo root:

```bash
docker build -t task-tracker:dev .
docker run -d --name tt-dev -p 8000:8000 task-tracker:dev
curl http://localhost:8000/health
```

Stop and remove the container when done:

```bash
docker stop tt-dev
docker rm tt-dev
```

Notes:
- The image runs the API only (`uvicorn app.main:app`) — the frontend, tests, and docs are excluded from the build context by `.dockerignore` and are not served by the container.
- The container runs as a non-root user (`app`), not `root`.
- A `HEALTHCHECK` is defined in the `Dockerfile` against `GET /health`.
- `.env` is not copied into the image (excluded via `.dockerignore`), so the container uses the default `PORT`/`APP_ENV`/`DATABASE_URL` values from `app/core/config.py` unless overridden with `docker run -e VAR=value`.
- Storage is in-memory, same as running locally — task data does not persist across container restarts.
- This Docker setup is for local, convenience use only; it is not a deployment or production configuration.

## 7. CI Workflow Summary

Defined in `.github/workflows/ci.yml`:

- Triggers: every `push` and every `pull_request`.
- Runs on `ubuntu-latest`.
- Sets up Python 3.11.
- Installs dependencies via `pip install -r requirements.txt`.
- Runs `pytest -v`.

CI does not build the Docker image, run linting, or publish coverage — it only runs the pytest suite.

## 8. Project Structure

```
task-tracker/
├── app/
│   ├── main.py             # FastAPI app instance, CORS, all routes
│   ├── models.py            # Pydantic v2 schemas (TaskCreate, TaskUpdate, TaskResponse, Comment, enums)
│   ├── business_rules.py    # validate_status_transition() — task status transition rules
│   ├── storage.py           # In-memory task/comment storage (module-level dict)
│   ├── database.py          # SQLAlchemy engine/session/init_db() (scaffolded, not used for storage)
│   ├── core/
│   │   └── config.py         # Settings loaded from .env (PORT, APP_ENV, DATABASE_URL)
│   └── api/
│       └── health.py         # GET /health liveness check
├── frontend/
│   └── index.html            # Vanilla JS/HTML/CSS task board UI
├── tests/
│   ├── conftest.py
│   ├── test_tasks.py
│   ├── test_status_transition.py
│   └── verify_a.py           # Standalone manual verification script (not pytest)
├── docs/mid-course/           # Course deliverables (ADR, user stories, reflection, verification notes)
├── Dockerfile
├── .dockerignore
├── requirements.txt
├── .env.example
└── .github/workflows/ci.yml
```

### Classes and Methods

Classes in `app/` that define their own methods (Pydantic validators), and what each does:

| File | Class | Method | Definition |
|---|---|---|---|
| `app/models.py` | `TaskCreate` | `validate_title(value)` | Validates and normalizes a task title: strips whitespace, rejects a blank title or one over 200 characters, raising `ValueError` (surfaced by FastAPI as `422`). |
| `app/models.py` | `TaskUpdate` | `validate_title(value)` | Same validation as `TaskCreate.validate_title`, but for an optional update — passes `None` through unchanged when the title isn't being updated. |
| `app/models.py` | `Comment` | `validate_text(value)` | Strips whitespace and rejects blank comment text, raising `ValueError` (surfaced by FastAPI as `422`). |
| `app/main.py` | `CommentCreate` | `validate_text(value)` | Same blank-text validation as `Comment.validate_text`, applied to the request body of `POST /tasks/{task_id}/comments`. |

**[VERIFY]**: `Comment.validate_text` (`app/models.py`) and `CommentCreate.validate_text` (`app/main.py`) are two separate, identically-behaving validators rather than one shared implementation — confirm whether that duplication is intentional or should be consolidated.

## 9. Project Conventions and Current Limitations

- **In-memory storage**: all task and comment data lives in a module-level dict in `app/storage.py`. Nothing persists across process/container restarts.
- **SQLite/SQLAlchemy scaffolding is unused**: `app/database.py` creates an empty `task_tracker.db` on startup, but no ORM models are registered against `Base`, and `app/storage.py` never touches this engine. **[VERIFY]** whether this split is intentional (course scope) or storage is meant to move onto this database later.
- **No authentication or authorization** on any endpoint.
- **No production database** — SQLite is scaffolded but not backing storage; see above.
- **Permissive CORS**: `app/main.py` sets `allow_origins=["*"]` with `allow_credentials=True`, so any origin can call the API. This exists because the frontend (port 5500) and API (port 8000) run as separate local servers — it is not hardened for any deployed use.
- **Comments are nested under tasks**, not a top-level resource (`GET/POST /tasks/{id}/comments`, `DELETE /tasks/{id}/comments/{comment_id}`).
- **Status transitions are restricted on update only**: `PATCH /tasks/{task_id}` enforces `ToDo → InProgress`, `InProgress → Done`, `Done → InProgress`, and same-status no-ops; any other transition returns `HTTP 422` (`app/business_rules.py`). `POST /tasks` does not run this check, so a task can be created directly with any status.
- **No pagination** on `GET /tasks`.
- This project does not claim deployment readiness, authentication, a production database, or production readiness of any kind — it is a local learning project only.

## 10. Technical Notes / Decisions

No `docs/decisions` directory exists in this repo. The closest technical/decision note is the Mini Architecture Decision Record:

- [`docs/mid-course/mini-adr.md`](docs/mid-course/mini-adr.md) — covers the task-comments and search/combined-filters feature decisions, including alternatives considered and rejected.

Other course documentation, if useful:
- [`docs/mid-course/user-stories.md`](docs/mid-course/user-stories.md)
- [`docs/mid-course/reflection.md`](docs/mid-course/reflection.md)
- [`docs/mid-course/verification.md`](docs/mid-course/verification.md)
