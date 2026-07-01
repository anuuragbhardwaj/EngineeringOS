# EngineeringOS CLI

Command-line interface for EngineeringOS. Binary: **`engineeringos`**.

## Installation

```bash
cd engineeringos
pip install -e ".[dev]"
engineeringos --help
engineeringos version
```

## Architecture

Thin Typer facade over [Framework API](../framework/framework-api.md). All commands use `company_cli.context.get_api()` — no SDLc logic in CLI code.

| Layer | Package |
|-------|---------|
| CLI | `company_cli` |
| Framework API | `company_core` |
| Platforms | lifecycle, workspace_execution, knowledge, source_control, parallel_execution, autonomous_company |
| Kernel stack | runtime_engine → orchestrator → ai_execution |

See [cli-architecture.md](../framework/cli-architecture.md).

---

## Command Reference

### Company & lifecycle

| Command | Status | Description |
|---------|--------|-------------|
| `init [PATH]` | Shipped | Bootstrap `company.yaml` |
| `open` | Shipped | Set active company context |
| `doctor` | Shipped | Health checks |
| `validate` | Shipped | Full validation suite |
| `status [--json]` | Shipped | Instance summary |
| `version` | Shipped | Framework, API, CLI versions |
| `upgrade` | Shipped | Framework upgrade planner |
| `migrate` | Shipped | Migration planner |
| `repair` | Shipped | Instance repair |
| `uninstall` | Shipped | Remove instance artifacts |
| `company` | Shipped | Company navigation |
| `config` | Planned | User configuration |

### Workspace & project

| Command | Status | Description |
|---------|--------|-------------|
| `workspace create/list/use/current/...` | Shipped | Workspace management |
| `project create/list/status/resume/history/validate/...` | Shipped | Project SDLC |
| `context show/reset/...` | Shipped | Execution context |
| `current` | Shipped | Active workspace/project |

### Execution

| Command | Status | Description |
|---------|--------|-------------|
| `continue [--autonomous/--manual]` | Shipped | Continue pipeline (default: autonomous) |
| `pause` | Shipped | Pause execution |
| `resume` | Shipped | Resume execution |
| `history` | Shipped | Execution history |

### Autonomous company

| Command | Status | Description |
|---------|--------|-------------|
| `work <goal>` | Shipped | Start goal-based execution |
| `stop` | Shipped | Stop autonomous runner |
| `goals` | Shipped | List goals |
| `blockers` | Shipped | Active blockers |
| `decisions` | Shipped | Decision history |
| `explain` | Shipped | State + latest decision |
| `supervise` | Shipped | One supervision cycle |
| `monitor` | Shipped | Monitor snapshot |
| `heartbeat` | Shipped | Runner heartbeat |
| `recover` | Shipped | Session recovery |
| `approvals list/approve` | Shipped | EM approval gates |
| `autonomy status` | Shipped | Autonomous status |

SDLC completion: `api.autonomous.complete_sdlc()` (API; no dedicated CLI command yet).

### Knowledge

| Command | Status | Description |
|---------|--------|-------------|
| `knowledge search/store/promote/history/...` | Shipped | Knowledge platform |

See [docs/knowledge/cli.md](../knowledge/cli.md).

### Source control

| Command | Status | Description |
|---------|--------|-------------|
| `repo status/diff/stage/commit/push/release/...` | Shipped | Source control platform |

See [docs/source-control/cli.md](../source-control/cli.md).

### Parallel execution

| Command | Status | Description |
|---------|--------|-------------|
| `parallel status/plan/execute/pause/resume/...` | Shipped | Parallel execution engine |

See [docs/parallel-execution/cli.md](../parallel-execution/cli.md).

### MCP

| Command | Status | Description |
|---------|--------|-------------|
| `mcp list` | Shipped | Registry listing |
| `mcp validate` | Shipped | Validation |
| `mcp doctor` | Shipped | Health checks |

### Employees

| Command | Status | Description |
|---------|--------|-------------|
| `employees [--phase]` | Stub | EmployeeAPI not implemented |

---

## Examples

```bash
engineeringos init ./my-co --id acme --yes
engineeringos open
engineeringos workspace create dev
engineeringos project create my-app --yes
engineeringos project status my-app

engineeringos work "Implement user authentication"
engineeringos continue
engineeringos approvals approve commit

engineeringos knowledge search "architecture"
engineeringos repo status
engineeringos parallel status
```

---

## Testing

```bash
pytest tests/ -q    # 128 tests
```

CLI discovery: `tests/test_command_discovery.py`.

---

## References

- [framework-api.md](../framework/framework-api.md)
- [docs/autonomous-company/cli.md](../autonomous-company/cli.md)
- [Known limitations](../../README.md#known-limitations)
