# Task Tracker API

A learning-focused REST API for managing tasks, built with **Python**, **FastAPI**, **Pydantic**, **SQLite**, and **SQLAlchemy**.

This is the Module 1 skeleton: it stands up the FastAPI application, project structure (`core`, `api`, database setup), and a `/health` endpoint only. CRUD endpoints for tasks and the frontend will be added in later modules.

## Project Structure

- `app/core/` — application configuration (environment variables, settings).
- `app/api/` — API route modules (currently just `/health`).
- `app/database.py` — SQLite + SQLAlchemy engine, session, and base setup.
- `app/main.py` — FastAPI application instance and startup wiring.

## Project Description

The Task Tracker application will support creating, viewing, filtering, updating, and deleting tasks while enforcing valid status transitions. Per the project's Architecture Decision Record, the stack is intentionally lightweight and runs entirely on a local machine with no Docker, no cloud dependencies, and no external database server.

Stack:
- Python
- FastAPI
- Pydantic
- SQLite (local file-based database)
- SQLAlchemy (ORM)
- HTML/CSS/JS frontend (separate, added later)
- Pytest + FastAPI TestClient (testing, added later)

## Setup Instructions

1. Ensure you have Python 3.10+ installed.
2. Clone or copy this project folder locally.
3. Create and activate a virtual environment (see commands below).
4. Install dependencies from `requirements.txt`.
5. Copy `.env.example` to `.env` and adjust values if needed.

## Run Command

**Linux/macOS/Windows (with virtual environment activated):**
```bash
uvicorn app.main:app --reload --port 8000
```

On startup, the app will automatically create a local `task_tracker.db` SQLite file (currently with no tables, since no models are defined yet).

The API will be available at `http://localhost:8000`.

## Testing the Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2026-07-09T12:00:00.000000+00:00"
}
```
(The actual `timestamp` value will reflect the current time when the request is made.)

## API Documentation (Swagger UI)

Once the server is running, open the following URL in your browser: