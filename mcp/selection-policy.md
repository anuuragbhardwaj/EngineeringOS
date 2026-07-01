# MCP Tool Selection Policy

**Authority:** `mcp/capabilities.yaml`, `mcp/registry.yaml`  
**Version:** 1.0.0

---

## Core Rule

**Employees request capabilities. The registry resolves MCPs. Never hardcode MCP server names in prompts or artifacts.**

```
Employee needs: documentation-lookup
       ↓
capabilities.yaml → primary: context7, fallback: fetch
       ↓
registry.yaml → check installation_status
       ↓
Use first installed MCP in chain
```

---

## Selection Priority Order

1. **Required capability for phase** — must resolve or STOP (see employee-matrix.md)
2. **Primary MCP** from `capabilities.yaml`
3. **Fallback chain** — first MCP with `installation_status: installed` or `available`
4. **Built-in Cursor tools** — when documented as fallback (e.g., Shell for `shell-execution`)
5. **STOP** — report to EM if required capability cannot resolve

---

## Fallback Order

For each capability, `capabilities.yaml` defines `fallback_chain`. Resolution algorithm:

```
for mcp in [primary_mcp] + fallback_chain:
    if registry[mcp].installation_status in (installed, available):
        return mcp
if capability.policy_only:
    return STOP with "policy_only — install not required"
return STOP with "no installed MCP for capability"
```

Log fallback usage in artifact footer per [evidence-policy.md](./evidence-policy.md).

---

## Offline Behaviour

| Scenario | Behaviour |
|----------|-----------|
| stdio MCP server down | Retry once; then try fallback; then STOP |
| Context7 plugin unavailable | Use `web-fetch` if installed; else document training-data risk |
| No network | Installed stdio MCPs work; network MCPs STOP |
| policy_only MCP | Do not attempt install; use shell/manual process |

---

## Unavailable MCP Behaviour

1. Check registry `installation_status`
2. If `not_installed` → follow fallback chain
3. If fallback exhausted and capability **required** → **STOP** and report:
   ```
   BLOCKED — Required capability [X] unavailable.
   Primary: [mcp]. Fallbacks exhausted.
   Action: Install per installation-guide.md or EM risk acceptance.
   ```
4. If capability **optional** → proceed without MCP; note in artifact

---

## Multiple MCP Conflict Resolution

When two MCPs satisfy the same capability:

| Rule | Application |
|------|-------------|
| Registry primary wins | Always prefer `capabilities.primary_mcp` |
| Employee required list | If employee has MCP in `required` list, prefer that |
| Health status | Prefer `healthy` over `unknown` |
| Most specific | `git` before `github` for local version-control |
| EM override | EM may document exception in pipeline-status.md |

---

## Permission Handling

1. Check `registry[mcp].permissions` before invocation
2. Never pass secrets in prompts or artifacts
3. Use env vars per [permission-policy.md](./permission-policy.md)
4. Filesystem MCP MUST be scoped to workspace root
5. Deny network MCPs access to internal/credential files

---

## Phase-Specific Rules

| Phase | Required Capabilities | Gate |
|-------|----------------------|------|
| Planning | structured-reasoning | G3 |
| Architecture | documentation-lookup | G4 |
| Implementation | documentation-lookup (advisory) | G5 |
| Testing | browser-automation (if E2E claimed) | G6 |

---

## Adding a New MCP

1. Add entry to `mcp/registry.yaml`
2. Map capabilities in `mcp/capabilities.yaml`
3. Update `employee-matrix.md` if employee assignment changes
4. Add install steps to `installation-guide.md`
5. If installing locally: add to `mcp.json` and run `python -m mcp_platform validate`
6. **Do not** edit employee prompts — they reference capabilities only

---

## References

- [registry.yaml](./registry.yaml)
- [capabilities.yaml](./capabilities.yaml)
- [employee-matrix.md](./employee-matrix.md)
- [evidence-policy.md](./evidence-policy.md)
