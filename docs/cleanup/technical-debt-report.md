# Technical Debt Report (Post-Cleanup)

**Date:** 2026-07-02  
**Prior baseline:** [docs/audit/technical-debt.md](../audit/technical-debt.md)  
**Debt score before:** 6.5 / 10  
**Debt score after:** **7.2 / 10** (lower debt = higher score)

---

## Resolved in This Project

| ID | Item | Resolution |
|----|------|------------|
| D1 | `em_runner.py` dead code | **Deleted** |
| D2 | Kernel `adapters/scaffold.py` | **Deleted** |
| D3 | `_validators_extra` write-only list | **Removed** |
| D4 | `ExecutionPolicyName` unused enum | **Removed** |
| D5 | Four `discover_framework_root` heuristics | **Consolidated** to `company_core.config.loader.discover_framework_root_from_path` |
| D6 | `mcp_platform` zero tests | **+5 tests** added |
| D7 | `pytest_out.txt` in repo | **Deleted** |

---

## Remaining Debt (Unchanged)

### Structural

| Item | Severity | Notes |
|------|----------|-------|
| `company_core → runtime_engine` import | High | Monorepo coupling via `ProjectAPI` |
| Orchestrator mutates `PipelineState` | High | No Runtime-owned mutation port |
| Ephemeral checkpoint/approval state | High | Resume across process unreliable |

### Stubs / Placeholders (By Design)

| Item | Status |
|------|--------|
| `EmployeeAPI` / `IntegrationAPI` | Stub — planned |
| `register_plugin` | NotImplementedError — planned |
| Placeholder AI providers | By design |
| `CursorProvider` scaffold-only | Documented limitation |

### Configuration

| Item | Status |
|------|--------|
| `timeout_seconds` not enforced | Open |
| `mcp_evidence_required` not enforced | Open |
| `providers.yaml` / `policies.yaml` package-relative | Open |

### Testing

| Area | Status |
|------|--------|
| `mcp_platform` health/CLI | Still untested (library core covered) |
| `company_core.api.project` | No dedicated unit tests |
| CLI per-command unit tests | Integration coverage only |

### Placement

| Item | Status |
|------|--------|
| `mcp_platform` at repo root vs `packages/` | Convention debt — deferred |

---

## Debt Trend

```
Pre-cleanup:  Dead code + duplicate discovery + untested mcp_platform
Post-cleanup:  Boundary hygiene improved; structural debt unchanged
```

**Conclusion:** Cleanup reduced **accidental complexity** without architectural changes. Remaining debt is **documented and manageable** — no rewrite required.

---

## Recommended Next Backlog

1. Add `mcp_platform` health CLI smoke test (subprocess)
2. Persist orchestrator checkpoints or document ephemeral model in runtime state
3. Inject Runtime at CLI composition root to fix `company_core` coupling
4. Formal `interfaces.md` v1.1 minor bump for orchestrator layer

---

## References

- [dead-code-report.md](./dead-code-report.md)
- [cleanup-report.md](./cleanup-report.md)
- [coverage-report.md](./coverage-report.md)
- [docs/audit/technical-debt.md](../audit/technical-debt.md)
