# Checkpoint Design

**Project:** Kernel Hardening — Project 3  
**Date:** 2026-07-02

---

## Problem

`CheckpointManager` stored checkpoints in memory only. Process restart, pause/resume across sessions, and crash recovery lost orchestrator checkpoint history not mirrored elsewhere.

---

## Design

### Storage location

```
{instance_root}/.company/checkpoints/orchestrator/{project_id}.yaml
```

Consolidates orchestrator checkpoint state inside the company workspace under `.company/`, alongside existing `state/`, `history/`, `knowledge/`, and `session/` paths.

### Schema

```yaml
schema_version: "1.0.0"
project_id: <id>
checkpoints: [...]
history: [...]
```

Each checkpoint record:

| Field | Type |
|-------|------|
| `checkpoint_id` | UUID string |
| `project_id` | string |
| `phase_id` | string |
| `employee_id` | string |
| `created_at` | ISO datetime |
| `status` | `active` \| `paused` \| `completed` \| `rolled_back` |
| `metadata` | dict |

### Components

| Module | Role |
|--------|------|
| `orchestrator/checkpoint/store.py` | Load/save YAML, path helpers, serialize/deserialize |
| `orchestrator/checkpoint/manager.py` | CRUD + lazy load per project + persist on mutations |
| `orchestrator/orchestrator.py` | Passes `instance_root` to `CheckpointManager` |

### Lifecycle

1. `create()` — append checkpoint, persist
2. `pause()` / `complete()` / `rollback()` — update status, persist
3. New `CheckpointManager(instance_root=...)` — `_ensure_loaded()` reads YAML before operations

---

## Durability Guarantees

| Scenario | Supported |
|----------|-----------|
| Pause within process | ✓ |
| Resume new process | ✓ (loads from disk) |
| Crash mid-checkpoint | ✓ (last persisted write survives) |
| Machine reboot | ✓ (filesystem-backed) |

---

## Non-Duplication

Reuses existing YAML persistence pattern (same as knowledge/session files). Does not introduce a second database or parallel checkpoint system.

---

## Architectural Benefit

Workspace-local, inspectable checkpoint files; version field enables future migrations without redesign.
