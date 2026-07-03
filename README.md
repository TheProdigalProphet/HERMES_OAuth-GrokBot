# HERMES_SuperGrokbot

SuperAssistant - Memory focussed - GOAL Driven

## Overview

This repository implements a Hermes Agent-based AI LinkedIn assistant with a constant user profile enhancement.

The agent is designed for `xai-oath [grok-4.20-0309-reasoning]`, and it expects Hermes Agent input forms running on WSL for tool orchestration and profile-aware reasoning.

## Hermes Agent Input

- The persistent user profile is treated as constant memory by the Hermes Agent.
- Tool calls are exposed as agent actions via `/profile`, `/jobs`, and `/network`.
- Prompt templates are structured to let the Hermes Agent reason with long-term goals and persona context.

## Structure

- `src/api` - FastAPI endpoints for auth, profile, jobs, and network
- `src/schemas` - Pydantic schemas for deterministic tool definitions
- `prompts` - Prompt templates for chain-of-thought prompting
- `data` - Local persistent JSON store for profile data
- `scripts` - Utility scripts for environment setup

## WSL Setup

From WSL, run:

```bash
cd /mnt/c/Users/willp/OneDrive/Documents/GitHub/HERMES_SuperGrokbot
chmod +x scripts/setup-wsl.sh
./scripts/setup-wsl.sh
```

Then activate the virtual environment:

```bash
source .venv/bin/activate
```

Start the app with:

```bash
uvicorn src.api.main:app --reload
```

## Hermes Agent sync

After the app is running, sync the agent manifest:

```bash
chmod +x scripts/sync-hermes-agent.sh
./scripts/sync-hermes-agent.sh
```

The manifest now uses Hermes-native structured tool schemas with explicit action definitions and JSON schemas for request and response shapes:
- `profile`: `GET /profile`, `POST /profile`
- `jobs`: `GET /jobs/match`
- `network`: `POST /network/outreach`
- `health`: `GET /health`

Schemas are defined under `#/schemas` and are referenced by each tool action to make agent tooling deterministic.

### Background / elite profile integration

Hermes now supports a background document workflow for profile enrichment:
- `POST /background/document` — add new experience, documentation, or career direction
- `GET /background/documents` — retrieve stored background entries
- `POST /background/elitesummary` — produce an elite profile summary
- `POST /background/sync-profile` — reprocess all background documents and update the persistent user profile

When a new background document is added, Hermes updates `user_profile.json` automatically:
- experience documents append to `profile.experiences`
- career direction documents update `profile.goals`
- notes and documentation append to `profile.summary`
- an extraction step also derives a concise summary statement from each document

A Hermes-native elite profile tool action is now available in the manifest as `eliteProfile`.

## Browser-based OAuth Integration

This repo now includes an auth toolset for browser-based OAuth using `/auth/start`, `/auth/callback`, `/auth/status`, and `/auth/revoke`.

- `GET /auth/start` opens the configured OAuth provider authorization page.
- `GET /auth/callback` receives the OAuth callback and stores a demo access token.
- `GET /auth/status` reports current authorization state.
- `POST /auth/revoke` clears stored authorization data.

For a real provider, configure these environment variables before running the server:

```bash
export OAUTH_CLIENT_ID=<your-client-id>
export OAUTH_AUTHORIZE_URL=https://provider.example.com/oauth/authorize
export OAUTH_TOKEN_URL=https://provider.example.com/oauth/token
export OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback
export OAUTH_SCOPES="openid profile email"
export OAUTH_PROVIDER=linkedin
```

> Note: the current implementation uses a placeholder token exchange. Replace the callback logic with a secure token request to the provider's token endpoint for production use.

## Hermes Gematria Streamlit App

A new Streamlit app is included for browser-based gematria analysis synchronized with your Hermes backend.

Run it with:

```bash
streamlit run streamlit_gematria_hermes.py --server.address=127.0.0.1 --server.port=8501
```

If your Hermes backend is local, set:

```bash
export HERMES_BASE_URLS=http://127.0.0.1:8000
```

