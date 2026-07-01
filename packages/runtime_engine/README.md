# Runtime Engine v1

Company Kernel implementation for EngineeringOS — orchestrates the planning pipeline (Idea → Architecture).

## Overview

| Component | Module | Contract |
|-----------|--------|----------|
| Runtime Facade | `runtime.facade.Runtime` | `IRuntime` |
| Workflow Loader | `workflow.loader` | `IWorkflowLoader` |
| Pipeline Engine | `pipeline.engine` | `IPipelineEngine` |
| Gate Engine | `gate.engine` | `IGateEngine` |
| Validation | `validation.engine` | `IArtifactValidationEngine` |
| Agent Registry | `agents.registry` | `IAgentRegistry` |
| Lifecycle Bridge | `lifecycle.RuntimeLifecycleBridge` | Gate, validate, persist |
| Orchestrator (external) | `orchestrator` package | Sequencing, context, prompts |
| State Store | `state.store` | `IStateStore` |
| Event Bus | `events.bus` | `IEventBus` |

## Execution Flow

```
CLI (engineeringos project create)
    → ProjectAPI
    → IRuntime.init_project
    → IRuntime.execute_planning_pipeline
        → Orchestrator (sequencing, context, prompts)
            → IAgentAdapter → AI Execution Platform
        → Runtime (validate, gate, advance, persist)
    → stops after Architecture
```

## Usage

```python
from runtime_engine import create_runtime

runtime = create_runtime()
runtime.init_project("my-app", artifact_root="./projects/my-app", metadata={...})
runtime.execute_planning_pipeline("my-app")
print(runtime.status("my-app"))
```

## CLI

```bash
engineeringos project create --yes --name "My App" --location ./projects/my-app
engineeringos project status my-app
engineeringos project validate my-app
engineeringos project history my-app
engineeringos project resume my-app
```

## Configuration

- **Workflow:** `workflow.yaml` (exclusive source of phases)
- **Employees:** `runtime/employee-registry.yaml`
- **State:** `{project}/.runtime/state.json`

## Testing

```bash
pytest tests/runtime/ -q
```

See [runtime/interfaces.md](../../runtime/interfaces.md) for the constitutional contract.
