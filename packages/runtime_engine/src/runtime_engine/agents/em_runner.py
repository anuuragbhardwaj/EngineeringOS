"""Engineering Manager runner — sole direct employee; delegates to specialists."""

from __future__ import annotations

from datetime import datetime

from runtime_engine.agents.registry import AgentRegistry
from runtime_engine.events import catalog as events
from runtime_engine.events.bus import EventBus
from runtime_engine.types import (
    AdapterStatus,
    ArtifactRecord,
    ArtifactRef,
    InvocationContext,
    PhaseStatus,
    PipelineState,
    WorkflowDefinition,
)


class EngineeringManagerRunner:
    """Coordinates specialist employees; Runtime invokes only this runner."""

    def __init__(
        self,
        registry: AgentRegistry,
        adapter: object,
        event_bus: EventBus,
    ) -> None:
        self._registry = registry
        self._adapter = adapter
        self._bus = event_bus

    def run_phase(
        self,
        state: PipelineState,
        workflow: WorkflowDefinition,
    ) -> PipelineState:
        phase_id = state.current_phase_id
        phase = workflow.phase_by_id(phase_id)
        if phase is None:
            return state

        orchestrator = self._registry.resolve_orchestrator(workflow)
        specialist = self._registry.resolve_primary(phase_id, workflow)
        if specialist is None:
            return state

        state.phase_status[phase_id] = PhaseStatus.IN_PROGRESS
        state.execution.active_agent_id = orchestrator.agent_id
        state.execution.last_invocation_at = datetime.utcnow()
        state.execution.invocation_count += 1

        self._bus.publish(
            self._bus.make_event(
                events.AgentInvoked,
                state.project_id,
                {
                    "agent_id": orchestrator.agent_id,
                    "phase_id": phase_id,
                    "adapter_status": AdapterStatus.DELEGATED.value,
                    "delegating_to": specialist.agent_id,
                },
            )
        )

        deliverables = specialist.expected_outputs or [phase.primary_artifact]
        for artifact_name in deliverables:
            context = InvocationContext(
                project_id=state.project_id,
                phase_id=phase_id,
                artifact_root=state.artifact_root,
                required_inputs=[
                    ArtifactRef(name=n, path=n, owner_agent=None)
                    for n in specialist.expected_inputs
                ],
                deliverable=artifact_name,
                delegation_brief=(
                    f"EM delegates {phase.name} to {specialist.role} "
                    f"for artifact {artifact_name}"
                ),
                metadata=state.metadata,
            )
            result = self._adapter.invoke(specialist, context)
            state.artifact_index[artifact_name] = ArtifactRecord(
                name=artifact_name,
                path=artifact_name,
                owner_agent=specialist.agent_id,
                last_validated_at=None,
                approved=False,
            )
            self._bus.publish(
                self._bus.make_event(
                    events.ArtifactCreated,
                    state.project_id,
                    {
                        "artifact_name": artifact_name,
                        "phase_id": phase_id,
                        "agent_id": specialist.agent_id,
                        "delegated_by": orchestrator.agent_id,
                    },
                )
            )
            state.execution.history.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "orchestrator": orchestrator.agent_id,
                    "specialist": specialist.agent_id,
                    "phase_id": phase_id,
                    "artifact": artifact_name,
                    "status": result.status.value,
                    "provider_id": result.metadata.get("provider_id"),
                }
            )

        if workflow.artifacts.orchestration.required:
            orch = workflow.artifacts.orchestration
            orch_context = InvocationContext(
                project_id=state.project_id,
                phase_id=phase_id,
                artifact_root=state.artifact_root,
                required_inputs=[],
                deliverable=orch.name,
                delegation_brief="EM maintains pipeline-status.md",
                metadata=state.metadata,
            )
            self._adapter.invoke(orchestrator, orch_context)
            state.artifact_index[orch.name] = ArtifactRecord(
                name=orch.name,
                path=orch.path,
                owner_agent=orchestrator.agent_id,
            )

        state.updated_at = datetime.utcnow()
        return state