This Streamlit app also loads local background personas from `data/background/*.json`.

### Built-in local personas

- `Librarian [Meta-Library]`: A knowledge curator and taxonomy specialist for Hermes, designed to preserve source intent and structure while organizing background documents into library-grade reference knowledge.
- `Expert Software Developer`: A senior engineering advisor focused on FastAPI, Python, OAuth, agent orchestration, and practical system integration guidance.
- `Full-Stack Coding Agent`: A feature-focused Hermes/XAI/OATH engineering persona that helps extend commands, manifest capabilities, and browser/backend interoperability.

### Exporting personas to Hermes

1. Add or edit persona JSON files in `data/background/`.
2. Start the Streamlit app.
3. In the sidebar, click `Publish local persona docs` to push each persona into Hermes via `/background/document`.
4. Use `Load background docs` and `Sync profile` to verify the persona documents are stored and applied to the profile.

### Exporting gematria analysis

- Use the `Persona for export` dropdown to select one of the loaded persona profiles.
- Click `Export analysis to Hermes background` after running a query.
- This creates a Hermes background document tagged as `documentation` and includes the selected persona label.

Then use the app sidebar to launch OAuth, inspect auth state, refresh health, load background documents, and sync the profile.

## Persistent Streamlit Launch

A helper script is included to run Streamlit persistently on WSL:

```bash
cd /mnt/c/Users/willp/OneDrive/Documents/GitHub/HERMES_SuperGrokbot/scripts
chmod +x run-streamlit-nohup.sh
./run-streamlit-nohup.sh
```

This will:
- start `streamlit_gematria_hermes.py` on `127.0.0.1:8501`
- disable CORS and enable XSRF protection for stability
- write logs to `/tmp/streamlit_hermes.log`
- save the process ID to `/tmp/streamlit_hermes.pid`

To stop it:

```bash
kill "$(cat /tmp/streamlit_hermes.pid)"
```

## Hermes Chat proxy

This repo includes a local `/chat` proxy at `http://127.0.0.1:8000/chat`.

Configure one of the following environment pairs before starting the app:

- `CHAT_PROVIDER_URL=https://provider.example.com/chat`
- `CHAT_PROVIDER_API_KEY=<your-api-key>`

or

- `HERMES_CHAT_ENDPOINT=https://provider.example.com/chat`
- `OPENAI_API_KEY=<your-api-key>`

Then you can use the local wrapper with:

```bash
curl -sS -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Using the Family and Criminal Law Defense Wizard persona and all background documents, generate a comprehensive, professional RP Contingency Framework for protecting Leo David Power\'s well-being and supporting the reunification case before the July 2026 deadline. Include risk assessment, protective strategies, legal research angles, relapse prevention, and actionable steps tailored to South Australia DCP processes.", "use_background": true, "profile_aware": true}'
```

The Streamlit app also exposes a `Hermes Chat` panel in the interface, so you can send prompts and review responses from the browser directly.

## Evidence tracker seed

A sample evidence item is available in `data/evidence/sample_evidence_item.json` to help bootstrap the new dashboard.

## Manifest validation

A validation helper is available:

```bash
python validate_manifest.py
```

This checks that `manifest.json` conforms to the expected Hermes schema structure.

If your Hermes CLI is not named `hermes-agent`, set:

```bash
export HERMES_AGENT_CLI=<your-cli-name>
```

## Unified WSL helper

Run this command from your WSL shell (not inside the Hermes Agent UI or prompt):

```bash
cd /mnt/c/Users/willp/OneDrive/Documents/GitHub/HERMES_SuperGrokbot
chmod +x scripts/run-hermes-wsl.sh
./scripts/run-hermes-wsl.sh
```

This is the exact sequence:
1. open WSL
2. `cd` into the repo path
3. run `./scripts/run-hermes-wsl.sh`

This will:
- create and activate `.venv`
- install Python dependencies
- start the FastAPI app on `http://127.0.0.1:8000`
- sync `manifest.json` with Hermes Agent

## Requirements

- `python3`
- `python3-venv`
- `python3-pip`
