# Task Tracker Smoke Tests

## 5.1C - Repository summary smoke test

| Claim | Evidence file | Evidence summary | Confidence | Assumption to verify |
|---|---|---|---|---|
| The project provides a task-management REST API with task comments. | `README.md`; `app/main.py` | README describes task CRUD and comments; routes include `/tasks` and `/tasks/{task_id}/comments`. | High | None |
| Task data is currently stored in memory and is lost on restart. | `app/storage.py`; `README.md` | Storage uses module-level `_tasks: dict[str, TaskResponse]`; README explicitly says storage is in-memory. | High | None |
| SQLite/SQLAlchemy infrastructure exists but is not confirmed as task persistence. | `app/database.py`; `app/storage.py` | `database.py` defines an engine and `Base`; task operations read and write `_tasks` in `storage.py`. | High | Whether SQLite persistence is planned or intentionally unfinished. |
| Tasks use three statuses and three priorities, with constrained PATCH transitions. | `app/models.py`; `app/business_rules.py` | Statuses are `ToDo`, `InProgress`, `Done`; priorities are `Low`, `Medium`, `High`; transition pairs are explicitly defined. | High | None |
| A static browser-based task board is included. | `frontend/index.html`; `README.md` | Frontend contains board UI and fetches `http://127.0.0.1:8000`; README documents serving the file with Python's HTTP server. | High | Browser behavior was not executed in this review. |

## 5.1D - Recent files smoke test

The timestamps below are the filesystem-metadata snapshot taken before this file was updated with this section.

| File | Modified time | What the file contains | Evidence confidence |
|---|---|---|---|
| `docs/final-project/smoke-test.md` | 2026-08-13 10:05:14 +03:00 | A five-row evidence-based summary table of the Task Tracker repository. | High |
| `docs/final-project/agents.md` | 2026-08-13 10:01:18 +03:00 | Repository guidance covering project facts, commands, business rules, and Module 5 governance guardrails. | High |
| `docs/final-project/release-evidence.md` | 2026-08-12 21:49:38 +03:00 | Recorded local, CI, Docker, and documentation claim-versus-reality evidence for a release review. | High |
