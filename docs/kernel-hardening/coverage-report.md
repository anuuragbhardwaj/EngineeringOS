# Coverage Report — Kernel Hardening

**Date:** 2026-07-02  
**Test run:** `pytest tests/ -q`

---

## Test Summary

| Metric | Before | After |
|--------|--------|-------|
| Total tests | 134 | **142** |
| New tests | — | **+8** |
| Failures | 0 | 0 |

---

## New Tests

### `tests/kernel_hardening/test_hardening.py` (4 tests)

| Test | Validates |
|------|-----------|
| `test_company_core_has_no_runtime_engine_imports` | AST dependency purity |
| `test_pipeline_state_mutator_owns_mutations` | Runtime mutator API |
| `test_checkpoints_persist_across_manager_instances` | Checkpoint durability |
| `test_runtime_bridge_requires_configuration` | Factory injection guard |

### `tests/mcp_platform/test_health.py` (4 tests)

| Test | Validates |
|------|-----------|
| `test_check_npx_available` | NPX health probe |
| `test_check_context7` | Context7 MCP check |
| `test_check_sequential_thinking_skip_when_not_installed` | Sequential thinking graceful path |
| `test_run_health_checks_smoke` | Full health check orchestration |

### Infrastructure

`tests/conftest.py` — autouse fixture configures `runtime_bridge` for all tests.

---

## Coverage Snapshot (kernel packages)

Command: `pytest tests/ --cov=company_core --cov=runtime_engine --cov=orchestrator --cov=mcp_platform`

| Package | Line coverage | Notable new coverage |
|---------|---------------|----------------------|
| `runtime_engine` | ~75% overall | `state/mutator.py` **97%** |
| `orchestrator` | ~88% overall | `checkpoint/store.py`, `manager.py` persistence paths |
| `company_core` | (included) | `runtime_bridge.py`, `ports/runtime_port.py` |
| `mcp_platform` | (included) | `health.py` doctor paths |

Combined measured total: **78%** line coverage across targeted packages.

---

## Gaps (Acceptable for Hardening Scope)

- Runtime `events/bus.py` — 53% (event bus not primary hardening target)
- Runtime `rework/engine.py` — 33% (out of scope)
- MCP doctor failure injection — smoke tests only; no network failure simulation

---

## Architectural Benefit

Hardening changes have direct regression tests; dependency purity is machine-verified.
