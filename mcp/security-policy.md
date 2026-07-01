# MCP Security Policy

**Version:** 1.0.0

---

## Principles

1. **Least privilege** — MCPs receive minimum permissions for their capability
2. **No secrets in repo** — credentials in env vars or vault only
3. **Scoped filesystem** — filesystem MCP limited to workspace root
4. **Audit trail** — evidence footers document MCP usage
5. **Kernel isolation** — Company Kernel never imports MCP-specific code

---

## Data Classification

| Class | MCP Handling |
|-------|--------------|
| Public code/artifacts | All MCPs may read |
| Internal business docs | No external research MCPs without EM approval |
| Credentials/secrets | Never pass to MCP prompts; env vars only |
| PII | Do not send to research/web MCPs |
| Production data | Database MCPs read-only in dev; EM approval for writes |

---

## Network Boundaries

| MCP Category | Network |
|--------------|---------|
| sequential-thinking | Outbound (npm) |
| context7 | Outbound (docs API) |
| fetch, tavily, exa | Outbound — public URLs only unless EM approves |
| github | Outbound — authenticated |
| database | Internal network only |

---

## Forbidden Actions

- Committing API keys, tokens, or passwords
- Filesystem MCP writing outside workspace
- Research MCPs querying internal URLs
- Bypassing permission-policy for convenience
- Hardcoding MCP server names in kernel code

---

## Incident Response

1. Revoke compromised credentials immediately
2. Log incident in `pipeline-status.md`
3. EM notifies user
4. Update registry `health_status: unavailable` until resolved

---

## Compliance

- `python -m mcp_platform validate` checks for secrets patterns in mcp.json
- Reviewer checks for leaked secrets in PRs (gitguardian policy when installed)

See [permission-policy.md](./permission-policy.md).
