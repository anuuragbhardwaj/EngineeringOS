"""Rework routing engine."""

from __future__ import annotations

from datetime import datetime

from runtime_engine.errors import ReworkNotFoundError, ReworkRoutingError
from runtime_engine.types import PhaseStatus, PipelineState, ReworkRecord, WorkflowDefinition


class ReworkEngine:
    """IReworkEngine implementation."""

    def route(
        self,
        state: PipelineState,
        symptom: str,
        reason: str,
        workflow: WorkflowDefinition,
    ) -> ReworkRecord:
        target = workflow.rework_routing.get(symptom)
        if target is None:
            raise ReworkRoutingError(f"Unknown symptom: {symptom}")

        rework_id = f"RW-{len(state.rework_history) + 1:03d}"
        return ReworkRecord(
            id=rework_id,
            timestamp=datetime.utcnow(),
            from_phase_id=state.current_phase_id,
            to_phase_id=target.route_to,
            symptom=symptom,
            reason=reason,
        )

    def apply(self, state: PipelineState, rework: ReworkRecord) -> PipelineState:
        state.rework_history.append(rework)
        state.current_phase_id = rework.to_phase_id
        state.phase_status[rework.to_phase_id] = PhaseStatus.IN_PROGRESS
        state.updated_at = datetime.utcnow()
        return state

    def resolve(self, state: PipelineState, rework_id: str) -> PipelineState:
        for record in state.rework_history:
            if record.id == rework_id:
                record.resolved = True
                record.resolved_at = datetime.utcnow()
                state.updated_at = datetime.utcnow()
                return state
        raise ReworkNotFoundError(rework_id)

    def list_open(self, state: PipelineState) -> list[ReworkRecord]:
        return [r for r in state.rework_history if not r.resolved]
