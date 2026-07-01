# Architecture — Kernel Hardening

**Type:** Implementation alignment (no constitutional change)

## Composition Root Pattern

```
company_cli/main.py
  → runtime_bootstrap (imports runtime_engine.factory.create_runtime)
  → configure_runtime_factory(create_runtime)
  → company_core.api.* uses runtime_bridge.create_runtime()
```

## Runtime Ownership

```
Orchestrator
  → lifecycle.mutator (PipelineStateMutator)
  → PipelineState (owned by Runtime)
```

## Checkpoint Persistence

```
CheckpointManager
  → store.load_project_checkpoints / save_project_checkpoints
  → .company/checkpoints/orchestrator/{project_id}.yaml
```

No new architectural layers. No package renames.
