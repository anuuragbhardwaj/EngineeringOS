# EngineeringOS Technical Debt Register

**Date:** 2026-07-02  
**Purpose:** Inventory debt without prescribing redesign — informs release and backlog prioritization

---

## Debt Summary

| Category | Items | Est. remediation |
|----------|:-----:|------------------|
| Dead code | 4 | Low effort |
| Documentation lag | 6+ docs | Medium effort |
| Placeholder / stub implementations | 8 | Expected for v1 |
| Duplicate abstractions | 5 | Medium effort |
| Unenforced configuration | 3 | Low–medium |
| Missing tests | 3 packages/areas | Medium effort |
| Contract drift | 7 items | Medium (doc + minor code) |

**Overall Technical Debt Score:** **6.5 / 10** (10 = minimal debt)

---

## Dead Code

| Asset | Path | Evidence | Priority |
|-------|------|----------|----------|
| Engineering Manager Runner | `runtime_engine/agents/em_runner.py` | Zero imports; superseded by `orchestrator/execution/phase_executor.py` | **Remove** |
| Scaffold Adapter (kernel) | `runtime_engine/adapters/scaffold.py` | Zero imports; superseded by `ai_execution/providers/scaffold.py` | **Remove** |
| Stub ProjectAPI | `company_core/api/stubs.py` (ProjectAPI class) | Real implementation in `api/project.py`; stub confuses readers | **Remove stub class** |
| `_validators_extra` | `runtime_engine/runtime/facade.py` | Appended never read | **Remove or wire** |

---

## Legacy Compatibility Layers

| Layer | Purpose | Still needed? |
|-------|---------|---------------|
| `specialist` field alias in history | Runtime tests expect `specialist` key | Yes until history schema unified |
| `RuntimeAgentAdapter` lazy import of `runtime_engine.types` | Anti-corruption at boundary | Yes — but should use shared contracts |
| `engineeringos` vs `company` CLI name | Branding migration | Document; optional alias entry point |

---

## Temporary / Placeholder Implementations

| Component | Location | Status |
|-----------|----------|--------|
| `WorkspaceAPI` | `company_core/api/stubs.py` | All methods raise `NotImplementedFeatureError` |
| `EmployeeAPI` | stubs | Same |
| `IntegrationAPI` | stubs | Same |
| `CompanyAPI.create/open/upgrade/migrate` | `api/company.py` | Not implemented |
| `PlaceholderProvider` | `ai_execution/providers/placeholders.py` | By design for claude, openai, gemini, etc. |
| `register_plugin` | `Runtime` facade | Raises `NotImplementedError` |
| CLI `config`, `open`, `workspace` | `company_cli/commands/` | Placeholder handlers |
| `CursorProvider` | `ai_execution/providers/cursor.py` | Prompt load + scaffold; not live Cursor API |

**Assessment:** Placeholders are **acceptable for v1 public preview** if documented. Plugin registration gap is **expected debt** per `plugin-architecture.md` future tier.

---

## Overengineering

| Item | Assessment |
|------|------------|
| Dual history stores (Runtime `execution.history` + `HistoryRecorder`) | **Mild overengineering** — consolidate recording in Orchestrator only |
| `RuntimeLifecycleBridge` duplicating facade advance/gate | **Mild** — could call facade methods instead of duplicating |
| `ExecutionPolicyName` enum unused | **Dead abstraction** — remove or use |
| Checkpoint manager + project PAUSED status | **Overlapping models** — simplify pause semantics |

---

## Underengineering

| Gap | Impact |
|-----|--------|
| No `mcp_platform` tests | Registry regressions undetected |
| Policy timeout not enforced | Silent ignore of `timeout_seconds` |
| MCP evidence flag not enforced | Policy config misleading |
| Checkpoint/approval not persisted | Resume across sessions unreliable |
| No `AgentInvocationFailed` event | Contract gap; observability loss |
| Provider plugin discovery | Adding provider requires code change |
| `company_core` dependency undeclared | Broken standalone install story |

---

## Documentation Debt

| Document | Issue | Status (2026-07-02) |
|----------|-------|----------------------|
| `docs/framework/package-architecture.md` | Was stale | **Aligned** — see [alignment/contract-sync-report.md](../alignment/contract-sync-report.md) |
| `docs/framework/framework-api.md` | Stated "not implemented" | **Aligned** |
| `docs/framework/dependency-map.md` | Missing platforms | **Aligned** |
| `docs/framework/cli-architecture.md` | `company` vs `engineeringos` | **Aligned** |
| `docs/framework/product-ecosystem.md` | CLI "Planned" | **Aligned** |
| `runtime/interfaces.md` | No orchestrator note | **Aligned** — §1.1 added |
| Root `README.md` | Overstated completeness | **Aligned** — honesty matrix |

**Remaining doc debt:** Formal `interfaces.md` v1.1 minor bump to add orchestrator to §3 diagram (optional).

---

## Configuration Debt

| Config | Issue |
|--------|-------|
| `providers.yaml` in package dir | Not overridable via `company.yaml` |
| `policies.yaml` in package dir | Same |
| `mcp.json` vs `.cursor/mcp.json` | Two MCP profile locations |
| Four `discover_framework_root` | Divergent heuristics |

---

## Test Debt

| Area | Tests | Gap |
|------|:-----:|-----|
| `runtime_engine` | 14 | Adequate for v1 |
| `orchestrator` | 10 | Good unit; 1 integration |
| `ai_execution` | 12 | Good |
| `company_cli` | ~15 (root tests) | No command-level unit tests |
| `company_core` API | 5 (config only) | No ProjectAPI/McpAPI tests |
| `mcp_platform` | **0** | **Critical gap** |

**Fragile tests:**
- `test_em_only_direct_invocation` depends on `specialist` key in merged history
- Integration tests assume scaffold provider completes full planning pipeline

---

## Technical Debt by Package

| Package | Debt score (10=low) | Top items |
|---------|:-------------------:|-----------|
| `company_core` | 5.5 | Runtime import, stubs, private API |
| `company_cli` | 8.0 | Naming, thin command tests |
| `runtime_engine` | 7.0 | Dead code, plugin stub, lifecycle duplication |
| `orchestrator` | 7.0 | State mutation, inert policy fields |
| `ai_execution` | 7.5 | Hardcoded providers, Cursor naming |
| `mcp_platform` | 6.0 | No tests, placement |
| Documentation | 5.0 | Constitutional drift |

---

## Recommended Backlog (Post-Audit, Pre-Release)

**Must-fix for architecture honesty (not feature work):**
1. Sync constitutional docs with orchestrator/ai_execution reality
2. Remove `em_runner.py` and kernel `scaffold.py`
3. Add `mcp_platform` test suite (smoke: load, validate, resolve)

**Should-fix for maintainability:**
4. Unify `discover_framework_root`
5. Declare monorepo-only install OR fix `company_core` Runtime coupling
6. Persist checkpoints or document ephemeral limitation in release notes

**Can defer:**
7. Plugin system implementation
8. Real Cursor API provider
9. Workspace/Employee APIs

---

## Debt Trend

```
Pre-orchestrator:  Runtime owned sequencing + provider calls (high coupling)
Post-orchestrator: Correct seams exist; debt is boundary hygiene + doc sync
```

**Conclusion:** Debt is **manageable evolutionary debt**, not **structural bankruptcy**. No major rewrite required — targeted cleanup and documentation alignment sufficient for release with clear known limitations.
