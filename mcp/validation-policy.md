# MCP Validation Policy

**Version:** 1.0.0

---

## Validation Types

| # | Validation | When | Owner |
|---|------------|------|-------|
| V1 | **Registry schema** | On registry edit; CI | `mcp_platform validate` |
| V2 | **mcp.json sync** | On mcp.json edit | `mcp_platform validate --check mcp-json` |
| V3 | **Required MCP exists** | Pre-phase | EM / automated health |
| V4 | **Configuration valid** | Post-install | `mcp_platform health` |
| V5 | **Health check pass** | Pre-gate | EM |
| V6 | **Evidence exists** | Gate review | EM per evidence-policy.md |
| V7 | **Fallback applied correctly** | When fallback used | Artifact footer audit |
| V8 | **Failure recorded** | On MCP failure | pipeline-status.md |

---

## Pre-Gate Validation (EM)

### G3 — Planning

- [ ] `tasks.md` contains structured-reasoning evidence footer
- [ ] sequential-thinking installed or available
- [ ] No hardcoded MCP names in tasks.md

### G4 — Architecture

- [ ] `architecture.md` References section lists documentation-lookup evidence
- [ ] context7 available or fallback documented

### G5 — Implementation

- [ ] Advisory: implementers used documentation-lookup for framework APIs
- [ ] On escalation: EM verifies Context7 usage

### G6 — Testing

- [ ] If E2E claimed: browser-automation evidence in qa-report.md
- [ ] playwright health if browser tests referenced

---

## Automated Validation CLI

```bash
cd ai-company
python -m mcp_platform validate          # all checks
python -m mcp_platform validate --check registry
python -m mcp_platform validate --check mcp-json
python -m mcp_platform validate --check secrets
python -m mcp_platform health
python -m mcp_platform resolve structured-reasoning
```

**Exit code 0** = pass. Non-zero = failures printed to stderr.

---

## Failure Recording

When validation fails, record in `pipeline-status.md`:

```markdown
## MCP Validation Failure
- Date: YYYY-MM-DD
- Capability: [id]
- MCP: [id]
- Check: [V1-V8]
- Action: [STOP | fallback | EM override]
```

---

## workflow.yaml Integration

Phases with `mcp_evidence` blocks reference this policy. Gates fail if evidence requirements not met.

---

## References

- [evidence-policy.md](./evidence-policy.md)
- [health-checks.md](./health-checks.md)
- [selection-policy.md](./selection-policy.md)
