# Plugin Architecture — AI Company Framework

**Version:** 2.0.0  
**Date:** 2026-07-01  
**Parent:** [framework-architecture.md](./framework-architecture.md)

---

## Principle

**Plugins extend; they never modify core.** No plugin may patch framework files, employee prompts, or kernel source.

Two tiers:

| Tier | Host | Contract | Scope |
|------|------|----------|-------|
| **Kernel plugins** | Runtime (`IRuntime`) | `IPlugin` in `runtime/interfaces.md` | Project lifecycle events |
| **Framework plugins** | Company CLI / core | `IFrameworkPlugin` (this doc) | Company/workspace lifecycle |

---

## Kernel Plugins (Existing Contract)

Defined in `runtime/interfaces.md`:

```python
class IPlugin(Protocol):
    def info(self) -> PluginInfo: ...
    def on_event(self, event: KernelEvent) -> None: ...
    def on_register(self, runtime: IRuntime) -> None: ...
    def on_shutdown(self) -> None: ...
```

**Events:** `ProjectCreated`, `PhaseEntered`, `GateRejected`, `ArtifactValidated`, etc.

**Planned kernel plugins:**

| Plugin | Events | Purpose |
|--------|--------|---------|
| Metrics | All | Counters, latency |
| Memory | `PhaseCompleted`, `ArtifactValidated` | Company knowledge |
| MCP Evidence | `ArtifactValidated` | Validate evidence footers |
| Cost Tracking | `AgentInvoked` | Token accounting |

---

## Framework Plugins (New Contract — Design)

```python
# Illustrative — packages/company_core/plugins.py

class IFrameworkPlugin(Protocol):
    def info(self) -> FrameworkPluginInfo: ...
    def on_framework_event(self, event: FrameworkEvent) -> None: ...
    def on_register(self, context: FrameworkContext) -> None: ...
    def on_shutdown(self) -> None: ...

@dataclass
class FrameworkEvent:
    type: str           # CompanyCreated, WorkspaceOpened, FrameworkUpgraded, ...
    company_id: str
    workspace_id: str | None
    timestamp: datetime
    payload: dict[str, Any]
```

### Framework Event Catalog

| Event | Publisher | Subscribers |
|-------|-----------|-------------|
| `CompanyCreated` | CLI `init` | Dashboard, analytics |
| `WorkspaceOpened` | CLI `open` | IDE integrations |
| `ProjectCreated` | CLI `project create` | GitHub, Linear |
| `FrameworkUpgraded` | CLI `upgrade` | Migration audit |
| `DoctorCompleted` | CLI `doctor` | CI |
| `PluginInstalled` | CLI `plugin install` | Marketplace |

---

## Plugin Categories (Future)

| Category | Examples | Tier |
|----------|----------|------|
| **Memory** | Company knowledge capture, artifact indexing | Kernel |
| **Metrics** | Prometheus export, phase timing | Kernel + Framework |
| **Dashboard** | Web UI live feed, pipeline viz | Framework |
| **GitHub** | PR sync on `PhaseCompleted` | Framework |
| **Git** | Branch hooks, commit templates | Framework |
| **Cloud** | Remote state backup, team sync | Framework |
| **Notifications** | Slack/Teams on `GateRejected` | Kernel |
| **Marketplace** | Plugin discovery and install | Framework |
| **Security** | Secret scanning, policy gates | Framework |
| **Analytics** | Usage telemetry (opt-in) | Framework |
| **AI Providers** | Custom `IAgentAdapter` | Kernel (adapter, not plugin) |

**Note:** AI Providers implement `IAgentAdapter` — adapter pattern, not framework plugin. Plugins **never require framework modifications**.

---

## Registration

### Kernel plugins

```python
runtime.register_plugin(MyPlugin())
```

### Framework plugins

```yaml
# company.yaml
plugins:
  - id: github-sync
    package: ai-company-plugin-github
    version: "^1.0.0"
    config:
      repo: org/repo
```

Loaded at `company init` or `company plugin install`.

---

## Isolation Rules

| Rule | Enforcement |
|------|-------------|
| No kernel imports in framework plugins | Static analysis |
| No file writes to framework root | Sandbox paths only |
| Handler exceptions isolated | Event bus pattern |
| `supported_contract_version` required | Reject incompatible |
| No secrets in plugin config in git | Env var references |

---

## Marketplace (Future)

```
Marketplace Registry (remote)
    ↓
company plugin search|install|remove
    ↓
workspaces/<ws>/.company/plugins/  OR  venv site-packages
```

Plugins signed (future); manifest declares trust level.

---

## Extension vs Plugin

| | Extension | Plugin |
|--|-----------|--------|
| **Form** | Config + files in workspace | Python package |
| **Load** | Manifest `extensions:` | `plugins:` |
| **Example** | Custom validator YAML rules | GitHub sync service |
| **Complexity** | Low | High |

---

## References

- [runtime/interfaces.md](../../runtime/interfaces.md) § Plugin System
- [ADR-0010](../adr/0010-plugin-system.md)
- [framework-api.md](./framework-api.md)
