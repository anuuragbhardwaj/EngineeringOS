# Cleanup Report

**Date:** 2026-07-02  
**Project:** Repository cleanup and technical debt reduction  
**Scope:** No new functionality

---

## Objectives Completed

| Objective | Status |
|-----------|--------|
| Remove dead code | ✓ |
| Remove obsolete adapters | ✓ (kernel scaffold adapter) |
| Remove unused stubs | ✓ (duplicate `ExecutionPolicyName`; ProjectAPI stub was already absent) |
| Consolidate duplicate utilities | ✓ |
| Increase test coverage | ✓ (+6 tests) |
| Identical external behavior | ✓ (134/134 tests pass) |

---

## Changes Made

### 1. Dead code removal

- Deleted `em_runner.py` (4,762 bytes)
- Deleted `runtime_engine/adapters/scaffold.py` (6,957 bytes)
- Removed `_validators_extra` write-only list from Runtime facade
- Removed unused `ExecutionPolicyName` enum
- Deleted `pytest_out.txt` artifact

### 2. Utility consolidation

**Problem:** Four divergent `discover_framework_root` implementations in `company_core`, `runtime_engine`, `ai_execution`, and `orchestrator`.

**Solution:** Canonical path discovery in `company_core.config.loader.discover_framework_root_from_path()`:

- Walks upward from `start` or cwd
- Matches `workflow.yaml` + `runtime/` directory
- Falls back to package root heuristic

**Delegates:**

| Package | Now uses |
|---------|----------|
| `runtime_engine.factory` | `discover_framework_root_from_path` |
| `ai_execution.factory` | `discover_framework_root_from_path` |
| `orchestrator.factory` | `discover_framework_root_from_path` |
| `company_core.config.loader.discover_framework_root` | Calls `from_path` before mcp/handbook heuristic |

### 3. Test coverage added

New package: `tests/mcp_platform/test_platform.py` (5 tests)

- Framework root discovery
- Registry validation
- Full validate smoke
- Capability resolution
- `is_usable` helper

Extended: `tests/test_config_loading.py` — `discover_framework_root_from_path` repo test

### 4. Documentation touch-up

- `README.md` Known Limitations — marked dead code removed, consolidation noted

---

## Not Changed (Out of Scope)

| Item | Reason |
|------|--------|
| `EmployeeAPI` / `IntegrationAPI` stubs | Active API contract |
| Orchestrator checkpoint persistence | Behavior change |
| `company_core → runtime_engine` coupling | Architectural change |
| Plugin system implementation | New functionality |
| Policy field enforcement | Behavior change |

---

## Test Results

```
134 passed in ~20s
```

Previous baseline: 128 tests.

---

## Deliverables

| Report | Path |
|--------|------|
| Dead code | [dead-code-report.md](./dead-code-report.md) |
| Cleanup (this) | [cleanup-report.md](./cleanup-report.md) |
| Coverage | [coverage-report.md](./coverage-report.md) |
| Technical debt | [technical-debt-report.md](./technical-debt-report.md) |
