# MCP Installation Guide

**Version:** 1.0.0  
**Date:** 2026-07-01

Install only MCPs you need. Update `mcp/registry.yaml` `installation_status` after verifying.

---

## Prerequisites

- Node.js 18+ and `npx` (for stdio MCPs)
- Cursor IDE with MCP support
- Python 3.11+ (for `mcp_platform` validation)

---

## Project Configuration

1. Copy or merge entries into `ai-company/mcp.json`
2. Mirror to `ai-company/.cursor/mcp.json` for Cursor IDE
3. Run validation:
   ```bash
   cd ai-company
   python -m mcp_platform validate
   ```

---

## Currently Installed (Verified)

### Sequential Thinking ✅

Already in user `~/.cursor/mcp.json`. Add to project `mcp.json`:

```json
"sequential-thinking": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
}
```

**Verify:** `python -m mcp_platform health sequential-thinking`

### Context7 ✅ (Plugin)

No stdio install. Enable **context7-plugin** in Cursor. Invoked via skill or `CallMcpTool`.

**Verify:** Use Context7 skill to resolve a library ID.

---

## Foundation MCPs (Not Installed — Install When Needed)

### Filesystem

```json
"filesystem": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "${workspaceFolder}"]
}
```

### Git

```json
"git": {
  "command": "uvx",
  "args": ["mcp-server-git"]
}
```

Requires `uv` installed. Alternative packages may vary — verify package name before install.

### GitHub

```json
"github": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "<your-token>"
  }
}
```

Set token in environment — never commit.

### Playwright

```json
"playwright": {
  "command": "npx",
  "args": ["-y", "@playwright/mcp@latest"]
}
```

Run `npx playwright install` for browsers.

### Fetch

```json
"fetch": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-fetch"]
}
```

### Terminal

Use Cursor built-in **Shell** tool when Terminal MCP not installed. Dedicated Terminal MCP packages vary — check MCP registry for current package before install.

---

## Database MCPs

| MCP | Prerequisites | Notes |
|-----|---------------|-------|
| SQLite | Package-specific | See MCP marketplace for current server |
| PostgreSQL | `DATABASE_URL` env | Connection string required |
| MySQL | `MYSQL_CONNECTION_STRING` | Connection string required |
| Neo4j | Neo4j instance + credentials | `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` |

Do not install until project `architecture.md` specifies database.

---

## Research MCPs

| MCP | API Key Env Var |
|-----|-----------------|
| Tavily | `TAVILY_API_KEY` |
| Firecrawl | `FIRECRAWL_API_KEY` |
| Exa | `EXA_API_KEY` |

Obtain keys from provider dashboards. Store in user environment or Cursor secrets — never in repo.

---

## Policy-Only MCPs

DevOps, Productivity, Quality, and Observability MCPs are documented in `registry.yaml` with `installation_status: policy_only`. Install when project requires — no company-wide mandate.

---

## Post-Install Checklist

- [ ] Entry in `mcp.json`
- [ ] Entry in `.cursor/mcp.json`
- [ ] Update `registry.yaml` → `installation_status: installed`
- [ ] Run `python -m mcp_platform validate`
- [ ] Run `python -m mcp_platform health <mcp_id>`
- [ ] Restart Cursor IDE

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| MCP not appearing in Cursor | Restart IDE; check `.cursor/mcp.json` syntax |
| npx timeout | Check network; try `npm cache clean --force` |
| Permission denied | Check env vars; see permission-policy.md |
| Server ID mismatch | Use canonical id from registry.yaml |

See [configuration-guide.md](./configuration-guide.md) for advanced setup.
