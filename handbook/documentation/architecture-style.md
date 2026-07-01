# Architecture Documentation Style

**Inherits:** [documentation-style-guide.md](./documentation-style-guide.md)  
**Version:** 1.0.0

---

## Scope

ARCHITECTURE.md, system design sections in docs/, and technical overview documents.

---

## ARCHITECTURE.md Structure

1. **Overview** — system purpose in one paragraph (from `architecture.md` project artifact, distilled)
2. **Context diagram** — mermaid or ASCII; components must match implementation
3. **Component responsibilities** — table: Component | Responsibility | Owner/package
4. **Data model** — schema summary; link to migrations or models
5. **API surface** — link to API.md; no duplicate full contracts
6. **Security** — auth, secrets, trust boundaries (from project `architecture.md`)
7. **Deployment** — high-level; detail in INSTALLATION.md
8. **Decisions** — link to ADRs if present; do not invent ADRs
9. **References** — project `architecture.md`, `spec.md` NFRs

---

## Diagrams

**Prefer mermaid** for GitHub rendering:

```mermaid
flowchart LR
  Client --> API
  API --> DB
```

Rules:

- Node labels match code module or service names
- No decorative complexity
- Legend if non-obvious symbols used

---

## Distinction from Project architecture.md

| Project `architecture.md` | Generated ARCHITECTURE.md |
|---------------------------|---------------------------|
| SDLC phase artifact — design authority | User-facing, stable, published |
| May include planning detail | Shipped system only |
| Owned by Architect | Owned by Documentation Engineer |

Generated doc **summarizes and explains** the approved design — never contradicts it.

---

## NFR Documentation

Map `NFR-*` from `spec.md` to how the architecture satisfies them:

| NFR | Approach | Evidence |
|-----|----------|----------|
| NFR-01 | Rate limiting at API gateway | `middleware/rate_limit.py` |

---

## References

- [documentation-templates.md](../../docs/documentation/documentation-templates.md) § ARCHITECTURE
