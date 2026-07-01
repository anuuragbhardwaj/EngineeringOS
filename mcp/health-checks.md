# MCP Health Checks

**Version:** 1.0.0

---

## Overview

Health checks verify installed MCPs are operational before phase work requiring capabilities.

**Automated:** `python -m mcp_platform health`  
**Manual:** Procedures below per MCP

---

## Health Status Values

| Status | Meaning |
|--------|---------|
| `healthy` | MCP responding correctly |
| `unknown` | Not checked yet |
| `unavailable` | Server down or misconfigured |
| `not_applicable` | policy_only or not_installed |

---

## Installed MCP Procedures

### sequential-thinking

**Automated:**
```bash
python -m mcp_platform health sequential-thinking
```

**Manual:** Invoke `sequentialthinking` tool with `thought: "health check"`, `nextThoughtNeeded: false`.

**Pass:** Tool returns response without error.

### context7 (plugin)

**Manual:** Invoke Context7 skill — `resolve-library-id` for `react`.

**Pass:** Returns valid library ID.

---

## Not Installed MCPs

Skip health check. Registry `health_status: not_applicable`.

When installed, add procedure here and update registry.

---

## Pre-Phase Health Gate

| Phase | Check |
|-------|-------|
| Planning (G3) | `structured-reasoning` → sequential-thinking healthy |
| Architecture (G4) | `documentation-lookup` → context7 available |
| Implementation (G5) | Advisory — context7 available |
| Testing (G6) | `browser-automation` → playwright healthy (if E2E claimed) |

EM may run `python -m mcp_platform health` before gate review.

---

## Failure Handling

1. Retry once after 30 seconds
2. Try fallback MCP from capabilities.yaml
3. If required capability fails → **STOP** per selection-policy.md
4. Log in `pipeline-status.md` blockers section
5. Update registry `health_status: unavailable`

---

## Scheduled Checks (Future)

- CI job: `python -m mcp_platform health` on registry changes
- Dashboard plugin subscribes to health events

---

## References

- [validation-policy.md](./validation-policy.md)
- [installation-guide.md](./installation-guide.md)
