# MCP Permission Policy

**Version:** 1.0.0

---

## Permission Model

Each MCP in `registry.yaml` declares:

```yaml
permissions:
  filesystem: none | read | read-write | scoped
  network: none | outbound | full
  secrets: none | env-var | vault
```

Employees must verify permissions before invoking capabilities.

---

## Credential Storage

| Method | When | Location |
|--------|------|----------|
| Environment variables | Local dev | `~/.bashrc`, Windows User env, Cursor secrets |
| Cursor MCP env block | Per-server | `.cursor/mcp.json` `env` (values from env, not literals) |
| Vault | Production | External — not in repo |

**Never:** Commit tokens in `mcp.json`, registry, or artifacts.

---

## Required Permissions by Category

| Category | Typical Permissions |
|----------|-------------------|
| Foundation (stdio) | scoped filesystem or none + outbound network |
| Database | outbound network + env-var secrets |
| Research | outbound network + env-var secrets |
| DevOps | outbound + vault secrets |
| policy_only | Documented for future install |

---

## Employee Responsibilities

| Role | Responsibility |
|------|----------------|
| All employees | Request capabilities only; never bypass permission model |
| Backend/Frontend | Do not embed API keys in source code |
| EM | Approve network MCP usage for internal resources |
| Reviewer | Flag secret leaks in review |

---

## MCP-Specific Notes

| MCP | Permission Notes |
|-----|------------------|
| filesystem | MUST scope to `${workspaceFolder}` |
| github | Fine-grained PAT minimum scope |
| postgresql/mysql | Read-only user for dev |
| aws/azure | IAM least privilege |
| git | Read-only for review phase |

---

## Denied Requests

If an MCP requests permission beyond registry declaration:

1. **STOP** invocation
2. Report to EM
3. Do not proceed with elevated permissions without user approval

---

## References

- [security-policy.md](./security-policy.md)
- [registry.yaml](./registry.yaml)
