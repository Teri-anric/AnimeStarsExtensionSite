# AGENTS – Contributor Guide

Welcome!  This document gives both human contributors and code-generation agents the shared context they need to work effectively in this repository.

---

## Repository Overview

| Path | Purpose |
|------|---------|
| `backend/` | Python backend (FastAPI), DB models, migrations, scheduled tasks |
| `frontend/` | React + Vite SPA that consumes the backend OpenAPI |
| `docker/`, `docker-compose*.yaml` | Local dev & production container definitions |
| `caddy/` | Caddy web-server config used in production |

Key entry points:
* **API** – `backend/app/web/main.py` (FastAPI app)
* **DB Models** – `backend/app/database/models/`
* **React App** – `frontend/src/main.tsx`

When adding or editing code, stay inside the relevant folder and keep the existing layering intact (e.g. add a new FastAPI route under `backend/app/web/api/`, not somewhere else).

---

## Dev Environment

1. **Prerequisites**  
   * Docker & Docker Compose (preferred) **or**  
   * Python 3.11 + Node 18
2. **Spin-up with Docker (recommended)**
   ```bash
   make up  # builds & starts the full stack on http://localhost:8000
   ```
3. **Manual setup**
   ```bash
   # backend
   cd backend
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   alembic upgrade head

   # frontend
   cd ../frontend
   npm install
   npm run dev  # runs Vite dev server on http://localhost:5173
   ```

---

## Style & Tooling

| Area | Formatter / Linter | How to run |
|------|--------------------|-----------|
| Python | black, isort, flake8, mypy | `make black` |
| SQL   | sqlfluff (coming soon) |  |
| TypeScript/JS | ESLint, TypeScript | `cd frontend && npm run lint` |
| CSS | Stylelint (via ESLint) | |

CI enforces the same tooling, so run the commands locally before opening a PR.

---

## Testing & Validation

* **Python** – `pytest` lives under `backend/`  
  Run: `make test` or `pytest backend`
* **Frontend** – Vitest unit tests (configuration in progress)  
  Run: `cd frontend && npm run test`
* **End-to-end** – (WIP) Playwright tests under `e2e/`

All tests plus type & lint checks must pass before merge.

---

## API Client Generation

Generate TypeScript API client:
```bash
# For production API
cd frontend
npm run generate-api-client

# For local development
npm run generate-api-client-local
```

---

## Database Migrations

1. Generate: `make migration-autogenerate`
2. Apply: `make migration-upgrade`
3. Rollback: `make migration-down`

---

## Pull-Request Guidelines

* **Title**: `[area] concise title` – examples: `[backend] Add card search endpoint`, `[frontend] Fix card flip animation`.
* **Description** should:
  * Explain **What & Why** (not just how).
  * Link related issues (e.g. `Closes #42`).
  * Include screenshots/GIFs for UI changes.
* Keep PRs focused & under ~500 LOC when possible.

---

## For AI Agents (Cursor, Claude, etc.)

When generating code or docs:
1. Prefer reading existing files with list/read tools over asking the user.
2. Generate **small, incremental edits** with clear intent – one logical change per commit.
3. Use `backend/` or `frontend/` context to decide where to place new code.
4. Update or add tests when you change behaviour.
5. Never break CI – run `make black` and other relevant checks before merge.

---

## FAQ / Tips

* Need to inspect the DB?  Use `make logs` to view container logs or `make psql` to access the database.
* To create a new scheduled task, add it to `backend/app/scheduler/tasks.py` and import in `scheduler.py`.
* Static assets live in `frontend/public/` – reference them with `/assets/...` in code.
* To regenerate the API client, use the npm scripts mentioned in the API Client Generation section.

Happy coding! :tada: 