# Workspace Execution Guide

EngineeringOS maintains persistent execution context so you rarely pass project paths or IDs.

## Self-hosting example

```bash
engineeringos open
engineeringos workspace use engineeringos
engineeringos project use memory-system
engineeringos continue
```

## Commands

| Command | Purpose |
|---------|---------|
| `current` | Active company, workspace, project, phase |
| `status` | Unified status engine output |
| `context` | Full session context |
| `reset-context` | Reset to default workspace |
| `continue` | Resume from active context |
| `pause` / `resume` | Pipeline control |
| `history` | Execution history |
| `workspace use` | Switch workspace |
| `project use` | Switch project |

See [packages/workspace_execution/README.md](../../packages/workspace_execution/README.md).
