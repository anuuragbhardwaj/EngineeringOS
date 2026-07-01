# Checkpoint Migration Guide

**Date:** 2026-07-02  
**Current schema version:** `1.0.0`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| `1.0.0` | 2026-07-02 | Initial persistent checkpoint format |

---

## File Location

```
.company/checkpoints/orchestrator/{project_id}.yaml
```

---

## Migration Strategy

### Pre-1.0.0 (in-memory only)

No on-disk checkpoints existed. First `create()` after upgrade writes `schema_version: 1.0.0`. No backfill required.

### Future 1.x → 2.x

1. Read `schema_version` from file
2. If missing, treat as `1.0.0` (loader accepts `history` or `checkpoints` key for compatibility)
3. Apply incremental transform functions: `migrate_1_0_to_2_0(data) -> data`
4. Write new version atomically (write temp + rename)

Recommended pattern (not yet implemented — reserved for future):

```python
MIGRATORS = {
    "1.0.0": lambda d: d,  # identity
    # "2.0.0": migrate_1_0_to_2_0,
}

def normalize_checkpoint_file(data: dict) -> dict:
    version = data.get("schema_version", "1.0.0")
    while version in NEXT_VERSION:
        data = MIGRATORS[version](data)
        version = NEXT_VERSION[version]
    data["schema_version"] = version
    return data
```

---

## Backward Compatibility

- `load_project_checkpoints` accepts either `history` or `checkpoints` top-level keys
- Missing `schema_version` defaults to implicit 1.0.0 behavior
- `CheckpointManager(instance_root=None)` retains in-memory-only mode for unit tests without filesystem

---

## Operator Notes

- Checkpoint files are safe to inspect/edit for recovery (YAML)
- Deleting a project checkpoint file resets orchestrator checkpoint history for that project
- Runtime `PipelineState` in `.runtime/state.json` remains separate — orchestrator checkpoints track execution pause/resume metadata
