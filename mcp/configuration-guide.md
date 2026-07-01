# MCP Configuration Guide

**Version:** 1.0.0

---

## Configuration Layers

| Layer | File | Scope |
|-------|------|-------|
| Registry (authority) | `mcp/registry.yaml` | All MCP metadata |
| Capabilities | `mcp/capabilities.yaml` | Capability → MCP mapping |
| Project | `ai-company/mcp.json` | Installed MCP processes |
| Cursor IDE | `ai-company/.cursor/mcp.json` | IDE MCP server config |
| User | `~/.cursor/mcp.json` | Developer machine overrides |

**Precedence for execution:** Cursor reads `.cursor/mcp.json`. Project `mcp.json` is canonical for SDK/validation sync.

---

## mcp.json Schema

```json
{
  "$schema": "./mcp/mcp.schema.json",
  "version": "1.0.0",
  "registry": "./mcp/registry.yaml",
  "capabilities": "./mcp/capabilities.yaml",
  "mcpServers": {
    "<mcp_id>": {
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": {}
    }
  }
}
```

Only include MCPs with verified `installation_status: installed`.

---

## Cursor Plugin MCPs (Context7)

Context7 uses `integration_type: cursor-plugin` in registry. Configuration:

- Enable context7-plugin in Cursor settings
- Agents invoke via capability `documentation-lookup`
- No `mcpServers` entry required
- Document usage in artifact References section

---

## Environment Variables

| Variable | MCP | Storage |
|----------|-----|---------|
| `GITHUB_PERSONAL_ACCESS_TOKEN` | github | User env / Cursor secrets |
| `TAVILY_API_KEY` | tavily | User env |
| `DATABASE_URL` | postgresql | User env |
| `NEO4J_URI` | neo4j | User env |

Never commit secrets. See [permission-policy.md](./permission-policy.md).

---

## SDK Bridge Configuration

For `cursor_sdk` agents (`test_sdk.py`):

```python
# Future: pass project MCP allowlist
Agent.create(
    ...
    setting_sources=["project"],  # loads .cursor/mcp.json
)
```

MCP requirements injected per phase from `workflow.yaml` `mcp_evidence` blocks.

---

## Validation

```bash
# Full validation
python -m mcp_platform validate

# Registry schema only
python -m mcp_platform validate --check registry

# mcp.json sync with registry
python -m mcp_platform validate --check mcp-json

# Resolve capability
python -m mcp_platform resolve documentation-lookup

# Health check installed MCP
python -m mcp_platform health
```

---

## Updating Registry

1. Edit `mcp/registry.yaml`
2. Update `mcp/capabilities.yaml` if capabilities change
3. Run `python -m mcp_platform validate`
4. Update `employee-matrix.md` if assignments change
5. No employee prompt edits required

---

## Runtime Kernel Integration

The Company Kernel (`runtime/interfaces.md`) does **not** read MCP config. Future integration:

- `McpEvidencePlugin` validates artifact footers against `evidence-policy.md`
- Subscribes to `ArtifactValidated` events
- No kernel interface changes required

---

## References

- [installation-guide.md](./installation-guide.md)
- [registry.yaml](./registry.yaml)
- [selection-policy.md](./selection-policy.md)
