# Tech Stack

Default technology choices for greenfield projects. **Per-project authority: `architecture.md`** — always follow the architect's documented stack for the active feature.

---

## Stack Hierarchy

1. `architecture.md` (project-specific, final)
2. This document (company defaults)
3. Existing codebase conventions (brownfield)

When in conflict, `architecture.md` wins.

---

## Backend Defaults

| Concern | Default |
|---------|---------|
| Language | Python 3.11+ |
| Framework | FastAPI |
| Server | Uvicorn |
| Validation / settings | Pydantic, pydantic-settings |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic (when schema evolves) |
| Auth | JWT (python-jose); passwords via passlib[bcrypt] |
| HTTP client (tests) | httpx |
| Testing | pytest, pytest-cov |
| Linting / format | ruff (or project standard) |
| Container | Docker; compose for local multi-service |

---

## Frontend Defaults

| Concern | Default |
|---------|---------|
| Framework | React 18+ |
| Meta-framework | Next.js (App Router) when SSR/routing needed |
| Language | TypeScript (strict) |
| Styling | Tailwind CSS |
| Forms / validation | Project standard (e.g., react-hook-form + zod) |
| Testing | Vitest or Jest; Playwright for E2E |
| Linting | ESLint + Prettier |

---

## Data Stores

| Use case | Default |
|----------|---------|
| Local / dev / small services | SQLite |
| Production RDBMS | PostgreSQL |
| Caching (when required) | Redis — document in `architecture.md` |

Architect selects per project; document connection pooling and migration strategy.

---

## API Conventions

| Topic | Standard |
|-------|----------|
| Style | REST, JSON |
| Versioning | URL prefix `/api/v1` or per `architecture.md` |
| Errors | Consistent JSON shape: `code`, `message`, optional `details` |
| Auth | Bearer JWT unless architecture specifies otherwise |
| Docs | OpenAPI from FastAPI `/docs` for backend |

---

## Infrastructure & DevOps

| Concern | Default |
|---------|---------|
| Containers | Docker; multi-stage builds for production |
| Local dev | docker-compose.yml when multiple services |
| CI | Run lint + tests on every PR (project pipeline) |
| Secrets | `.env` locally; never commit; `.env.example` checked in |
| Logging | Structured JSON in production when feasible |

Implementation of deployment pipelines is defined per task in `tasks.md` / `architecture.md`. No dedicated DevOps agent — Backend or Architect owns container config unless user assigns otherwise.

---

## MCP & Tooling

**Authority:** [mcp/](../mcp/) MCP Platform. Employees request **capabilities** — never hardcode MCP names.

| Capability | Primary role | Purpose |
|------------|--------------|---------|
| `structured-reasoning` | Software Planner | Task decomposition before `tasks.md` |
| `documentation-lookup` | Architect, Backend, Frontend | Current library/framework docs |
| See [employee-matrix.md](../mcp/employee-matrix.md) | All | Full assignments |

**Validation:** `python -m mcp_platform validate`

## Adding or Changing Stack

1. Propose in `architecture.md` with rationale.
2. Update affected tasks in `tasks.md` if dependencies shift.
3. Do not change stack silently in implementation — escalate to Architect.

New dependencies require justification (security, license, maintenance burden) in implementation notes or `architecture.md`.
