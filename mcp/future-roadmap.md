# MCP Platform — Future Roadmap

**Version:** 1.0.0  
**Supersedes:** `mcp-roadmap.md` (historical reference)

---

## Phase 1 — Complete ✅

- Central registry (`mcp/registry.yaml`)
- Capability mapping (`mcp/capabilities.yaml`)
- Governance policies (8 documents)
- Employee matrix and capability-based agent prompts
- workflow.yaml MCP evidence gates
- `mcp_platform` validation tooling
- Installed: sequential-thinking, context7 (plugin)

---

## Phase 2 — Foundation Rollout (Next)

| Priority | MCP | Unblocks |
|----------|-----|----------|
| 1 | filesystem | Scoped file ops |
| 2 | git + github | Review/release automation |
| 3 | playwright | E2E evidence for G6 |
| 4 | fetch | Context7 fallback |

---

## Phase 3 — Database & Research

Install per project need:
- sqlite / postgresql for backend projects
- tavily / exa for PM/BA research phases

---

## Phase 4 — DevOps & Observability

Promote from policy_only when release phase needs:
- docker + kubernetes for deploy verification
- sentry for error tracking integration
- grafana/prometheus for monitoring

---

## Phase 5 — Productivity & Quality

- linear/jira for issue traceability
- semgrep/gitguardian in review pipeline
- promptfoo for LLM feature testing

---

## Phase 6 — Runtime Integration

- `McpEvidencePlugin` on Company Kernel event bus
- SDK bridge passes MCP allowlist to agents
- CI: `mcp_platform validate` on registry PRs
- Auto-sync mcp.json from registry installed entries

---

## Phase 7 — Advanced

- MCP proxy server for multi-agent sharing
- Cost tracking plugin per MCP invocation
- Company memory plugin on research MCP results
- Distributed MCP for remote agents

---

## Adding MCPs

Always: registry → capabilities → validate → install guide. Never: employee prompt edits.

See [selection-policy.md](./selection-policy.md).
