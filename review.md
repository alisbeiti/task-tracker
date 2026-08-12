# Branch diff review — `final-project` vs `main`

Reviewed: `app/main.py`, `app/models.py`, `app/storage.py`, `app/business_rules.py`, `app/database.py`, `app/api/health.py`, `tests/test_tasks.py`, `Dockerfile`, `.dockerignore`, `.github/workflows/ci.yml`, `CLAUDE.md`, `README.md`, `temp_verify_comments.py` (all changed/added in this branch vs `origin/main`).

---

**file/section:** `CLAUDE.md:5` and `CLAUDE.md:101`, vs `Dockerfile` (new) and `.github/workflows/ci.yml` (new)
**severity:** high
**category:** docs
**issue:** The same diff adds a working `Dockerfile` + CI workflow while also adding a doc file that explicitly forbids exactly that.
**evidence:** `CLAUDE.md:5` — "Runs entirely locally: no Docker, no cloud dependencies... (per docs/mid-course/mini-adr.md)"; `CLAUDE.md:101` — "Do not add deployment steps or configuration (Docker, cloud hosting, CI/CD) — explicitly out of scope per docs/mid-course/mini-adr.md." Both `Dockerfile` and `.github/workflows/ci.yml` are new files in this same diff. Additionally, `docs/mid-course/mini-adr.md` (also new in this diff) never actually mentions Docker/cloud/CI anywhere in its text — it only covers the comments and search features — so the citation doesn't hold up even against the document it names.
**suggested minimal fix:** Reconcile one direction: either drop the "no Docker/no CI/CD" language from `CLAUDE.md` now that both exist, or explicitly note Docker/CI as a separate, later addition outside the mini-ADR's original scope.

---

**file/section:** `app/storage.py:246-248` (`add_comment`) called from `app/main.py:222` (`add_task_comment`)
**severity:** medium
**category:** correctness
**issue:** `storage.add_comment` raises a bare `ValueError` on blank text, but the route that calls it has no exception handler for `ValueError`, so if this branch is ever reached it becomes an unhandled 500, not the 422 the docstring promises.
**evidence:** `app/storage.py`: `cleaned_text = text.strip(); if not cleaned_text: raise ValueError("comment cannot be blank")`; the docstring on this function claims `Raises: ValueError: If the stripped text is empty.` as if that's a handled outcome. `app/main.py:add_task_comment` calls `storage.add_comment(task_id, payload.text)` with no try/except, and no FastAPI exception handler for `ValueError` is registered anywhere in `app/main.py`. Currently unreachable via HTTP because `CommentCreate.validate_text` (`app/main.py`) already strips/rejects blank text before the route body runs — but the guard is broken as written and would surface as a 500 the moment any other caller (e.g., a future internal caller) skips that Pydantic layer.
**suggested minimal fix:** Not asking for a fix now per your constraints — flagging for awareness; if kept, the guard should either be removed (dead code, since `CommentCreate` already guarantees non-blank text) or wired to actually produce a 422.

---

**file/section:** `app/storage.py:12-83` (`_coerce_comments`, `_hydrate_task`, `load_tasks_from_json`, `save_tasks_to_json`)
**severity:** medium
**category:** scope
**issue:** ~70 lines of new JSON load/save/hydrate machinery are added but never called from any route, test, or script in the repo.
**evidence:** `grep` for `load_tasks_from_json`/`save_tasks_to_json` across the repo only matches their own definitions in `app/storage.py` — no caller in `app/main.py`, `tests/`, or `frontend/`. This also edges toward persistence work that `CLAUDE.md:100` explicitly says not to build ("this course intentionally uses in-memory storage").
**suggested minimal fix:** None requested — flagging as unused/untested surface area worth confirming is intentional before it ships.

---

**file/section:** `.github/workflows/ci.yml:1-23`
**severity:** low
**category:** CI / Docker
**issue:** CI only runs `pytest -v`; it never builds or runs the new `Dockerfile`, so a broken image (e.g., the root-owned `/app` directory that previously crashed the container on startup) would not be caught by CI.
**evidence:** `ci.yml` job steps are limited to checkout, Python setup, `pip install -r requirements.txt`, and `pytest -v` — no `docker build`/`docker run` step exists anywhere in the workflow, despite `Dockerfile` being added in this same diff.
**suggested minimal fix:** None requested — noting as a coverage gap given Docker is now part of the branch.

---

**file/section:** `temp_verify_comments.py` (whole file, new)
**severity:** low
**category:** scope
**issue:** A throwaway, print-based manual verification script is committed at the repo root rather than under `tests/`.
**evidence:** File uses `print(...)` statements instead of assertions, is named with a `temp_` prefix, is excluded from the Docker build via `.dockerignore:43`, and is not referenced by `README.md` or `CLAUDE.md`.
**suggested minimal fix:** None requested — flagging as repo clutter outside the two ADR-scoped features (comments, search).

---

**file/section:** `README.md:7` and `README.md:203`
**severity:** low
**category:** docs
**issue:** The claim "task status transitions are restricted" doesn't note that this check only fires on `PATCH`, not on task creation.
**evidence:** `app/main.py:update_task` only calls `validate_status_transition` `if payload.status is not None`; `app/main.py:create_task` never calls it, so `POST /tasks` can create a task with any `status` value (e.g. `"Done"`) with no transition check.
**suggested minimal fix:** None requested — noted from the earlier README audit, still applicable since README.md is part of this diff.

---

**file/section:** `app/business_rules.py:5-9` (`VALID_TRANSITIONS`), vs `tests/test_status_transition.py`
**severity:** low
**category:** test
**issue:** The reverse-of-valid transitions (`Done → ToDo`, `InProgress → ToDo`) and the one other valid transition (`Done → InProgress`) have no test coverage, even though this branch actively touches this test file (`test_tasks.py`'s same-status test was renamed/re-asserted in this diff) and `business_rules.py`'s docstring.
**evidence:** `tests/test_status_transition.py` only covers `ToDo→InProgress` (valid), `ToDo→Done` (invalid), and same-status no-op; `tests/test_tasks.py`'s diff only touches `ToDo→Done` (invalid, pre-existing) and same-status (renamed 422→200). No test in either file exercises `Done→InProgress`, `Done→ToDo`, or `InProgress→ToDo`.
**suggested minimal fix:** None requested — flagging as a coverage gap in an area this diff is actively editing.

---

No issues found in `app/models.py`, `app/database.py`, `app/api/health.py`, or `.dockerignore` beyond what's listed above — those changes are additive docstrings/schema fields consistent with existing code.
