# Dead Code Report

**Date:** 2026-07-02  
**Project:** Repository cleanup and technical debt reduction

---

## Summary

| Action | Files | Lines removed (approx.) |
|--------|-------|-------------------------|
| Deleted | 2 | ~290 |
| Removed dead fields/abstractions | 2 | ~15 |
| Removed stray artifact | 1 | ~30 |

**External behavior:** Unchanged — 134 tests pass (was 128).

---

## Removed Files

| File | Reason | Evidence |
|------|--------|----------|
| `packages/runtime_engine/src/runtime_engine/agents/em_runner.py` | Superseded by `orchestrator/execution/phase_executor.py` | Zero imports in codebase |
| `packages/runtime_engine/src/runtime_engine/adapters/scaffold.py` | Superseded by `ai_execution/providers/scaffold.py` | Zero imports; live path uses AI Execution scaffold provider |
| `pytest_out.txt` (repo root) | Accidental test output artifact | Not referenced; should not be versioned |

---

## Removed In-Code Dead Paths

| Location | Item | Action |
|----------|------|--------|
| `runtime_engine/runtime/facade.py` | `_validators_extra` list | Removed — `register_validator()` already delegates to `ArtifactValidationEngine.register()` |
| `orchestrator/types.py` | `ExecutionPolicyName` enum | Removed — zero references; policy uses string `name` on `ExecutionPolicy` |

---

## Retained (Intentional Stubs — Not Dead)

| Component | Reason kept |
|-----------|-------------|
| `company_core/api/stubs.py` — `EmployeeAPI`, `IntegrationAPI` | Active Framework API surface; raises `NotImplementedFeatureError` by design |
| `Runtime.register_plugin()` | Contract method; raises `NotImplementedError` per v1 scope |
| `ai_execution/providers/placeholders.py` | Registered placeholder providers by design |

---

## Empty Directories

`packages/runtime_engine/src/runtime_engine/adapters/` — contains no modules after scaffold removal. Directory left in place (git does not track empty dirs); no `__init__.py` existed.

---

## Verification

```bash
pytest tests/ -q   # 134 passed
```

No import errors. No test referenced removed symbols.
