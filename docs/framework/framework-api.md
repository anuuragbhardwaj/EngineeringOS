# Framework API — AI Company Framework

**Version:** 2.0.0 (alignment 2026-07-02)  
**Date:** 2026-07-01  
**Status:** **Implemented** — `FrameworkAPI` in `packages/company_core`

**Parent:** [framework-architecture.md](./framework-architecture.md)

---

## Purpose

The **Framework API** is the **single public interface** through which all products consume the AI Company Framework. No product may bypass it to read framework internals directly.

**Consumers:** `engineeringos` CLI, future editors, SDK, cloud, dashboard.

---

## Implemented Aggregate (`FrameworkAPI`)

Entry point: `company_core.FrameworkAPI` (`packages/company_core/src/company_core/api/framework.py`).

```python
from company_core import FrameworkAPI

api = FrameworkAPI()  # discovers company.yaml from cwd
api.manifest.load()
api.project.create(...)
api.autonomous.work("Implement feature X")
api.knowledge.search("architecture decision")
api.source_control.status()
api.parallel_execution.status()
api.validate_all()
```

| Property | Status | Delegates to |
|----------|--------|--------------|
| `manifest` | Shipped | `company_core` |
| `company` | Shipped | `company_lifecycle` |
| `workspace` | Shipped | `company_lifecycle` |
| `project` | Shipped | `runtime_engine` (via ProjectAPI) |
| `context` | Shipped | `workspace_execution` |
| `execution` | Shipped | `workspace_execution` |
| `mcp` | Shipped | `mcp_platform` |
| `knowledge` | Shipped | `knowledge` |
| `source_control` | Shipped | `source_control` |
| `parallel_execution` | Shipped | `parallel_execution` |
| `autonomous` | Shipped | `autonomous_company` |
| `lifecycle` | Shipped | `company_lifecycle` |
| `employee` | **Stub** | raises `NotImplementedFeatureError` |
| `integration` | **Stub** | raises `NotImplementedFeatureError` |

**Known coupling:** `ProjectAPI` imports `runtime_engine` directly. Documented in [docs/audit/technical-debt.md](../audit/technical-debt.md). Monorepo v1 accepts this; standalone `company_core` distribution requires composition-root injection (future).

---

## API Layers

```
┌─────────────────────────────────────────────────────────┐
│  Products (CLI, Editors, SDK, Cloud, Dashboard)         │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│  FRAMEWORK API (this document)                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│  │ CompanyAPI  │ │ WorkspaceAPI│ │ ProjectAPI          │ │
│  └─────────────┘ └─────────────┘ └─────────────────────┘ │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│  │ ManifestAPI │ │ McpAPI      │ │ IntegrationAPI      │ │
│  └─────────────┘ └─────────────┘ └─────────────────────┘ │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│  │ EmployeeAPI │ │ TemplateAPI │ │ PluginAPI           │ │
│  └─────────────┘ └─────────────┘ └─────────────────────┘ │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│  KERNEL API (runtime/interfaces.md) — subset for runtime  │
└───────────────────────────────────────────────────────────┘
```

---

## Design Rules

1. **Stable contracts** — semver; breaking = major bump
2. **Language bindings** — Python primary; TypeScript for SDK/editors
3. **No editor types** in API surface
4. **No MCP vendor types** in API surface
5. **Manifest-first** — all paths resolved via `ManifestAPI`
6. **Kernel separate** — `IRuntime` accessed via `RuntimeAPI` wrapper, not duplicated

---

## ManifestAPI

```python
# Illustrative — packages/company_core/api/manifest.py

class IManifestAPI(Protocol):
    def load(self, path: Path | None = None) -> CompanyManifest: ...
    def resolve(self, key: str) -> Path: ...
    def framework_version(self) -> str: ...
    def validate(self) -> list[ValidationError]: ...
```

| Method | Input | Output | Failure |
|--------|-------|--------|---------|
| `load` | optional path | `CompanyManifest` | `ManifestNotFoundError` |
| `resolve` | manifest key | `Path` | `KeyNotFoundError` |
| `validate` | — | errors list | empty = valid |

---

## CompanyAPI

```python
class ICompanyAPI(Protocol):
    def init(self, target: Path, template: str | None) -> CompanyInstance: ...
    def create(self, instance_id: str, config: CompanyConfig) -> CompanyInstance: ...
    def open(self, instance_id: str | None) -> CompanyInstance: ...
    def doctor(self) -> DoctorReport: ...
    def status(self) -> CompanyStatus: ...
    def upgrade(self, version: str | None) -> UpgradeResult: ...
    def migrate(self, dry_run: bool) -> MigrationReport: ...
    def version(self) -> VersionInfo: ...
```

---

## WorkspaceAPI

