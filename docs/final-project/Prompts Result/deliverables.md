# Module 4 Final Checklist and Reflection

Notes:
1. Verification limits: `gh` CLI isn't installed in this environment, so GitHub Actions run history could not be pulled directly. `README.md` was grepped for a `TechnicalNote.md` link (none found). Where something couldn't be verified, it's marked as such rather than assumed complete.
2. This session has no evidence of Copilot or Cursor being used on this project. The reflection below gives Claude Code a paragraph grounded in what actually happened in this session, and leaves Copilot/Cursor as explicit fill-in templates rather than inventing comparison claims.

## 1. Deliverable Checklist

| Deliverable | Status | Basis |
|---|---|---|
| Claude Code setup | Complete (per your notes) | Not independently checkable beyond `CLAUDE.md` existing and being actively used/edited throughout this session — consistent with the claim, not separately verified. |
| CLAUDE.md verification notes | **Complete** | Directly done in this session: audited `CLAUDE.md` against the actual `Dockerfile`/`ci.yml`, found the "no Docker/no CI-CD" contradiction, logged it in `review.md`/`triage.md`, then fixed `CLAUDE.md` itself (commit `7fe3444`). |
| CI green/red/green evidence | **Missing (not verifiable here)** | `gh` CLI isn't installed in this environment, so GitHub Actions run history couldn't be pulled. Nothing in this session shows an actual red→green cycle — all local `pytest -v` runs were green throughout (37→40 passing), no failure was ever deliberately captured. |
| Docker /health and whoami evidence | **Complete** | Verified multiple times directly in this session: `curl /health` → `200` with the expected JSON body, `docker exec tt-dev whoami` → `app`, `docker inspect` health status → `healthy`. Re-confirmed after the storage.py cleanup too. |
| Documentation claim-vs-reality log | **Complete** | Captured in `review.md` and the earlier audit turn — includes the stale "Module 1" FastAPI description, `{id}` vs `{task_id}` README wording, and the PATCH-only status-transition scoping issue. |
| AI review triage summary | **Complete** | `triage.md` exists with each finding bucketed Useful/Noise/Wrong and evidence cited for each. |
| Technical note path and README link | **Partial / Missing** | `TechnicalNote.md` exists (path confirmed, committed at `03f6657`). The README link does not exist — grepping `README.md` for `TechnicalNote` returns zero matches. README §10 only links `docs/mid-course/mini-adr.md` and the other course docs, not this one. |

## 2. Reflection Draft

**Claude Code:** In this session, Claude Code was used end-to-end for multi-file engineering work that required actually running things, not just writing code: fixing a Dockerfile bug that only showed up when the container was built and run (a root-owned `/app` directory breaking SQLite on startup), auditing documentation against source code across several files at once, triaging its own review findings, and applying only the ones marked Useful — then re-verifying the Docker image and test suite still worked afterward. Its fit is tasks with a build-run-verify loop spanning multiple files and needing terminal/tool access (git, docker, pytest) inside the same workflow, rather than single-function autocomplete.

**GitHub Copilot:** [Fill in from your own usage — no evidence from this session. Copilot's usual strength is inline, in-editor suggestions while you're actively typing a function or test, so a fitting paragraph here would describe how well it worked for small, localized code generation inside a file you were already writing, not for cross-file audits like the ones done above.]

**Cursor:** [Fill in from your own usage — no evidence from this session. Cursor's usual strength is codebase-aware chat/edit inside the IDE, so a fitting paragraph here would describe how it handled tasks like refactors that touch a few related files, compared to how the terminal-native, multi-tool Claude Code session above handled the Docker/CI/docs work.]

**Overall:** No single winner — the deliverable evidence above shows Claude Code's fit for verification-heavy, multi-file, run-it-and-check tasks (Docker builds, doc audits, test-suite fixes). Whichever paragraph you write for Copilot and Cursor, frame it the same way: not "which tool is better" but "which task shape it handled well" — e.g., fast inline completion inside one file vs. codebase-aware in-IDE edits vs. terminal-driven build/verify loops.

## 3. Missing Evidence Still Needed

- **CI red→green proof**: a screenshot or `gh run list --branch final-project` output (or the GitHub Actions UI) showing an actual failing run followed by a passing one — not just local `pytest -v` output, since that never went red in this session.
- **README → TechnicalNote.md link**: `README.md` §10 currently doesn't reference `TechnicalNote.md` at all; this needs to be added before this deliverable is truly complete.
- **Copilot usage notes/evidence** for this project (what task it was used for, what worked/didn't).
- **Cursor usage notes/evidence** for this project (same).
- Confirmation of what "Claude Code setup" evidence actually consists of (e.g., a screenshot, a config file, a specific note) — taken on your word since nothing in this session contradicts it, but there's nothing concrete in-repo to point to either.
