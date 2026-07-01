# EngineeringOS Orchestrator

Operational intelligence layer for EngineeringOS — decides what executes, when, and with what context.

## Role

| Layer | Responsibility |
|-------|----------------|
| **Runtime** | Lifecycle, state, gates, validation, persistence |
| **Orchestrator** | Sequencing, context, prompts, policies, checkpoints |
| **AI Execution Platform** | Provider execution only |

## Execution Flow

```
Runtime
  -> Orchestrator (context + prompt + policy)
    -> IAgentAdapter
      -> AI Execution Platform
        -> Provider
  <- Normalized result
Runtime (validate, gate, advance, persist)
```

## Modules

| Module | Purpose |
|--------|---------|
| `context/engine` | Assemble normalized execution context |
| `prompt_builder` | Deterministic prompt composition |
| `policy/engine` | Configuration-driven execution policies |
| `checkpoint/manager` | Pause, resume, rollback |
| `conversation/router` | Provider-independent conversation routing |
| `scheduler` | Employee execution sequencing |
| `execution/` | Phase and pipeline executors |
| `approval/hooks` | Human approval pauses |
| `history/recorder` | Execution metadata logs |

## Configuration

`policies.yaml` — per-phase policies, retries, timeouts, approval gates.

## Usage

```python
from orchestrator import create_orchestrator
from ai_execution import create_runtime_adapter

adapter = create_runtime_adapter(framework_root)
orchestrator = create_orchestrator(adapter, agent_registry, framework_root)
```

Runtime factory wires this automatically.

## Testing

```bash
pytest tests/orchestrator/ -q
```
