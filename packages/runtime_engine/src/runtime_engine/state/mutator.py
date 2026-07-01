"""Runtime-owned PipelineState mutation API."""

from __future__ import annotations

from datetime import datetime
from typing import Any


class PipelineStateMutator:
    """All PipelineState mutations flow through Runtime-owned APIs."""

    def __init__(self, state: Any) -> None:
        self._state = state

    @property
    def state(self) -> Any:
        return self._state

    def set_project_paused(self) -> None:
        from runtime_engine.types import ProjectStatus

        self._state.status = ProjectStatus.PAUSED

    def begin_phase_execution(self, phase_id: str, orchestrator_agent_id: str) -> None:
        from runtime_engine.types import PhaseStatus

        self._state.phase_status[phase_id] = PhaseStatus.IN_PROGRESS
        self._state.execution.active_agent_id = orchestrator_agent_id
        self._state.execution.last_invocation_at = datetime.utcnow()
        self._state.execution.invocation_count += 1

    def append_parallel_track(self, track: Any) -> None:
        self._state.execution.parallel_tracks.append(track)

    def record_artifact(self, artifact_name: str, record: Any) -> None:
        self._state.artifact_index[artifact_name] = record

    def append_execution_history(self, entry: dict) -> None:
        self._state.execution.history.append(entry)

    def complete_planning_pipeline(self, stop_phase: str, phase_id: str) -> None:
        from runtime_engine.types import PhaseStatus

        self._state.execution.pipeline_completed = True
        self._state.execution.pipeline_stop_phase = stop_phase
        self._state.phase_status[phase_id] = PhaseStatus.PASS

    def touch_updated_at(self) -> None:
        self._state.updated_at = datetime.utcnow()
