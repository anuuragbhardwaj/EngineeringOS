"""Employee execution scheduler."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ScheduledExecution:
    orchestrator_id: str
    specialist: Any
    deliverables: list[str]
    delegation_template: str


class ExecutionScheduler:
    """Determines employee execution order within a phase."""

    def plan_phase(
        self,
        *,
        orchestrator: Any,
        specialist: Any,
        phase: Any,
    ) -> list[ScheduledExecution]:
        deliverables = list(specialist.expected_outputs or [phase.primary_artifact])
        if not deliverables:
            return []

        if len(deliverables) == 1:
            return [
                ScheduledExecution(
                    orchestrator_id=orchestrator.agent_id,
                    specialist=specialist,
                    deliverables=deliverables,
                    delegation_template=(
                        "EM delegates {phase_name} to {role} for artifact {artifact}"
                    ),
                )
            ]

        return [
            ScheduledExecution(
                orchestrator_id=orchestrator.agent_id,
                specialist=specialist,
                deliverables=[artifact],
                delegation_template=(
                    "EM delegates {phase_name} to {role} for artifact {artifact}"
                ),
            )
            for artifact in deliverables
        ]
