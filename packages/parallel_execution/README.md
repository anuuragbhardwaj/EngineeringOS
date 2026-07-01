# Parallel Execution Engine

Concurrent employee execution with deterministic scheduling.

## Philosophy

- Parallelism never changes project correctness
- Independent work executes concurrently; dependent work sequentially
- Deterministic execution over maximum parallelism

## API

```python
api.parallel_execution.graph("implementation")
api.parallel_execution.plan(project_id, "implementation")
api.parallel_execution.execute(plan, invoke_fn)
api.parallel_execution.pause() / resume() / cancel()
```

## CLI

```bash
engineeringos parallel status
engineeringos parallel graph implementation
engineeringos parallel workers
engineeringos parallel execute my-app implementation
engineeringos parallel explain my-app implementation
```

## Orchestrator Integration

When `parallel_ready` policy applies (implementation phase), Orchestrator delegates scheduling to Parallel Execution Engine. Runtime remains unchanged; `parallel_tracks` populated on state.
