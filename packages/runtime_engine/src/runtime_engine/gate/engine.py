"""Gate evaluation engine."""

from __future__ import annotations

from datetime import datetime

from runtime_engine.errors import GateNotFoundError, ProjectBlockedError
from runtime_engine.types import (
    GateEvaluation,
    GateRecord,
    PipelineState,
    ProjectStatus,
    WorkflowDefinition,
)
from runtime_engine.validation.engine import ArtifactValidationEngine


class GateEngine:
    """IGateEngine implementation."""

    def __init__(self, validation_engine: ArtifactValidationEngine) -> None:
        self._validation = validation_engine

    def evaluate(
        self,
        state: PipelineState,
        workflow: WorkflowDefinition,
    ) -> GateEvaluation:
        gate = self.get_current_gate(state, workflow)
        if gate is None:
            raise GateNotFoundError(f"No gate for phase {state.current_phase_id}")

        report = self._validation.validate_phase_exit(state, workflow)
        errors = [
            f"{err.code}: {err.message}"
            for result in report.results
            for err in result.errors
        ]
        strikes = self.get_strikes(state, gate.id)
        passed = report.passed
        if not passed:
            strikes += 1

        return GateEvaluation(
            gate_id=gate.id,
            phase_id=state.current_phase_id,
            passed=passed,
            errors=errors,
            artifact_results=report.results,
            strike_count=strikes,
            max_strikes=workflow.defaults.max_gate_failures,
        )

    def record_result(
        self,
        state: PipelineState,
        gate_id: str,
        passed: bool,
        notes: str,
        evaluator: str,
        user_approved: bool,
    ) -> tuple[PipelineState, GateRecord]:
        phase = state.current_phase_id
        record = GateRecord(
            gate_id=gate_id,
            phase_id=phase,
            passed=passed,
            timestamp=datetime.utcnow(),
            notes=notes,
            evaluator=evaluator,
            user_approved=user_approved,
        )
        state.gate_history.append(record)
        if not passed:
            state.gate_strikes[gate_id] = state.gate_strikes.get(gate_id, 0) + 1
            if state.gate_strikes[gate_id] >= 3:
                state.status = ProjectStatus.BLOCKED
        else:
            state.gate_strikes[gate_id] = 0
            if state.status == ProjectStatus.AT_RISK:
                state.status = ProjectStatus.ACTIVE
        state.updated_at = datetime.utcnow()
        return state, record

    def get_strikes(self, state: PipelineState, gate_id: str) -> int:
        return state.gate_strikes.get(gate_id, 0)

    def is_blocked(self, state: PipelineState, workflow: WorkflowDefinition) -> bool:
        max_failures = workflow.defaults.max_gate_failures
        return state.status == ProjectStatus.BLOCKED or any(
            strikes >= max_failures for strikes in state.gate_strikes.values()
        )

    def get_current_gate(self, state: PipelineState, workflow: WorkflowDefinition):
        phase = workflow.phase_by_id(state.current_phase_id)
        return phase.gate if phase else None
