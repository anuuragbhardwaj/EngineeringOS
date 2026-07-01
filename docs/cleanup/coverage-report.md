# Coverage Report

**Date:** 2026-07-02  
**Baseline:** 128 tests → **134 tests** after cleanup

---

## Full Suite

| Metric | Value |
|--------|-------|
| Total tests | **134** |
| Passed | **134** |
| Failed | 0 |
| Duration | ~20–24s |

---

## New Coverage (This Project)

### `mcp_platform` — previously **0 tests**

| Test | Covers |
|------|--------|
| `test_discover_framework_root_from_path` | Framework root resolution |
| `test_validate_registry_passes` | `validate_registry()` |
| `test_validate_all_smoke` | `validate_all()` integration |
| `test_resolve_documentation_capability` | `resolve_capability()` |
| `test_is_usable_installed` | `is_usable()` helper |

**Package coverage (focused run):**

| Module | Statements | Miss | Cover |
|--------|:----------:|:----:|:-----:|
| `mcp_platform/__init__.py` | 1 | 0 | 100% |
| `mcp_platform/models.py` | 34 | 0 | 100% |
| `mcp_platform/loader.py` | 29 | 1 | 97% |
| `mcp_platform/resolver.py` | 24 | 4 | 83% |
| `mcp_platform/validator.py` | 92 | 16 | 83% |
| `mcp_platform/health.py` | 41 | 41 | 0% |
| `mcp_platform/__main__.py` | 45 | 45 | 0% |

**Note:** CLI entry points (`__main__.py`, `health.py`) remain uncovered — smoke tests exercise library APIs used by `engineeringos mcp` and `python -m mcp_platform validate`.

### `company_core.config.loader`

| Module | Cover (focused) |
|--------|-----------------|
| `loader.py` | 80% |
| New path: `discover_framework_root_from_path` | Covered by mcp + config tests |

### `runtime_engine.factory`

| Module | Cover (focused) |
|--------|-----------------|
| `factory.py` | 83% |

---

## Coverage by Package Area (Existing)

| Area | Test files | Approx. tests |
|------|------------|---------------|
| `runtime_engine` | `tests/runtime/*` | 14 |
| `orchestrator` | `tests/orchestrator/*` | 10 |
| `ai_execution` | `tests/ai_execution/*` | 12 |
| `company_lifecycle` | `tests/company_lifecycle/*` | 12 |
| `workspace_execution` | `tests/workspace_execution/*` | 4 |
| `knowledge` | `tests/knowledge/*` | 10 |
| `source_control` | `tests/source_control/*` | 8 |
| `parallel_execution` | `tests/parallel_execution/*` | 10 |
| `autonomous_company` | `tests/autonomous_company/*` | 15 |
| `mcp_platform` | `tests/mcp_platform/*` | **5 (new)** |
| CLI / core | `tests/test_*.py`, `tests/company_cli` | ~24 |

---

## Remaining Gaps

| Area | Gap | Priority |
|------|-----|----------|
| `mcp_platform/health.py` | No unit tests | Low — CLI wrapper |
| `mcp_platform/__main__.py` | No CLI subprocess tests | Low |
| `company_core.api.project` | No dedicated API tests | Medium |
| Per-command CLI unit tests | Integration-only | Low |

---

## Commands

```bash
pytest tests/ -q
pytest tests/mcp_platform/ -v
pytest tests/ --cov=mcp_platform --cov-report=term-missing
```
