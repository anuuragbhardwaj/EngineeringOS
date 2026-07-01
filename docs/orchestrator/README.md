# Orchestrator Documentation

## Execution Lifecycle

1. Runtime loads project state
2. Runtime creates `RuntimeLifecycleBridge`
3. Orchestrator `PipelineExecutor` sequences phases
4. For each phase, `PhaseExecutor`:
   - Resolves policy from `policies.yaml`
   - Creates checkpoint
   - Schedules employee executions
   - Context Engine assembles artifacts and metadata
   - Prompt Builder composes deterministic prompt
   - Conversation Router assigns conversation ID
   - Invokes `IAgentAdapter` (never a provider directly)
   - Records execution history
5. Runtime validates, evaluates gate, records gate, advances
6. Runtime persists state

## Context Engine

Collects: project metadata, workflow state, artifacts, execution history, MCP evidence, company config.

Produces: `AssembledContext` with optional compression for context size policy.

## Prompt Builder

Loads employee prompt from `.cursor/agents/{id}.md`, injects project context, artifact summaries, workflow state, MCP evidence, and deliverable instructions.

Output stored in `metadata.assembled_prompt` for AI Execution Platform.

## Execution Policies

Configured in `packages/orchestrator/policies.yaml`:

- `sequential` — default, retries enabled
- `parallel_ready` — future parallel tracks
- `approval_required` — pauses for human approval

## Checkpoints

Every phase execution creates a checkpoint. Supports pause (approval), complete, rollback.

Exposed in `engineeringos project history` under `checkpoints`.

## Human Approval

```python
orchestrator.approve(project_id, "G0")
runtime.resume(project_id)
```

## References

- [packages/orchestrator/README.md](../../packages/orchestrator/README.md)
- [runtime/interfaces.md](../../runtime/interfaces.md)
