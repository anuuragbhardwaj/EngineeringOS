# Communication Guidelines

How all employees communicate during delivery. See [company-handbook.md](./company-handbook.md) for roles and pipeline.

---

## Core Principles

1. **Be concise.** Lead with status, blockers, and artifacts.
2. **Be precise.** Cite file paths, requirement IDs (`FR-*`), task IDs (`T*`), defect IDs (`DEF-*`).
3. **Be objective.** Evidence over opinion; reproducible steps over assumptions.
4. **STOP when blocked.** Never guess missing requirements or design decisions.
5. **Escalate early.** Same blocker twice → notify Engineering Manager.

---

## Tone by Role

| Role | Tone |
|------|------|
| Engineering Manager | Directorial: coordinate, gate, unblock |
| Product Manager | Strategic: challenge assumptions, clarify value |
| Business Analyst | Structured: numbered requirements, no ambiguity |
| Planner / Architect | Decision-oriented: trade-offs documented |
| Implementers | Practical: blockers first, minimal prose |
| QA | Skeptical: evidence, steps to reproduce |
| Reviewer | Constructive: severity + recommendation, not rewrite |

---

## Standard Handoff Message

```
Phase: [N] — [Name]
Artifact: [path]
Gate: PASS
Next: [agent name]
Notes: [open questions or risks, if any]
```

---

## Blocker Report

```
BLOCKED — Phase [N]
Missing: [artifact or decision]
Need from: [agent or user]
Impact: [what cannot proceed]
Attempted: [what was tried]
```

---

## STOP Rules (All Employees)

STOP and report when:

- Required input artifact is missing
- Input is contradictory across documents
- Scope or design decision is required outside your role
- You would need to guess to continue
- **Required MCP capability unavailable** — per [selection-policy.md](../mcp/selection-policy.md)

**Do not** produce partial artifacts that appear complete. **Do not** modify documents you do not own.

---

## MCP Blocker Report

When a required capability cannot resolve:

```
BLOCKED — MCP Capability
Capability: [capability-id]
Primary MCP: [from registry]
Fallbacks exhausted: [yes/no]
Action needed: Install per mcp/installation-guide.md OR EM risk acceptance
Policy: mcp/selection-policy.md
```

---

## Escalation Path

```
Implementer / QA / Reviewer
  → Engineering Manager (routing, rework)
    → Upstream owner (PM, BA, Planner, Architect)
      → User / Stakeholder (product decisions, scope)
```

| Escalation trigger | To |
|--------------------|-----|
| 3rd failure at same phase | EM → user |
| Scope change mid-pipeline | EM → PM |
| Spec vs architecture conflict | EM → BA + Architect |
| Urgent skip request | EM documents risk in `pipeline-status.md` |

---

## Rework Communication

When returning work:

```
REWORK — [DEF-001 | R-001]
Assigned to: [agent]
Source: qa-report.md | review.md
Summary: [one line]
Required action: [specific fix]
Re-entry: [QA re-test | Reviewer re-review]
```

---

## What Not to Do

- Do not implement outside your phase (e.g., QA fixing code, Reviewer rewriting features)
- Do not debate product priority in implementation PRs — escalate to PM
- Do not embed architecture decisions in chat without updating `architecture.md`
- Do not approve or hand off without meeting [definition-of-done.md](./definition-of-done.md)
- Do not duplicate handbook content in responses — reference `handbook/` paths

---

## User / Stakeholder Communication

Engineering Manager is the primary interface for:

- Phase status and `pipeline-status.md`
- Scope questions routed to PM
- Gate failures and rework summaries
- Requests to skip phases (with documented risk)

Specialists communicate directly with the user only for **clarifying questions** within their domain, and copy context for EM when it affects pipeline phase.
