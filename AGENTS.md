# AGENTS.md

## Cursor Cloud specific instructions

This repo (`HERMES_OAuth-GrokBot`) is the runnable product: a **FastAPI backend**
("Hermes AI LinkedIn Agent") plus a **Streamlit** companion UI. The sibling repo
`HERMES_SuperGrokbot` is an Obsidian notes vault with sync scripts, not a runnable
service.

Ignore the README's `/mnt/c/...` WSL paths — those are the original author's
machine. On the cloud VM the repo lives at its checkout root and runs on plain
Linux (no WSL). A Python virtualenv is created at `.venv` by the update script.

### Services

| Service | Start command (from repo root) | URL |
|---------|-------------------------------|-----|
| FastAPI backend | `.venv/bin/uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload` | http://127.0.0.1:8000 |
| Streamlit UI | `HERMES_BASE_URLS=http://127.0.0.1:8000 .venv/bin/streamlit run streamlit_gematria_hermes.py --server.address=127.0.0.1 --server.port=8501 --server.headless=true` | http://127.0.0.1:8501 |

Start the backend first; the Streamlit sidebar calls it via `HERMES_BASE_URLS`.

### Lint / test / build

- There is **no test suite, linter config, or build step** in this repo.
- The closest thing to a check is `.venv/bin/python validate_manifest.py`, which
  validates `manifest.json` against the expected Hermes tool-schema structure.

### Non-obvious gotchas

- **`gematria_full` module is missing.** `streamlit_gematria_hermes.py` does
  `from gematria_full import GematriaFull`, but that module exists neither in the
  repo nor on PyPI — it is uncommitted application code. As a result the Streamlit
  app shows a red `Unable to import GematriaFull` banner and `st.stop()`s the main
  gematria panel. This is expected with the current repo contents; do NOT try to
  `pip install` it. The **sidebar backend-integration panel still works fully**
  (Refresh health, Load profile, Load background docs, evidence, personas, OAuth
  link), so the frontend↔backend flow is testable without the gematria engine.
- The persistent data store is `data/user_profile.json`, which is gitignored
  (`.gitignore` excludes `/data/*.json`). `POST /profile` writes it; other
  endpoints (`/jobs/match`, `/network/outreach`, `/background/*`) read from it.
- OAuth (`/auth/*`) and the `/chat` proxy are stubs/placeholders and require
  external provider env vars (`OAUTH_*`, `CHAT_PROVIDER_URL`/`OPENAI_API_KEY`) to
  do anything real; they are not needed to run or demo the core app.
- Requires the `python3.12-venv` system package to build the virtualenv (already
  handled by the update script's use of `python3 -m venv`).
