# GitHub Documentation Style

**Inherits:** [documentation-style-guide.md](./documentation-style-guide.md)  
**Version:** 1.0.0

---

## Scope

README.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md (when requested), `.github/` templates, and repository landing-page content.

---

## README.md Structure

Use this order unless project type justifies omission (document omission in `documentation-report.md`):

1. **Title + one-line description**
2. **Badges** (optional) — only if CI/version badges exist and are accurate
3. **Overview** — 2–4 sentences: problem, solution, audience
4. **Features** — bullet list from `spec.md` Must-Haves / shipped scope only
5. **Quick Start** — minimal path to running locally (5 steps max)
6. **Installation** — link to INSTALLATION.md or inline if short
7. **Usage** — link to USAGE.md or one canonical example
8. **Documentation** — table linking to docs/
9. **Development** — link to CONTRIBUTING.md, test command
10. **License** — SPDX identifier or "TBD"

### README rules

- First screen (before scroll) must answer: *What is this?* and *How do I try it?*
- No internal SDLC jargon (`FR-*`, gate IDs) in public README
- Screenshots only when UI exists and files are committed
- "Table of contents" optional for README &lt; 200 lines

---

## CONTRIBUTING.md Structure

1. Welcome + code of conduct reference
2. Prerequisites (tool versions from `architecture.md`)
3. Setup steps (same as dev quick start)
4. Branch / PR conventions (from handbook or architecture)
5. Running tests — exact command from `tasks.md` verify commands
6. SDLc note (internal projects only) — link to company handbook if repo is ai-company

---

## Repository Layout Documentation

When documenting folder structure:

```
project/
├── src/           # brief purpose
├── tests/
└── docs/
```

Every listed path must exist. Comment each top-level directory in one line.

---

## GitHub Templates

Issue and PR templates (when generated):

- YAML frontmatter with name, about, labels
- Checklist items traceable to review/QA expectations
- No assignment of internal employee names in public templates

---

## Markdown Conventions

- ATX headings (`#`) only
- Tables for feature comparison, not for prose
- Collapsible `<details>` sparingly — prefer flat structure

---

## References

- [github-documentation.md](../../docs/documentation/github-documentation.md)
- [documentation-templates.md](../../docs/documentation/documentation-templates.md) § README
