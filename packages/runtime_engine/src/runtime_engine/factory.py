"""Runtime factory."""

from __future__ import annotations

from pathlib import Path

from ai_execution import create_runtime_adapter
from orchestrator import create_orchestrator
from runtime_engine.agents.registry import AgentRegistry
from runtime_engine.events.bus import EventBus
from runtime_engine.gate.engine import GateEngine
from runtime_engine.pipeline.engine import PipelineEngine
from runtime_engine.rework.engine import ReworkEngine
from runtime_engine.runtime.facade import Runtime
from runtime_engine.state.store import JsonStateStore
from runtime_engine.validation.engine import ArtifactValidationEngine
from runtime_engine.workflow.loader import WorkflowLoader


def discover_framework_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for directory in [current, *current.parents]:
        if (directory / "workflow.yaml").is_file() and (directory / "runtime").is_dir():
            return directory
    package_root = Path(__file__).resolve().parents[4]
    if (package_root / "workflow.yaml").is_file():
        return package_root
    raise FileNotFoundError("Cannot locate framework root (workflow.yaml)")


def create_runtime(
    framework_root: Path | None = None,
    workflow_path: str | None = None,
    registry_path: str | None = None,
) -> Runtime:
    root = framework_root or discover_framework_root()
    wf_path = workflow_path or str(root / "workflow.yaml")
    reg_path = registry_path or str(root / "runtime" / "employee-registry.yaml")

    workflow_loader = WorkflowLoader()
    event_bus = EventBus()
    validation_engine = ArtifactValidationEngine()
    gate_engine = GateEngine(validation_engine)
    pipeline = PipelineEngine()
    rework = ReworkEngine()
    store = JsonStateStore()
    registry = AgentRegistry(reg_path)
    adapter = create_runtime_adapter(framework_root=root)
    orchestrator = create_orchestrator(adapter, registry, framework_root=root)

    return Runtime(
        workflow_loader=workflow_loader,
        workflow_path=wf_path,
        state_store=store,
        event_bus=event_bus,
        agent_registry=registry,
        orchestrator=orchestrator,
        pipeline=pipeline,
        gate_engine=gate_engine,
        validation_engine=validation_engine,
        rework_engine=rework,
        framework_root=root,
    )
