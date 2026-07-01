# EngineeringOS CLI

Command-line interface for the AI Company Framework.

## Installation

From the `ai-company` repository root:

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -e ".[dev]"
```

Verify:

```bash
engineeringos --help
engineeringos version
```

## Overview

EngineeringOS (`engineeringos`) is the **primary operator interface** for the framework. It is a thin Typer facade over the [Framework API](../framework/framework-api.md) — no SDLc logic lives in CLI code.

| Layer | Package | Role |
|-------|---------|------|
| CLI | `company_cli` | Commands, help, exit codes |
| Framework API | `company_core` | Manifest, company, MCP APIs |
| MCP Platform | `mcp_platform` | Registry validation |

## Command Reference

| Command | Status | Description |
|---------|--------|-------------|
| `engineeringos --help` | Shipped | Show all commands |
| `engineeringos version` | Shipped | Framework, API, CLI versions |
| `engineeringos doctor` | Shipped | Health checks (manifest, MCP) |
| `engineeringos validate` | Shipped | Full validation suite |
| `engineeringos init [PATH]` | Shipped | Bootstrap `company.yaml` |
| `engineeringos status [--json]` | Partial | Instance summary |
| `engineeringos open` | Planned | Set active context |
| `engineeringos config` | Planned | User configuration |
| `engineeringos workspace create <id>` | Planned | Create workspace |
| `engineeringos workspace list` | Planned | List workspaces |
| `engineeringos project create` | Shipped | Create project + run planning pipeline |
| `engineeringos project status` | Shipped | Pipeline status |
| `engineeringos project resume` | Shipped | Resume interrupted pipeline |
| `engineeringos project history` | Shipped | Transition and gate history |
| `engineeringos project validate` | Shipped | Validate phase artifacts |
| `engineeringos project list` | Shipped | List projects with runtime state |
| `engineeringos employees [--phase]` | Planned | List employees |
| `engineeringos mcp list` | Shipped | List MCP registry |
| `engineeringos mcp validate` | Shipped | MCP validation |
| `engineeringos mcp doctor` | Shipped | MCP health checks |

## Usage Examples

### Initialize a company instance

```bash
mkdir ~/my-company && cd ~/my-company
engineeringos init --id acme-engineering
engineeringos doctor
```

### Validate MCP registry (from framework root)

```bash
cd ai-company
engineeringos validate
engineeringos mcp list
```

### Check versions

```bash
engineeringos version
engineeringos --version
```

## Configuration

The CLI loads configuration from `company.yaml` in the current directory or any parent. See [company-instance-model.md](../framework/company-instance-model.md).

Future releases will support user-level and workspace-level configuration via `engineeringos config`.

## Architecture

- [cli-architecture.md](../framework/cli-architecture.md) — command index
- [package-architecture.md](../framework/package-architecture.md) — `packages/company_cli`, `packages/company_core`

## Testing

```bash
pytest tests/ -q
```
