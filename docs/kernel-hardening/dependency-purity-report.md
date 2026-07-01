# Dependency Purity Report

**Project:** Kernel Hardening — Project 1  
**Date:** 2026-07-02

---

## Violation (Previous)

```
company_core.api.project
    └── from runtime_engine.factory import create_runtime
    └── Runtime type annotation
```

`company_core` (Framework API / L6) imported Runtime implementation (L3), violating `package-architecture.md` and `dependency-map.md`.

---

## Resolution (New)

### Contract extraction

`company_core/ports/runtime_port.py` defines `IRuntimePort` — a Protocol with the minimum methods `ProjectAPI` needs:

- `init_project`, `execute_planning_pipeline`, `status`, `load_project`, `history`, `validate`
- `list_project_ids`, `project_exists` (added to Runtime facade for API parity)

### Composition-root injection

`company_core/runtime_bridge.py`:

- `configure_runtime_factory(factory)` — register callable
- `create_runtime(**kwargs)` — delegate to factory
- Raises `RuntimeError` if factory not configured

`company_cli/runtime_bootstrap.py` wires `runtime_engine.factory.create_runtime` at CLI startup.

`company_cli/main.py` imports bootstrap before API use.

### ProjectAPI rewrite

`company_core/api/project.py` uses `IRuntimePort` and `runtime_bridge.create_runtime()` — no `runtime_engine` imports.

---

## Verification

AST scan test (`tests/kernel_hardening/test_hardening.py::test_company_core_has_no_runtime_engine_imports`) walks all `company_core` Python files — zero `runtime_engine` import nodes.

Manual grep confirms no matches in `packages/company_core/`.

---

## Architectural Benefit

| Aspect | Effect |
|--------|--------|
| Coupling | Framework API depends on Protocol, not implementation |
| Testability | Tests inject factory via `configure_runtime_factory` |
| Evolution | Runtime can be swapped at composition root without touching `company_core` |

---

## Compatibility Impact

| Surface | Change |
|---------|--------|
| `ProjectAPI` public methods | Unchanged |
| CLI users | No action — bootstrap automatic |
| Library embedders | Must call `configure_runtime_factory()` once |

---

## Documentation Updates

- `dependency-map.md` — remove `CC --> RT` exception (updated in this project)
- `README.md` Known Limitations — remove resolved coupling item
