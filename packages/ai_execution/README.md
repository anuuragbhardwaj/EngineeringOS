# AI Execution Platform

Permanent execution boundary between EngineeringOS and all AI providers.

## Purpose

The Runtime, CLI, and Employees **never** communicate directly with Cursor, Claude, OpenAI, Gemini, VS Code, or any future provider. Every AI interaction flows through this platform.

## Architecture

```
Engineering Manager
    -> Runtime (IAgentAdapter)
        -> AI Execution Platform
            -> Provider Registry (capability routing)
                -> CursorProvider | ScaffoldProvider | (future)
            -> ConversationManager
    <- Normalized ExecutionResponse
```

## Packages

| Module | Role |
|--------|------|
| `platform` | Orchestration, retry, fallback |
| `registry` | Dynamic provider registration |
| `capabilities` | Capability-based provider selection |
| `conversation` | Sessions, history, persistence |
| `adapter.runtime_adapter` | Runtime boundary (`IAgentAdapter`) |
| `providers.cursor` | First AI provider (Cursor) |
| `providers.scaffold` | Fallback provider |
| `providers.placeholders` | Future providers (Claude, OpenAI, etc.) |

## Configuration

`providers.yaml` — provider capabilities, priority, defaults:

```yaml
default_provider: cursor
fallback_provider: scaffold
```

## Usage

```python
from ai_execution import create_runtime_adapter

adapter = create_runtime_adapter(framework_root=Path("./ai-company"))
result = adapter.invoke(descriptor, invocation_context)
# result.metadata["provider_id"] — Runtime never hardcodes provider
```

## Provider Development

1. Implement `IExecutionProvider` (`provider_id`, `capabilities`, `health`, `execute`)
2. Register in `factory.py` or via future plugin hook
3. Add entry to `providers.yaml` with capabilities
4. **No Runtime changes required**

See [docs/ai-execution/README.md](../../docs/ai-execution/README.md).

## Testing

```bash
pytest tests/ai_execution/ -q
```
