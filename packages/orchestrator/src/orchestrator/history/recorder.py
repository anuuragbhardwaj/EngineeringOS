"""Execution history recorder."""

from __future__ import annotations

from datetime import datetime

from orchestrator.types import ExecutionRecord


class HistoryRecorder:
    """Records employee execution metadata."""

    def __init__(self) -> None:
        self._records: list[ExecutionRecord] = []

    def record(
        self,
        *,
        project_id: str,
        employee_id: str,
        orchestrator_id: str,
        phase_id: str,
        provider_id: str | None,
        duration_ms: float | None,
        input_artifacts: list[str],
        output_artifacts: list[str],
        status: str,
        retry_count: int,
        policy: str,
        checkpoint_id: str | None,
    ) -> ExecutionRecord:
        entry = ExecutionRecord(
            project_id=project_id,
            employee_id=employee_id,
            timestamp=datetime.utcnow(),
            provider_id=provider_id,
            duration_ms=duration_ms,
            input_artifacts=input_artifacts,
            output_artifacts=output_artifacts,
            status=status,
            retry_count=retry_count,
            policy=policy,
            checkpoint_id=checkpoint_id,
            phase_id=phase_id,
            orchestrator_id=orchestrator_id,
        )
        self._records.append(entry)
        return entry

    def for_project(self, project_id: str, execution_history: list[dict]) -> list[dict]:
        """Merge orchestrator records with runtime execution history."""
        records = [
            {
                "employee_id": r.employee_id,
                "specialist": r.employee_id,
                "orchestrator_id": r.orchestrator_id,
                "phase_id": r.phase_id,
                "provider_id": r.provider_id,
                "duration_ms": r.duration_ms,
                "input_artifacts": r.input_artifacts,
                "output_artifacts": r.output_artifacts,
                "status": r.status,
                "retry_count": r.retry_count,
                "policy": r.policy,
                "checkpoint_id": r.checkpoint_id,
                "timestamp": r.timestamp.isoformat(),
            }
            for r in self._records
            if r.project_id == project_id
        ]
        return records + execution_history

    def all_records(self) -> list[ExecutionRecord]:
        return list(self._records)

    def filter_project(self, project_id: str, runtime_history: list[dict]) -> list[dict]:
        orch_records = [
            {
                "employee_id": r.employee_id,
                "specialist": r.employee_id,
                "orchestrator_id": r.orchestrator_id,
                "phase_id": r.phase_id,
                "provider_id": r.provider_id,
                "duration_ms": r.duration_ms,
                "status": r.status,
                "retry_count": r.retry_count,
                "policy": r.policy,
                "checkpoint_id": r.checkpoint_id,
                "timestamp": r.timestamp.isoformat(),
                "source": "orchestrator",
            }
            for r in self._records
            if r.project_id == project_id
        ]
        tagged = [{**h, "source": "runtime"} for h in runtime_history]
        return orch_records + tagged
