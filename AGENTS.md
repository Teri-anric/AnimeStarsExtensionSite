# AGENTS – Contributor Guide

Welcome!  This document gives both human contributors and code-generation agents the shared context they need to work effectively in this repository.

---

## Repository Overview

| Path | Purpose |
|------|---------|
| `backend/` | Python backend (FastAPI), DB models, migrations, scheduled tasks |
| `frontend/` | React + Vite SPA that consumes the backend OpenAPI |
| `docker/` | Local development Compose stack, environment files, and container build files |
| `deploy/` | Kubernetes production manifests, Terraform-owned app infrastructure, and manual deployment tooling |

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
2. **Spin up the local development stack with Docker**
   ```bash
   cp docker/.env.example docker/.env
   task dev:up  # builds & starts the local stack on http://localhost:8000
   ```
   Compose runs only the local application services. Production observability is managed by the shared K3s infrastructure.
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
| Python | black, isort, flake8, mypy | `python -m black backend` |
| SQL   | sqlfluff (coming soon) |  |
| TypeScript/JS | ESLint, TypeScript | `cd frontend && npm run lint` |
| CSS | Stylelint (via ESLint) | |

Run the relevant tooling locally before opening a PR.

---

## Testing & Validation

* **Python** – `pytest` lives under `backend/`
  Run: `python -m pytest backend`
* **Frontend** – Vitest unit tests (configuration in progress)
  Run: `cd frontend && npm run test`
* **End-to-end** – (WIP) Playwright tests under `e2e/`

All tests plus type & lint checks must pass before merge.

Production runs on the existing K3s cluster. Use `Taskfile.yml` and the
`deploy/` scripts for manual releases; production is not deployed from GitHub
Actions. Shared Traefik, registry, Prometheus, Loki, and Grafana resources are
managed by the cluster infrastructure project, not by this repository.

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

1. Generate: `docker compose --env-file docker/.env -f docker/docker-compose.yaml run --rm backend python -m alembic revision --autogenerate`
2. Apply: `task dev:migrate`
3. Rollback: `docker compose --env-file docker/.env -f docker/docker-compose.yaml run --rm backend python -m alembic downgrade -1`

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
5. Never break CI – run `python -m black backend` and other relevant checks before merge.

---

## FAQ / Tips

* Need to inspect local services? Use `task dev:logs` to follow Compose logs.
* To create a new scheduled task, add it to `backend/app/scheduler/tasks.py` and import in `scheduler.py`.
* Static assets live in `frontend/public/` – reference them with `/assets/...` in code.
* To regenerate the API client, use the npm scripts mentioned in the API Client Generation section.

Happy coding! :tada:
