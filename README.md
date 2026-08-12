# Task Tracker API - Final Project

# Branch reviewed: final-project

https://github.com/alisbeiti/task-tracker/tree/final-project

A learning-focused REST API for managing tasks. Built with **Python**, **FastAPI**, and **Pydantic**, with a small vanilla **HTML/CSS/JS** frontend.

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

## 7. CI Workflow Summary

Defined in `.github/workflows/ci.yml`:

- Triggers: every `push` and every `pull_request`.
- Runs on `ubuntu-latest`.
- Sets up Python 3.11.
- Installs dependencies via `pip install -r requirements.txt`.
- Runs `pytest -v`.

## 8. Evidence files
- docs/release-evidence.md
- docs/final-ai-review.md
- docs/ai-playbook.md

## 9. AI assistance summary
AI helped draft or review: [CI / Docker / docs / security / debugging].
I verified the work by: [tests / diff review / Docker / /health / manual scan].
One AI suggestion I rejected or corrected: AI suggested completing the database table creation, since I had already created the database but did not finish it because it was not required for this course.