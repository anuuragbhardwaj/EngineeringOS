"""Planning pipeline execution sequencing."""

from __future__ import annotations

from typing import Any

from orchestrator.errors import ApprovalRequiredError
from orchestrator.execution.phase_executor import PhaseExecutor
from orchestrator.types import LifecycleCallbacks


class PipelineExecutor:
    """Sequences phases through orchestrator; delegates lifecycle to Runtime."""

    def __init__(self, phase_executor: PhaseExecutor) -> None:
        self._phases = phase_executor

    def execute_planning_pipeline(
        self,
        state: Any,
        workflow: Any,
        stop_after_phase: str,
        lifecycle: LifecycleCallbacks,
    ) -> Any:
        from runtime_engine.errors import AdapterInvocationError

        stop_phase = workflow.phase_by_id(stop_after_phase)
        if stop_phase is None:
            raise ValueError(f"Unknown phase: {stop_after_phase}")

        while True:
            phase = workflow.phase_by_id(state.current_phase_id)
            if phase is None or phase.order > stop_phase.order:
                break

            lifecycle.publish_event(
                "PhaseStarted",
                {"phase_id": phase.id, "gate_id": phase.gate.id},
            )

            try:
                state = self._phases.execute(
                    state,
                    workflow,
                    lifecycle=lifecycle,
                    publish_event=lifecycle.publish_event,
                )
            except ApprovalRequiredError:
                lifecycle.persist(state)
                return state

            lifecycle.persist(state)

            report = lifecycle.validate()
            for result in report.results:
                lifecycle.publish_event(
                    "ArtifactValidated",
                    {
                        "artifact_name": result.checks_run[0] if result.checks_run else "",
                        "passed": result.passed,
                        "phase_id": phase.id,
                    },
                )
            if not report.passed:
                raise AdapterInvocationError("Phase validation failed")

            evaluation = lifecycle.evaluate_gate()
            if not evaluation.passed:
                raise AdapterInvocationError(
                    f"Gate {evaluation.gate_id} failed: {evaluation.errors}"
                )

            lifecycle.record_gate(
                phase.gate.id,
                True,
                f"Planning pipeline — {phase.name} complete",
            )

            if phase.id == stop_after_phase:
                lifecycle.mutator.complete_planning_pipeline(stop_after_phase, phase.id)
                lifecycle.persist(lifecycle.mutator.state)
                lifecycle.publish_event(
                    "PipelineCompleted",
                    {"stop_phase": stop_after_phase},
                )
                break

            state = lifecycle.advance()

        return state
