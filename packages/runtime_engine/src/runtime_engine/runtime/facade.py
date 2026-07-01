"""IRuntime facade — single public entry point."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from runtime_engine.version import CONTRACT_VERSION, SCHEMA_VERSION
from runtime_engine.agents.registry import AgentRegistry
from runtime_engine.errors import (
    AdapterInvocationError,
    GateNotFoundError,
    ProjectBlockedError,
    ProjectNotFoundError,
    TransitionError,
)
from runtime_engine.events import catalog as events
from runtime_engine.events.bus import EventBus
from runtime_engine.gate.engine import GateEngine
from runtime_engine.pipeline.engine import PipelineEngine
from runtime_engine.rework.engine import ReworkEngine
from runtime_engine.state.store import JsonStateStore
from runtime_engine.types import (
    AdapterResult,
    AdapterStatus,
    AgentDescriptor,
    ArtifactRecord,
    ExecutionState,
    GateRecord,
    KernelEvent,
    PhaseStatus,
    PipelineState,
    ProjectStatus,
    ProjectStatusView,
    SubscriptionId,
    ValidationReport,
    WorkflowDefinition,
)
from runtime_engine.validation.engine import ArtifactValidationEngine
from runtime_engine.workflow.loader import WorkflowLoader


class Runtime:
    """Company Kernel runtime facade per runtime/interfaces.md."""

    def __init__(
        self,
        workflow_loader: WorkflowLoader,
        workflow_path: str,
        state_store: JsonStateStore,
        event_bus: EventBus,
        agent_registry: AgentRegistry,
        orchestrator: object,
        pipeline: PipelineEngine,
        gate_engine: GateEngine,
        validation_engine: ArtifactValidationEngine,
        rework_engine: ReworkEngine,
        framework_root: Path,
    ) -> None:
        self._workflow_loader = workflow_loader
        self._workflow_path = workflow_path
        self._workflow: WorkflowDefinition = workflow_loader.load(workflow_path)
        self._store = state_store
        self._bus = event_bus
        self._registry = agent_registry
        self._orchestrator = orchestrator
        self._pipeline = pipeline
        self._gate = gate_engine
        self._validation = validation_engine
        self._rework = rework_engine
        self._framework_root = framework_root
        self._validators_extra: list = []

    @property
    def workflow(self) -> WorkflowDefinition:
        return self._workflow

    def init_project(
        self,
        project_id: str,
        artifact_root: str | None = None,
        metadata: dict | None = None,
    ) -> PipelineState:
        if self._store.exists(project_id):
            raise ProjectNotFoundError(f"Project already exists: {project_id}")

        root = artifact_root or "."
        abs_root = str(Path(root).resolve())
        Path(abs_root).mkdir(parents=True, exist_ok=True)

        phase_status = {p.id: PhaseStatus.PENDING for p in self._workflow.ordered_phases()}
        first_phase = self._workflow.ordered_phases()[0]

        state = PipelineState(
            project_id=project_id,
            status=ProjectStatus.ACTIVE,
            artifact_root=abs_root,
            workflow_version=self._workflow.version,
            workflow_path=self._workflow_path,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata=metadata or {},
            current_phase_id=first_phase.id,
            phase_status=phase_status,
            skip_risk_accepted={},
            gate_strikes={},
            artifact_index={},
            rework_history=[],
            gate_history=[],
            transition_history=[],
            execution=ExecutionState(),
            schema_version=SCHEMA_VERSION,
        )
        state.phase_status[first_phase.id] = PhaseStatus.IN_PROGRESS

        self._store.register_project_path(project_id, Path(abs_root))
        self._persist(project_id, state)

        self._bus.publish(
            self._bus.make_event(
                events.ProjectCreated,
                project_id,
                {
                    "artifact_root": abs_root,
                    "workflow_version": self._workflow.version,
                    "initial_phase_id": first_phase.id,
                },
            )
        )
        self._bus.publish(
            self._bus.make_event(
                events.PhaseEntered,
                project_id,
                {
                    "phase_id": first_phase.id,
                    "previous_phase_id": None,
                    "gate_id": first_phase.gate.id,
                },
            )
        )
        return state

    def load_project(self, project_id: str) -> PipelineState:
        return self._store.load(project_id)

    def delete_project(self, project_id: str) -> None:
        self._store.delete(project_id)

    def status(self, project_id: str) -> ProjectStatusView:
        state = self.load_project(project_id)
        phase = self._workflow.phase_by_id(state.current_phase_id)
        open_rework = next(
            (r for r in reversed(state.rework_history) if not r.resolved),
            None,
        )
        return ProjectStatusView(
            project_id=project_id,
            status=state.status,
            current_phase_id=state.current_phase_id,
            current_gate_id=phase.gate.id if phase else None,
            phase_status=dict(state.phase_status),
            gate_strikes=dict(state.gate_strikes),
            blockers=self._blockers(state),
            last_gate=state.gate_history[-1] if state.gate_history else None,
            open_rework=open_rework,
            next_agent=self.next_agent(project_id),
            metadata=dict(state.metadata),
        )

    def validate(
        self,
        project_id: str,
        phase_id: str | None = None,
    ) -> ValidationReport:
        state = self.load_project(project_id)
        if phase_id:
            original = state.current_phase_id
            state.current_phase_id = phase_id
            report = self._validation.validate_phase_exit(state, self._workflow)
            state.current_phase_id = original
            return report
        return self._validation.validate_phase_exit(state, self._workflow)

    def evaluate_gate(self, project_id: str):
        state = self.load_project(project_id)
        evaluation = self._gate.evaluate(state, self._workflow)
        self._bus.publish(
            self._bus.make_event(
                events.GateEvaluated,
                project_id,
                {
                    "gate_id": evaluation.gate_id,
                    "phase_id": evaluation.phase_id,
                    "passed": evaluation.passed,
                    "error_count": len(evaluation.errors),
                    "strike_count": evaluation.strike_count,
                },
            )
        )
        if not evaluation.passed:
            self._bus.publish(
                self._bus.make_event(
                    events.ValidationFailed,
                    project_id,
                    {
                        "gate_id": evaluation.gate_id,
                        "errors": evaluation.errors,
                    },
                )
            )
        return evaluation

    def record_gate(
        self,
        project_id: str,
        gate_id: str,
        passed: bool,
        notes: str,
        evaluator: str = "em",
        user_approved: bool = False,
    ) -> GateRecord:
        state = self.load_project(project_id)
        state, record = self._gate.record_result(
            state, gate_id, passed, notes, evaluator, user_approved
        )
        self._persist(project_id, state)
        event = events.GatePassed if passed else events.GateRejected
        self._bus.publish(
            self._bus.make_event(
                event,
                project_id,
                {
                    "gate_id": gate_id,
                    "phase_id": record.phase_id,
                    "evaluator": evaluator,
                    "notes": notes,
                },
            )
        )
        return record

    def advance(self, project_id: str) -> PipelineState:
        state = self.load_project(project_id)
        if self._gate.is_blocked(state, self._workflow):
            raise ProjectBlockedError("Project is blocked")

        previous = state.current_phase_id
        try:
            state = self._pipeline.advance(state, self._workflow)
        except TransitionError as exc:
            self._bus.publish(
                self._bus.make_event(
                    events.TransitionBlocked,
                    project_id,
                    {
                        "target_phase_id": self._pipeline.get_next_phase(
                            state, self._workflow
                        ),
                        "reason": str(exc),
                        "blockers": [str(exc)],
                    },
                )
            )
            raise

        self._persist(project_id, state)
        self._bus.publish(
            self._bus.make_event(
                events.PhaseCompleted,
                project_id,
                {"phase_id": previous, "gate_id": None},
            )
        )
        self._bus.publish(
            self._bus.make_event(
                events.PhaseEntered,
                project_id,
                {
                    "phase_id": state.current_phase_id,
                    "previous_phase_id": previous,
                },
            )
        )
        return state

    def rework(self, project_id: str, symptom: str, reason: str) -> PipelineState:
        state = self.load_project(project_id)
        record = self._rework.route(state, symptom, reason, self._workflow)
        state = self._rework.apply(state, record)
        self._persist(project_id, state)
        self._bus.publish(
            self._bus.make_event(
                events.ReworkStarted,
                project_id,
                {
                    "rework_id": record.id,
                    "symptom": symptom,
                    "from_phase_id": record.from_phase_id,
                    "to_phase_id": record.to_phase_id,
                    "reason": reason,
                },
            )
        )
        return state

    def next_agent(self, project_id: str) -> AgentDescriptor | None:
        state = self.load_project(project_id)
        return self._registry.resolve_orchestrator(self._workflow)

    def invoke_agent(self, project_id: str) -> AdapterResult:
        state = self.load_project(project_id)
        orchestrator_desc = self._registry.resolve_orchestrator(self._workflow)

        def publish(event_type: str, payload: dict) -> None:
            self._bus.publish(self._bus.make_event(event_type, project_id, payload))

        state = self._orchestrator.execute_phase(
            state, self._workflow, publish_event=publish
        )
        self._persist(project_id, state)

        provider_id = None
        if state.execution.history:
            provider_id = state.execution.history[-1].get("provider_id")

        return AdapterResult(
            status=AdapterStatus.DELEGATED,
            agent_id=orchestrator_desc.agent_id,
            phase_id=state.current_phase_id,
            message="EM coordinated phase execution via Orchestrator",
            artifacts_touched=list(state.artifact_index.keys()),
            metadata={"provider_id": provider_id} if provider_id else {},
        )

    def release(self, project_id: str, notes: str) -> PipelineState:
        state = self.load_project(project_id)
        state.status = ProjectStatus.RELEASED
        state.updated_at = datetime.utcnow()
        self._persist(project_id, state)
        self._bus.publish(
            self._bus.make_event(
                events.ProjectReleased,
                project_id,
                {"released_at": datetime.utcnow().isoformat(), "notes": notes},
            )
        )
        return state

    def close(self, project_id: str, outcome: str) -> PipelineState:
        state = self.load_project(project_id)
        state.status = ProjectStatus.CLOSED
        state.updated_at = datetime.utcnow()
        self._persist(project_id, state)
        self._bus.publish(
            self._bus.make_event(
                events.ProjectClosed,
                project_id,
                {"outcome": outcome, "closed_at": datetime.utcnow().isoformat()},
            )
        )
        return state

    def subscribe(
        self,
        event_type: str,
        handler: Callable[[KernelEvent], None],
    ) -> SubscriptionId:
        return self._bus.subscribe(event_type, handler)

    def register_validator(self, validator) -> None:
        self._validation.register(validator)
        self._validators_extra.append(validator)

    def register_plugin(self, plugin) -> str:
        raise NotImplementedError("Plugins not implemented in Runtime v1")

    def execute_planning_pipeline(
        self,
        project_id: str,
        stop_after_phase: str = "architecture",
    ) -> PipelineState:
        """Delegate planning pipeline to Orchestrator; Runtime manages lifecycle only."""
        from runtime_engine.lifecycle import RuntimeLifecycleBridge

        state = self.load_project(project_id)
        lifecycle = RuntimeLifecycleBridge(self, project_id)
        lifecycle.bind(state)

        return self._orchestrator.execute_planning_pipeline(
            state,
            self._workflow,
            stop_after_phase,
            lifecycle,
        )

    def resume(self, project_id: str) -> PipelineState:
        state = self.load_project(project_id)
        if state.execution.pipeline_completed:
            return state
        if state.status == ProjectStatus.PAUSED:
            state.status = ProjectStatus.ACTIVE
            self._persist(project_id, state)
            self._bus.publish(
                self._bus.make_event(
                    events.PipelineResumed,
                    project_id,
                    {"phase_id": state.current_phase_id},
                )
            )
        stop = state.execution.pipeline_stop_phase or "architecture"
        return self.execute_planning_pipeline(project_id, stop_after_phase=stop)

    def pause(self, project_id: str) -> PipelineState:
        state = self.load_project(project_id)
        state.status = ProjectStatus.PAUSED
        self._persist(project_id, state)
        self._bus.publish(
            self._bus.make_event(
                events.PipelinePaused,
                project_id,
                {"phase_id": state.current_phase_id},
            )
        )
        return state

    def history(self, project_id: str) -> dict:
        state = self.load_project(project_id)
        base = {
            "transitions": [
                {
                    "from": t.from_phase_id,
                    "to": t.to_phase_id,
                    "gate_id": t.gate_id,
                    "trigger": t.trigger,
                    "timestamp": t.timestamp.isoformat(),
                }
                for t in state.transition_history
            ],
            "gates": [
                {
                    "gate_id": g.gate_id,
                    "phase_id": g.phase_id,
                    "passed": g.passed,
                    "evaluator": g.evaluator,
                    "timestamp": g.timestamp.isoformat(),
                }
                for g in state.gate_history
            ],
            "execution": self._orchestrator.get_execution_history(
                project_id, state.execution.history
            ),
            "checkpoints": [
                {
                    "checkpoint_id": cp.checkpoint_id,
                    "phase_id": cp.phase_id,
                    "status": cp.status,
                    "employee_id": cp.employee_id,
                }
                for cp in self._orchestrator.get_checkpoints(project_id)
            ],
        }
        return base

    def _persist(self, project_id: str, state: PipelineState) -> None:
        state.updated_at = datetime.utcnow()
        self._store.save(project_id, state)
        self._bus.publish(
            self._bus.make_event(
                events.StateSaved,
                project_id,
                {
                    "schema_version": state.schema_version,
                    "updated_at": state.updated_at.isoformat(),
                },
            )
        )

    def _blockers(self, state: PipelineState) -> list[str]:
        blockers: list[str] = []
        if state.status == ProjectStatus.BLOCKED:
            blockers.append("project_blocked")
        if state.status == ProjectStatus.PAUSED:
            blockers.append("pipeline_paused")
        return blockers
