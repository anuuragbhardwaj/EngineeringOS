"""Pipeline phase navigation engine."""

from __future__ import annotations

from datetime import datetime

from runtime_engine.errors import PhaseNotFoundError, TransitionError
from runtime_engine.types import (
    ArtifactRef,
    PhaseStatus,
    PipelineState,
    ProjectStatus,
    TransitionDecision,
    TransitionRecord,
    WorkflowDefinition,
)


class PipelineEngine:
    """IPipelineEngine implementation."""

    def get_current_phase(self, state: PipelineState) -> str:
        return state.current_phase_id

    def get_next_phase(
        self,
        state: PipelineState,
        workflow: WorkflowDefinition,
    ) -> str | None:
        phase = workflow.phase_by_id(state.current_phase_id)
        return phase.next if phase else None

    def can_transition(
        self,
        state: PipelineState,
        target_phase_id: str,
        workflow: WorkflowDefinition,
    ) -> TransitionDecision:
        if state.status == ProjectStatus.BLOCKED:
            return TransitionDecision(
                allowed=False,
                reason="Project is blocked",
                blockers=["project_blocked"],
            )

        current = workflow.phase_by_id(state.current_phase_id)
        target = workflow.phase_by_id(target_phase_id)
        if current is None or target is None:
            return TransitionDecision(
                allowed=False,
                reason="Unknown phase",
                blockers=["phase_not_found"],
            )

        if target.order > current.order + 1 and not target.skippable:
            return TransitionDecision(
                allowed=False,
                reason="Cannot skip phases",
                blockers=["illegal_skip"],
            )

        if target.order != current.order + 1 and target.order > current.order:
            return TransitionDecision(
                allowed=False,
                reason="Non-sequential transition",
                blockers=["sequence_violation"],
            )

        last_gate = state.gate_history[-1] if state.gate_history else None
        if target.order > current.order:
            if last_gate is None or not last_gate.passed or last_gate.phase_id != current.id:
                return TransitionDecision(
                    allowed=False,
                    reason="Current phase gate not passed",
                    blockers=["gate_not_passed"],
                )

        return TransitionDecision(allowed=True)

    def advance(
        self,
        state: PipelineState,
        workflow: WorkflowDefinition,
    ) -> PipelineState:
        next_id = self.get_next_phase(state, workflow)
        if next_id is None:
            raise TransitionError("No next phase")

        decision = self.can_transition(state, next_id, workflow)
        if not decision.allowed:
            raise TransitionError(decision.reason or "Transition denied")

        current = state.current_phase_id
        state.phase_status[current] = PhaseStatus.PASS
        state.current_phase_id = next_id
        state.phase_status[next_id] = PhaseStatus.IN_PROGRESS
        state.transition_history.append(
            TransitionRecord(
                timestamp=datetime.utcnow(),
                from_phase_id=current,
                to_phase_id=next_id,
                gate_id=workflow.phase_by_id(current).gate.id if workflow.phase_by_id(current) else None,
                trigger="advance",
            )
        )
        state.updated_at = datetime.utcnow()
        return state

    def get_entry_requirements(
        self,
        phase_id: str,
        workflow: WorkflowDefinition,
    ) -> list[ArtifactRef]:
        phase = workflow.phase_by_id(phase_id)
        if phase is None:
            raise PhaseNotFoundError(phase_id)
        return [
            ArtifactRef(name=name, path=name, owner_agent=None, required=True)
            for name in phase.required_inputs
        ]

    def get_exit_requirements(
        self,
        phase_id: str,
        workflow: WorkflowDefinition,
    ) -> list[ArtifactRef]:
        phase = workflow.phase_by_id(phase_id)
        if phase is None:
            raise PhaseNotFoundError(phase_id)
        return [
            ArtifactRef(
                name=phase.primary_artifact,
                path=phase.primary_artifact,
                owner_agent=phase.owner.agent,
                required=True,
            )
        ]
