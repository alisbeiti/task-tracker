# Technical Decision Note: Dockerfile Design for the Module 4 Task Tracker

**Status:** Draft
**Scope:** `Dockerfile`, `.dockerignore` — local containerized run of the FastAPI backend only

---

## 1. Context

The Task Tracker started as a course project meant to run entirely locally via `uvicorn app.main:app --reload --port 8000` (see `README.md` §4, `CLAUDE.md` §2). At some point in this branch's history a `Dockerfile` and `.dockerignore` were added so the API could also be built and run as a container, without changing how the app behaves.

The app itself has no database, no authentication, and no deployment target — storage is an in-memory dict in `app/storage.py`, and `README.md` §1/§9 and `CLAUDE.md` explicitly disclaim production readiness. `CLAUDE.md` was recently updated (this session) to stop claiming "no Docker" now that the `Dockerfile` exists, but it still states this is "a local learning project with no cloud deployment" (`CLAUDE.md:5`). Any decision here has to be read in that context: **this is a way to run the existing local app in a container, not a step toward deploying it anywhere.**

The `Dockerfile` builds and serves only the FastAPI backend (`app/`) — the frontend, tests, and docs are excluded from the build context via `.dockerignore` and are not part of the image, per `README.md` §6.

## 2. Decision

Use a **two-stage Dockerfile** (`builder` → `runtime`), both stages on `python:3.11-slim`:

- The `builder` stage creates a venv at `/opt/venv` and installs `requirements.txt` into it.
- The `runtime` stage copies only that venv and the `app/` source into the final image — no build tools, no `requirements.txt`, no pip cache.
- The container runs as a dedicated non-root user (`app`), created with `useradd --create-home --shell /usr/sbin/nologin app`, and `/app` is `chown`'d to that user before the app code is copied in.
- A `HEALTHCHECK` polls `GET /health` every 30s (3s timeout, 5s start period, 3 retries), using `urllib.request` from the standard library so no extra package (like `curl`) is needed in the runtime image.
- `.dockerignore` excludes `.env`, `.git`, virtualenvs, caches, and the dev-only `frontend/`, `tests/`, and `docs/` directories, so the image contains only what `uvicorn app.main:app` needs to run.

This was verified working in this session: the image builds, the container starts, `GET /health` returns `200`, `docker exec ... whoami` returns `app` (not `root`), and `docker inspect` reports the healthcheck as `healthy`.

## 3. Alternatives Considered

- **Single-stage build** (`pip install` directly into the final image, no venv/copy split). Rejected because it would leave `pip`'s build cache and `requirements.txt`-only tooling in the runtime image, increasing image size for no runtime benefit.
- **Run as root** (skip the `useradd`/`chown`/`USER app` steps). Rejected — running application code as root inside a container is an avoidable privilege-escalation surface even for a local learning project, and the fix cost (a few `Dockerfile` lines) is low.
- **No `HEALTHCHECK`**. Rejected — since the app already exposes `GET /health` (`app/api/health.py`), wiring it into `HEALTHCHECK` is close to free and gives `docker ps`/`docker inspect` a real signal instead of just "container process is running."
- **Alpine base instead of `slim`**. **[VERIFY]**: not evaluated in this branch — `python:3.11-slim` (Debian-based) was used without a documented comparison against an Alpine variant (musl libc compatibility with the pinned dependency versions in `requirements.txt` was not checked).
- **Building/running the Docker image in CI**. Not done — `.github/workflows/ci.yml` only runs `pytest -v`; it does not `docker build` or `docker run` the image (see Open Questions).

## 4. Trade-offs

DRAFT - REWRITE IN MY OWN WORDS

- Multi-stage build costs a bit of `Dockerfile` complexity and a slightly longer first build, in exchange for a smaller, cleaner runtime image with no build toolchain in it.
- Running as a non-root `app` user required an explicit `RUN chown app:app /app` step — without it, the app crashed on startup because SQLite couldn't create `task_tracker.db` in a root-owned directory. This was found and fixed manually during this session, not caught automatically, which is itself evidence for one of the open questions below.
- The `HEALTHCHECK` uses `urllib.request` instead of `curl`/`wget` to avoid adding a package to the slim runtime image, at the cost of a slightly less idiomatic-looking healthcheck command.
- `.env` is deliberately excluded from the image (`.dockerignore`), so container config falls back to the defaults in `app/core/config.py` unless overridden with `docker run -e`. That's a reasonable default for a repo with no secrets, but it's a manual step to remember if `PORT`/`DATABASE_URL` ever need to differ from defaults.
- I would do this differently by...

## 5. Consequences

- Anyone can build and run the API in a container with three copy-pasteable commands (`README.md` §6: `docker build`, `docker run`, `curl .../health`), without installing Python locally.
- The container is non-root and has a working healthcheck, so `docker ps`/`docker inspect` give an honest signal about whether the app actually started — this is what caught the original root-ownership bug during manual testing.
- Because storage is in-memory (`app/storage.py`), task data created inside a container is lost on `docker stop`/`docker rm`, identical to restarting the local `uvicorn` process. The Dockerfile does not change or hide this.
- The `Dockerfile`'s correctness currently depends entirely on manual verification (as done in this session) — there is no automated check that a future change to `app/` or the `Dockerfile` doesn't break the image, since CI never builds it.
- `CLAUDE.md`'s Do-Not Rules had to be updated (this session) because they previously forbade exactly this Docker/CI work; that update is itself a consequence of this decision existing, not a cause of it.

## 6. Open Questions

DRAFT - REWRITE IN MY OWN WORDS

- Should CI (`.github/workflows/ci.yml`) build and smoke-test the Docker image on every push, given the root-ownership bug that manual testing caught was never something automated tests would have exercised?
- [VERIFY]: is `python:3.11-slim` the version the course actually wants pinned, given `README.md`/`CLAUDE.md` both flag that the local dev venvs were built against 3.12.3 and no `runtime.txt`/`pyproject.toml` exists anywhere in the repo to settle it?
- Is a `HEALTHCHECK` even meaningful here, given nothing in this repo currently orchestrates the container (no `docker-compose`, no restart policy, no supervisor reading the health status)?
- Should the image accept `PORT`/`DATABASE_URL` overrides more explicitly (e.g., documented `docker run -e` examples), or is relying on `app/core/config.py`'s defaults sufficient for a local-only tool?
- Now that `Dockerfile`/CI exist and `CLAUDE.md` was edited to stop forbidding them, is there a follow-up decision needed about how far "local container use" is allowed to grow before it counts as the "deployment steps" `CLAUDE.md` still says not to add?