```python
class IWorkspaceAPI(Protocol):
    def create(self, workspace_id: str) -> Workspace: ...
    def list(self) -> list[WorkspaceInfo]: ...
    def open(self, workspace_id: str) -> Workspace: ...
    def current(self) -> Workspace | None: ...
```

---

## ProjectAPI

```python
class IProjectAPI(Protocol):
    def create(self, project_id: str, workspace: Workspace) -> Project: ...
    def list(self, workspace: Workspace) -> list[ProjectInfo]: ...
    def archive(self, project_id: str) -> None: ...
    def get_runtime(self, project_id: str) -> IRuntime: ...  # delegates to kernel
```

`IRuntime` methods per `runtime/interfaces.md` — not redefined here.

---

## McpAPI

```python
class IMcpAPI(Protocol):
    def list_capabilities(self) -> list[CapabilityInfo]: ...
    def list_tools(self) -> list[McpInfo]: ...
    def resolve(self, capability_id: str) -> Resolution: ...
    def validate(self) -> ValidationReport: ...
    def doctor(self) -> HealthReport: ...
```

Delegates to `mcp_platform` internally.

---

## IntegrationAPI

```python
class IIntegrationAPI(Protocol):
    def install(self, editor: str) -> InstallResult: ...
    def uninstall(self, editor: str) -> None: ...
    def list_editors(self) -> list[EditorInfo]: ...
    def sync(self, editor: str) -> SyncResult: ...
    def doctor(self, editor: str) -> HealthReport: ...
```

Supported editors: `cursor`, `vscode`, `claude-code`, `roo-code` (future).

---

## EmployeeAPI

```python
class IEmployeeAPI(Protocol):
    def list(self) -> list[EmployeeInfo]: ...
    def get(self, employee_id: str) -> EmployeeDescriptor: ...
    def for_phase(self, phase_id: str) -> list[EmployeeDescriptor]: ...
    def resolve_path(self, employee_id: str) -> Path: ...
```

Returns paths and metadata — **does not invoke** agents (editor responsibility).

---

## TemplateAPI

```python
class ITemplateAPI(Protocol):
    def scaffold_workspace(self, workspace_id: str) -> Path: ...
    def scaffold_project(self, project_id: str, workspace: Workspace) -> Path: ...
    def version(self) -> str: ...
```

---

## PluginAPI

```python
class IPluginAPI(Protocol):
    def register_framework_plugin(self, plugin: IFrameworkPlugin) -> PluginId: ...
    def register_kernel_plugin(self, runtime: IRuntime, plugin: IPlugin) -> PluginId: ...
    def list(self) -> list[PluginInfo]: ...
```

Kernel tier: `IPlugin` from `runtime/interfaces.md`.  
Framework tier: `IFrameworkPlugin` from [plugin-architecture.md](./plugin-architecture.md).

---

## RuntimeAPI

Thin facade over kernel — no duplicate method signatures:

```python
class IRuntimeAPI(Protocol):
    def get_runtime(self, project_id: str) -> IRuntime: ...
    def create_runtime(self, config: RuntimeConfig) -> IRuntime: ...
```

All orchestration methods (`advance`, `gate`, etc.) are **on `IRuntime`** only.

---

## EventAPI (Future)

```python
class IEventAPI(Protocol):
    def subscribe(self, event_type: str, handler: Callable) -> SubscriptionId: ...
    def publish_framework_event(self, event: FrameworkEvent) -> None: ...
```

Bridges kernel `IEventBus` and framework lifecycle events.

---

## Error Taxonomy

| Error | Layer |
|-------|-------|
| `ManifestError` | ManifestAPI |
| `CompanyNotFoundError` | CompanyAPI |
| `WorkspaceNotFoundError` | WorkspaceAPI |
| `ProjectNotFoundError` | ProjectAPI |
| `IntegrationError` | IntegrationAPI |
| `McpValidationError` | McpAPI |
| Kernel errors | RuntimeAPI → `runtime/interfaces.md` |

---

## Versioning

| API surface | Version field |
|-------------|---------------|
| Framework API | `framework_api.version` in manifest |
| Binding compatibility | `min_framework_version` per package |

Breaking API change = framework major bump.

---

## Consumer Mapping

| Product | APIs Used |
|---------|-----------|
| `engineeringos` CLI | All shipped APIs — thin Typer wrapper |
| Cursor integration | Partial — `.cursor/agents/`; IntegrationAPI stub |
| VS Code | Planned — IntegrationAPI |
| SDK | Planned — CompanyAPI, WorkspaceAPI, ProjectAPI |
| Cloud | Planned — CompanyAPI, ProjectAPI, EventAPI |
| Dashboard | Planned — EventAPI, CompanyAPI |
| Marketplace | Planned — PluginAPI |

---

## References

- [runtime/interfaces.md](../../runtime/interfaces.md)
- [ADR-0006](../adr/0006-framework-api.md)
- [package-architecture.md](./package-architecture.md)
