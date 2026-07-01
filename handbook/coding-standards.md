# Coding Standards

Production code quality for Backend and Frontend engineers. Reviewers enforce via [review-checklist.md](./review-checklist.md). Project overrides in `architecture.md`.

---

## Principles

1. **Match the architecture.** Structure, APIs, and module boundaries follow `architecture.md`.
2. **Satisfy tasks.** Meet acceptance criteria and verify commands in `tasks.md`.
3. **Behavior from spec.** Implement `FR-*` / `NFR-*` in `spec.md`; do not invent requirements.
4. **Minimal scope.** Smallest correct change. No drive-by refactors.
5. **No placeholders.** No `TODO`, `FIXME`, or stubbed production paths at handoff.

---

## General (All Code)

| Area | Standard |
|------|----------|
| Types | Strong typing (Python type hints; TypeScript strict) |
| Naming | Clear, consistent; match project conventions |
| Modules | Single responsibility; small files; explicit exports |
| Errors | Fail explicitly; no silent catches; user-safe messages at boundaries |
| Validation | Validate all external input at API/UI boundary |
| Logging | Structured logs at service boundaries; no secrets in logs |
| Secrets | Environment variables or secret manager; never committed |
| Dependencies | Pin versions; justify new dependencies in commit context |
| Docs | Public APIs documented; non-obvious logic gets a brief comment |

---

## Backend (Python / FastAPI)

| Area | Standard |
|------|----------|
| Layout | Follow `architecture.md` folder structure |
| API | REST conventions; consistent status codes and error shape |
| Auth | Per `architecture.md` Security section; secure defaults |
| Database | Migrations for schema changes; parameterized queries |
| Services | Business logic in service layer; thin route handlers |
| Tests | Unit tests for logic; integration tests for API + DB ([testing-standards.md](./testing-standards.md)) |
| Config | `pydantic-settings` or project pattern; `.env.example` maintained |

---

## Frontend (React / Next.js / TypeScript)

| Area | Standard |
|------|----------|
| Layout | Follow `architecture.md` component structure |
| Components | Reusable; props typed; avoid god components |
| State | Minimal state; server state via project data-fetch pattern |
| API | Use contracts from `architecture.md`; handle loading/error/empty |
| Styling | Consistent with project (e.g., Tailwind); responsive by default |
| Accessibility | Semantic HTML; labels; keyboard nav; WCAG 2.1 AA for Must-Have flows |
| Tests | Component and integration tests per task verify commands |
| Performance | Avoid unnecessary re-renders; lazy-load heavy routes |

---

## Security Defaults

- Authenticate and authorize per `architecture.md` — deny by default
- Sanitize and validate input; encode output appropriately
- No hardcoded credentials, tokens, or API keys
- CORS, rate limits, and headers per architecture
- Dependencies: no known Critical CVEs at handoff

---

## Git / Delivery

- Atomic commits per logical change when possible
- Commit messages: imperative mood; reference task ID if applicable
- Do not commit generated files, secrets, or local IDE config
- All tests pass locally before QA handoff

---

## Out of Scope for Implementers

- Editing `requirements.md`, `spec.md`, `tasks.md`, `architecture.md`
- Redesigning APIs or schema (escalate to Architect)
- Product prioritization (escalate to PM via EM)
- Writing `qa-report.md` or `review.md`
