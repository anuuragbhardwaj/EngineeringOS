# Documentation Style Guide

**Authority:** Master writing standard for all AI Company project documentation  
**Version:** 1.0.0  
**Date:** 2026-07-01

Specialized guides inherit this document:

- [github-style.md](./github-style.md) — README, CONTRIBUTING, repo docs
- [architecture-style.md](./architecture-style.md) — ARCHITECTURE.md, system design
- [api-style.md](./api-style.md) — API reference
- [release-notes-style.md](./release-notes-style.md) — CHANGELOG, RELEASE_NOTES

Standards and SDLC rules: [../documentation-standards.md](../documentation-standards.md)

---

## Purpose

Define how the Documentation Engineer writes — voice, structure, accuracy, and traceability. **Agent prompts must not duplicate these rules.** Update this handbook to change company-wide documentation behavior.

---

## Core Principles

1. **Truth from artifacts** — Every factual claim traces to `spec.md`, `architecture.md`, source code, config, or git history.
2. **Never invent** — If information is missing, state the gap. Do not fabricate APIs, flags, versions, or behavior.
3. **Source over assumption** — Prefer reading code and artifacts over memory or inference.
4. **Concise and scannable** — Short paragraphs, clear headings, tables for comparisons, lists for steps.
5. **GitHub-ready** — Valid Markdown (GFM), renders on GitHub without broken structure.
6. **Maintainable** — Stable section order; templates in [documentation-templates.md](../../docs/documentation/documentation-templates.md).

---

## Voice and Tone

| Do | Don't |
|----|-------|
| Direct, professional, neutral | Marketing hype or vague superlatives |
| Second person for instructions ("Run…") | Passive voice for procedures |
| Present tense for current behavior | Future tense unless describing roadmap |
| Active verbs | Filler ("simply", "just", "easily") |

**Audience:** Professional developers who may be new to the project. Assume competence; define project-specific terms once.

---

## Document Structure

Every document starts with:

```markdown
# Title

**Version:** x.y.z (if versioned)  
**Last updated:** YYYY-MM-DD  
**Status:** draft | current | deprecated
```

Then:

1. **One-paragraph summary** — what this document is and who should read it
2. **Body** — logical sections with `##` headings (max depth `###` unless API reference)
3. **References** — links to source artifacts or external docs (when verified)

No orphaned sections. Every `##` needs at least one sentence of content.

---

## Accuracy Rules

| Rule | Enforcement |
|------|-------------|
| Version numbers match `release.md`, tags, or `package.json` / `pyproject.toml` | Cross-check before G8 |
| Commands are copy-pasteable and tested or marked `unverified` | Run when environment allows |
| File paths exist in the repository | Glob or list before linking |
| API endpoints match `architecture.md` and implementation | Read route definitions |
| Feature lists match `spec.md` Must-Haves only unless labeled roadmap | Traceability matrix |

When uncertain, use:

```markdown
> **Gap:** [what is missing] — source artifact [path] does not define this.
```

---

## Traceability

In `documentation-report.md`, map each generated file:

| Document | Section | Source artifact | Source location |
|----------|---------|-----------------|-----------------|
| README.md | Installation | architecture.md | § Deployment |
| API.md | POST /users | source | `routes/users.py:42` |

Claims without a source row are **violations** — fix before PASS.

---

## Code in Documentation

- Use fenced blocks with language tags: ` ```bash `, ` ```python `
- Snippets must compile or run when marked as examples; otherwise label `illustrative`
- Show minimal viable example — not entire files
- Never include secrets, tokens, or real credentials
- Line length in snippets: prefer ≤ 88 characters for Python, ≤ 100 for shell

---

## Links

- Use relative links within the repo: `[Architecture](./ARCHITECTURE.md)`
- External links: full URL, verify reachable when MCP available
- Anchor headings: lowercase, hyphenated (GitHub auto-anchors)
- No bare URLs — always descriptive link text

---

## Terminology

- **Project** — one SDLC execution (artifact root)
- **Framework** — AI Company Framework product (when documenting ai-company itself)
- **Employee** — AI agent role (internal docs only; use "agent" in public GitHub docs if clearer)
- Use `code` for paths, commands, env vars, and identifiers
- Use **bold** sparingly for UI labels or critical warnings

---

## Warnings and Notes

```markdown
> **Warning:** Destructive or irreversible action.

> **Note:** Optional context that does not block the reader.
```

Use warnings for data loss, security, or production impact.

---

## Confidence Levels

When MCP or source verification is incomplete, annotate in `documentation-report.md`:

| Level | Meaning |
|-------|---------|
| **high** | Verified against source + artifacts |
| **medium** | Verified against artifacts only; code not re-read |
| **reduced** | MCP unavailable or partial; manual review recommended |

---

## Revision Policy

Proposed by Documentation Engineer or any employee. Approved by Engineering Manager. Synchronized with [documentation-standards.md](../documentation-standards.md).

---

## References

- [documentation-standards.md](../documentation-standards.md)
- [documentation-validation.md](../../docs/documentation/documentation-validation.md)
- [documentation-templates.md](../../docs/documentation/documentation-templates.md)
