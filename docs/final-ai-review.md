# Final AI Review and Ownership Evidence

## AGENTS.md guardrails

- Repo-specific stack and commands included: yes
- Docs-first/read-first guardrail included: yes
- Unexpected app/frontend edits rule included: yes

## AI code review mini-log

| AI comment | Grade: Useful / Noise / Wrong | Reason | Verification or decision |
|---|---|---|---|
| `CLAUDE.md` forbids Docker and CI while the branch adds both. | Wrong | The reviewed comment reflects stale content. The current `CLAUDE.md` says a Dockerfile and CI workflow exist for local containerized and automated test runs. | Checked current `CLAUDE.md:5` and `:101`; rejected this comment as no longer applicable. |
| `storage.add_comment` could raise an unhandled `ValueError` for blank text. | Noise | The route first validates `CommentCreate.text`, which strips and rejects blank text before calling storage. The storage guard is redundant, but the reported HTTP 500 path is not reachable through the current API. | Checked `app/main.py:12-35, 199-225` and `app/storage.py:175-192`; kept this only as future-maintenance awareness. |
| CI does not build or run the Docker image. | Useful | The workflow runs pytest only, while the repo documents Docker as a supported local run path. A Docker build problem would not be detected by current CI. | Checked `.github/workflows/ci.yml:1-23` and `Dockerfile`; recorded as a low-priority coverage gap rather than a course blocker. |

## AI security mini-review

| Finding | File evidence | Grade: Valid / False Positive / Noise | Reason | Next action |
|---|---|---|---|---|
| SEC-01: permissive CORS plus no authentication | `app/main.py:43-49`; `frontend/index.html:665`; `agents.md:97-108` | Valid | This is a real risk if the API is exposed beyond the local learning setup. No authentication is intentional course scope, so it is not a required current-project change. | Keep the app local-only; before a shared deployment, add authorization and restrict CORS to the intended frontend origin. |
| SEC-02: unbounded fields, in-memory growth, and unpaginated task responses | `app/models.py:22-38`; `app/main.py:12-35`; `app/storage.py:9, 67-93` | Valid | Descriptions, assignees, comments, and task/comment counts have no server-side limit. This can matter under untrusted or sustained usage, though the present local scope reduces exposure. | Treat as production-readiness work: add server-side size/quantity limits and pagination if deployment scope expands. |
| SEC-03: no lockfile/hash verification, image digest pinning, or visible vulnerability scan | `requirements.txt:1-7`; `Dockerfile:2, 9-11`; `.github/workflows/ci.yml:11-23` | Noise | The dependencies are directly version-pinned and no vulnerable version or compromised dependency was identified. The finding is general hardening advice, not a demonstrated issue in this course repository. | Do not treat as a current security defect; revisit supply-chain controls only if production deployment is in scope. |

## Manual security check

1 - I checked the field validators in `app/models.py` and the comment validator in `app/main.py` for handling of SQL-like characters. Titles and comments are trimmed and checked for blank values; descriptions and assignees have no equivalent validation. Special characters are accepted, including strings that resemble SQL injection payloads.

This is not currently exploitable because task data is stored in the in-memory Python dictionary in `app/storage.py`; request values are not interpolated into SQL queries. If persistence is added later, the required protection is parameterized queries and safe ORM/database usage—not trying to block SQL characters in validation.

2 - I checked whether the API actually enforces size limits on task fields, by sending a real 5MB description — not just trusting the AI review's claim.

What I found: it went through with no problem — title is capped at 200 characters, but description and assignee aren't, and GET /tasks echoes it all back with no pagination.

## One AI output I rejected or corrected

I rejected the AI code-review comment that claimed the current `CLAUDE.md` forbids Docker and CI while this project adds them. I checked the current file and found that it explicitly documents the Dockerfile and CI workflow as existing local-development and automated-testing support. I treated the comment as stale rather than changing project files based on it.

## Three AI usage rules

1. Never paste secrets, `.env` contents, credentials, or tokens into prompts, source files, or review evidence.
2. Always verify AI claims against the current repository files and supported test or run commands before accepting them.
3. Record AI contributions by noting the claim, the evidence checked, the decision made, and any remaining uncertainty.

## app/ change disclosure: database scaffold

`app/database.py` (SQLAlchemy engine/session/`init_db()`), `sqlalchemy==2.0.35` in
`requirements.txt`, and `DATABASE_URL` in `.env.example`/`app/core/config.py` are
not new work from this branch. `app/database.py` was created in the repository's
initial commit (`b4655d5`, 2026-07-10) — before this final-project branch existed.
Diffing `final-project` against its merge-base with `main` confirms
`app/core/config.py`, `.env.example`, and `requirements.txt` have zero changes on
this branch; `app/database.py` and the `init_db()` startup hook in `app/main.py`
received only a docstring reformat (Google-style), with no schema, model, or
wiring change — the docstring still states the schema is "(currently empty)."

No ORM models are registered against `Base`; `app/storage.py`'s in-memory dict
remains the only place task data is stored. This is already disclosed in
`README.md` (storage model: line 13; no production database claimed: line 15;
`[VERIFY]` empty-schema note: line 71; an AI suggestion to finish wiring the
database was explicitly rejected: line 155). This entry closes the gap of that
disclosure not being repeated in the final-project documentation set.

## Ownership statement

I reviewed the repository guidance, code-review comments, security findings, and manual security-check notes rather than accepting AI output automatically. I verified the cited current files and distinguished course-scope limitations from present defects. I rejected a stale AI claim after checking the current documentation and retained only findings supported by the repository. I understand the project’s local-only, in-memory, and intentionally unauthenticated scope, including what would need to change before broader deployment. I am comfortable submitting this work because the final decisions and verification are my own.
