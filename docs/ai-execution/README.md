# AI Execution Platform Documentation

## Overview

The AI Execution Platform (`packages/ai_execution`) is the **permanent execution boundary** for EngineeringOS. No kernel component may call AI providers directly.

## Execution Lifecycle

1. **Runtime** invokes `IAgentAdapter.invoke()` (via `RuntimeAgentAdapter`)
2. **Platform** builds `ExecutionContext` from project metadata, phase, artifacts, prompts
3. **ConversationManager** creates session and conversation
4. **CapabilityResolver** selects provider by capability (never by name from Runtime)
5. **Provider** executes and returns normalized `ExecutionResponse`
6. **Adapter** translates to `AdapterResult` for the kernel

## Conversation Model

| Concept | Description |
|---------|-------------|
| `Conversation` | Message history with system/user/assistant roles |
| `ExecutionSession` | Links project, employee, phase to a conversation |
| Persistence | `{project}/.runtime/conversations/{id}.json` |

## Provider Registration

Edit `packages/ai_execution/providers.yaml`:

```yaml
providers:
  my-provider:
    enabled: true
    priority: 85
    capabilities:
      - coding
      - reasoning
```

Implement `IExecutionProvider` and register in `factory.create_platform()`.

## Cursor Provider (v1)

`CursorProvider`:
- Loads employee prompts from `.cursor/agents/{employee}.md`
- Builds conversation context
- Generates artifacts via normalized execution path
- Exposes health based on agent directory availability
- Never exposes Cursor APIs to Runtime

## Adapter Development

Runtime integration uses `RuntimeAgentAdapter` only:

```python
from ai_execution import create_runtime_adapter
adapter = create_runtime_adapter()
```

## Capability Routing

| Phase | Capabilities |
|-------|-------------|
| idea | reasoning, planning |
| requirements | reasoning, planning |
| specification | reasoning, planning |
| planning | planning, reasoning |
| architecture | documentation, coding, planning |
| implementation | coding, implementation, tool-use |

## Error Handling

- Provider unavailable -> retry -> fallback to scaffold
- Placeholder providers -> `ProviderPlaceholderError`
- Rate limits -> retry with fallback
- Conversation corruption -> `ConversationCorruptError`

## MCP

The platform passes MCP evidence in `ExecutionContext.mcp_evidence`. It does **not** execute MCP servers.

## References

- [runtime/interfaces.md](../../runtime/interfaces.md) — `IAgentAdapter` contract
- [packages/ai_execution/README.md](../../packages/ai_execution/README.md)
