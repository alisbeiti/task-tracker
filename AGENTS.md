# AGENTS.md — Task Tracker

## Project summary

Task Tracker is a learning-focused REST API for creating, listing, filtering,
updating, and deleting tasks, with task comments. It has a small static
HTML/CSS/JavaScript task-board frontend.

The backend currently stores tasks in a module-level in-memory dictionary.
`app/database.py` initializes a SQLite/SQLAlchemy scaffold, but no confirmed
ORM task model is wired to it; task data is therefore not persistent across
application restarts.

Evidence: `README.md`, `app/main.py`, `app/storage.py`, `app/database.py`,
and `frontend/index.html`.

## Tech stack

- Python with FastAPI and Pydantic.
- Uvicorn ASGI server.
- Pytest and FastAPI TestClient for automated tests.
- SQLAlchemy and SQLite are present but task persistence through them is not
  confirmed.
- Static vanilla HTML/CSS/JavaScript frontend.

Evidence: `requirements.txt`, `app/main.py`, `app/database.py`,
`frontend/index.html`, and `tests/`.

## Confirmed commands

Run commands from the repository root.

```powershell
python -m venv venv
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
pytest -v
python tests/verify_a.py
python -m http.server 5500
```

- The frontend is served at `http://localhost:5500/frontend/index.html` and
  calls the API at `http://127.0.0.1:8000`.
- Docker commands are documented in `README.md`, but are not confirmed here
  as part of the normal local workflow.
- A required Python version is not confirmed by a version-pin file.

Evidence: `README.md`, `requirements.txt`, and `frontend/index.html`.

## Confirmed business rules

### Tasks

- Status values: `ToDo`, `InProgress`, `Done`.
- Priority values: `Low`, `Medium`, `High`.
- New tasks default to status `ToDo`, priority `Medium`, empty description,
  and no assignee.
- Titles are trimmed, required, non-blank, and limited to 200 characters.
- Request models forbid unknown fields.
- List filtering supports `status`, `priority`, `search`, and `assignee`.
  Search matches title and description case-insensitively; assignee filtering
  is a case-insensitive substring match. Blank search/assignee filters do not
  filter results.
- PATCH updates only supplied fields. An explicit `null` for an optional
  field is applied as an update; confirm this behavior is intended before
  changing it.
- Allowed status transitions are:
  - `ToDo` → `InProgress`
  - `InProgress` → `Done`
  - `Done` → `InProgress`
  - Updating to the same status is allowed.
- Initial task creation accepts any declared status; transition validation is
  applied only when PATCH includes a status.

### Comments

- Comments belong to an existing task.
- Comment text is trimmed and must not be blank.
- Adding or deleting a comment updates the parent task's `updated_at` value.

Evidence: `app/models.py`, `app/main.py`, `app/storage.py`,
`app/business_rules.py`, and `tests/`.

## Working guardrails

- Treat each Codex task/thread as one bounded task.
- Start docs-first and read-only by default.
- Do not change `app/` unless the user explicitly approves one specific,
  minimal fix.
- Prefer documentation-only work during Module 5. Do not modify files outside
  `docs/` unless explicitly authorized; `AGENTS.md` is permitted when the
  user asks for it.
- Before editing, state the understood task, files to inspect, and whether
  edit permission is needed.
- Preserve unrelated working-tree changes.

## Security and governance

- Never paste, expose, log, or commit secrets. Treat `.env` and credentials
  as sensitive; use `.env.example` only as a non-secret template.
- Do not run destructive commands or resets without explicit user approval
  and a verified target.
- Make repository claims only from inspected evidence. Cite the relevant file
  paths in findings and clearly label anything not visible as **not
  confirmed**.
- Do not invent test results, deployment status, database persistence,
  authentication, or production-readiness claims.
- Keep changes minimal, reviewable, and scoped to the user's approved task.

## Verification expectations

- For documentation/governance work, inspect cited source files and report
  uncertainty.
- For approved code changes, run the narrowest relevant supported test first,
  then report the exact command and result.
- `tests/verify_a.py` is a standalone manual verification script, not a
  confirmed part of the pytest suite.

Evidence: `README.md`, `tests/conftest.py`, `tests/test_tasks.py`,
`tests/test_status_transition.py`, and `tests/verify_a.py`.
