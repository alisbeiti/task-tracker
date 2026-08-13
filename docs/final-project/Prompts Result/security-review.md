# Security Review — Task Tracker

| ID | Severity | File / location | Finding | Evidence | Suggested next step | Confidence |
|---|---|---|---|---|---|---|
| SEC-01 | Medium* | `app/main.py:43-49` | The API permits cross-origin reads and state-changing requests from any origin. With no authentication, this makes the full task/comment dataset and mutations accessible to arbitrary websites whenever the API is network-reachable. | CORS allows `*` origins, methods, and headers, including credentials; all task and comment CRUD routes have no access control. The frontend uses only `http://127.0.0.1:8000` (`frontend/index.html:665`). | Keep the service local-only as documented. Before any shared/network deployment, add authentication/authorization and replace `*` with the exact frontend origin; set `allow_credentials=False` unless credentialed auth is deliberately implemented. | High |
| SEC-02 | Medium | `app/models.py:31-38`, `app/main.py:12-35`, `app/storage.py:9, 67-93` | Several client-controlled strings and collections are unbounded, enabling memory, CPU, or response-size exhaustion. | Titles are capped at 200 characters (`app/models.py:22-28`), but `description`, `assignee`, and comment text have no server-side maximum. Tasks are retained indefinitely in a process-global dictionary, and `GET /tasks` returns every task—including nested comments—without pagination. | If the API will receive untrusted or sustained traffic, add server-side field and request-size limits, task/comment quotas, and pagination. Frontend `maxlength` is bypassable. | High |
| SEC-03 | Low | `requirements.txt:1-7`, `Dockerfile:2, 9-11`, `.github/workflows/ci.yml:11-23` | Dependency supply-chain integrity is only partially controlled: direct packages are version-pinned, but there is no lockfile/hash verification, image digest pinning, or visible vulnerability scan. | CI and Docker install directly from `requirements.txt`; the image uses the mutable `python:3.11-slim` tag. | For a production path, generate a locked, hash-checked dependency set, pin the base image by digest, and add dependency/image vulnerability scanning to CI. No specific vulnerable pinned dependency is asserted by this review. | High |

\* The authorization-free design is intentionally documented for this local course project, so SEC-01 is a deployment-boundary finding rather than a request to change the current assignment scope (`docs/final-project/agents.md:97-105`, `CLAUDE.md:97-103`).

## Files inspected

- Backend: `app/main.py`, `app/models.py`, `app/storage.py`, `app/database.py`, `app/business_rules.py`, `app/core/config.py`, `app/api/health.py`, and package initializers.
- Tests: `tests/conftest.py`, `tests/test_tasks.py`, `tests/test_status_transition.py`, `tests/verify_a.py`.
- Frontend: `frontend/index.html`.
- Configuration/deployment: `requirements.txt`, `Dockerfile`, `.dockerignore`, `.gitignore`, `.env.example`, `.github/workflows/ci.yml`.
- Project guidance/docs: `README.md`, `CLAUDE.md`, `docs/final-project/agents.md`. No root-level `AGENTS.md` exists; the latter is the available project-specific equivalent.

## Categories where no issue was found

- Enum and unknown-field handling are strict: request models use `extra="forbid"` and status/priority use enums.
- Title and blank-comment validation are present; tests cover invalid enums, unknown fields, blank titles, and blank comments.
- No hardcoded secrets or tracked credential files were found; `.env` is ignored and excluded from Docker builds.
- No application debug mode, custom stack-trace response, broad route-level exception handler, or frontend `innerHTML` injection of API data was found. Dynamic task/comment text is rendered with `textContent`.
- Docker runs as a non-root user and excludes the frontend, tests, local database, and `.env` from the runtime image.

## Assumptions and audit limits

- This was a read-only static review; the application, tests, Docker build, dependency scanner, and penetration tests were not run.
- No compose or `pyproject.toml` file was present.
- Findings assume the API could eventually be reachable beyond the local machine; the documented present scope is local-only and intentionally unauthenticated.
