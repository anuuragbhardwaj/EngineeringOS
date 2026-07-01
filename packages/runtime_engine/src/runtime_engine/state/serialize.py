"""PipelineState serialization."""

from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from runtime_engine.version import SCHEMA_VERSION
from runtime_engine.errors import StateCorruptError
from runtime_engine.types import (
    ArtifactRecord,
    ExecutionState,
    GateRecord,
    ParallelTrack,
    PhaseStatus,
    PipelineState,
    ProjectStatus,
    ReworkRecord,
    TransitionRecord,
)


def _dt_to_str(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _str_to_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _enum_val(enum_cls: type[Enum], raw: str) -> Enum:
    return enum_cls(raw)


def state_to_dict(state: PipelineState) -> dict[str, Any]:
    return {
        "schema_version": state.schema_version,
        "project_id": state.project_id,
        "status": state.status.value,
        "artifact_root": state.artifact_root,
        "workflow_version": state.workflow_version,
        "workflow_path": state.workflow_path,
        "created_at": _dt_to_str(state.created_at),
        "updated_at": _dt_to_str(state.updated_at),
        "metadata": state.metadata,
        "current_phase_id": state.current_phase_id,
        "phase_status": {k: v.value for k, v in state.phase_status.items()},
        "skip_risk_accepted": state.skip_risk_accepted,
        "gate_strikes": state.gate_strikes,
        "artifact_index": {
            name: {
                "name": rec.name,
                "path": rec.path,
                "owner_agent": rec.owner_agent,
                "last_validated_at": _dt_to_str(rec.last_validated_at),
                "validation_status": rec.validation_status.value
                if rec.validation_status
                else None,
                "version": rec.version,
                "approved": rec.approved,
            }
            for name, rec in state.artifact_index.items()
        },
        "rework_history": [
            {
                "id": r.id,
                "timestamp": _dt_to_str(r.timestamp),
                "from_phase_id": r.from_phase_id,
                "to_phase_id": r.to_phase_id,
                "symptom": r.symptom,
                "reason": r.reason,
                "resolved": r.resolved,
                "resolved_at": _dt_to_str(r.resolved_at),
            }
            for r in state.rework_history
        ],
        "gate_history": [
            {
                "gate_id": g.gate_id,
                "phase_id": g.phase_id,
                "passed": g.passed,
                "timestamp": _dt_to_str(g.timestamp),
                "notes": g.notes,
                "evaluator": g.evaluator,
                "user_approved": g.user_approved,
                "metadata": g.metadata,
            }
            for g in state.gate_history
        ],
        "transition_history": [
            {
                "timestamp": _dt_to_str(t.timestamp),
                "from_phase_id": t.from_phase_id,
                "to_phase_id": t.to_phase_id,
                "gate_id": t.gate_id,
                "trigger": t.trigger,
            }
            for t in state.transition_history
        ],
        "execution": {
            "parallel_tracks": [
                {
                    "track_id": t.track_id,
                    "agent_id": t.agent_id,
                    "phase_id": t.phase_id,
                    "status": t.status.value,
                    "merge_complete": t.merge_complete,
                }
                for t in state.execution.parallel_tracks
            ],
            "active_agent_id": state.execution.active_agent_id,
            "last_invocation_at": _dt_to_str(state.execution.last_invocation_at),
            "invocation_count": state.execution.invocation_count,
            "history": state.execution.history,
            "pipeline_completed": state.execution.pipeline_completed,
            "pipeline_stop_phase": state.execution.pipeline_stop_phase,
        },
    }


def state_from_dict(data: dict[str, Any]) -> PipelineState:
    schema = data.get("schema_version", "0.0.0")
    major = schema.split(".")[0]
    expected_major = SCHEMA_VERSION.split(".")[0]
    if major != expected_major:
        raise StateCorruptError(
            f"Unsupported schema major version: {schema} (expected {SCHEMA_VERSION})"
        )

    artifact_index = {
        name: ArtifactRecord(
            name=rec["name"],
            path=rec["path"],
            owner_agent=rec.get("owner_agent"),
            last_validated_at=_str_to_dt(rec.get("last_validated_at")),
            validation_status=PhaseStatus(rec["validation_status"])
            if rec.get("validation_status")
            else None,
            version=rec.get("version"),
            approved=bool(rec.get("approved", False)),
        )
        for name, rec in data.get("artifact_index", {}).items()
    }

    execution_raw = data.get("execution", {})
    execution = ExecutionState(
        parallel_tracks=[
            ParallelTrack(
                track_id=t["track_id"],
                agent_id=t["agent_id"],
                phase_id=t["phase_id"],
                status=PhaseStatus(t["status"]),
                merge_complete=bool(t.get("merge_complete", False)),
            )
            for t in execution_raw.get("parallel_tracks", [])
        ],
        active_agent_id=execution_raw.get("active_agent_id"),
        last_invocation_at=_str_to_dt(execution_raw.get("last_invocation_at")),
        invocation_count=int(execution_raw.get("invocation_count", 0)),
        history=list(execution_raw.get("history", [])),
        pipeline_completed=bool(execution_raw.get("pipeline_completed", False)),
        pipeline_stop_phase=execution_raw.get("pipeline_stop_phase"),
    )

    return PipelineState(
        project_id=data["project_id"],
        status=ProjectStatus(data["status"]),
        artifact_root=data["artifact_root"],
        workflow_version=data["workflow_version"],
        workflow_path=data["workflow_path"],
        created_at=_str_to_dt(data["created_at"]) or datetime.utcnow(),
        updated_at=_str_to_dt(data["updated_at"]) or datetime.utcnow(),
        metadata=dict(data.get("metadata", {})),
        current_phase_id=data["current_phase_id"],
        phase_status={k: PhaseStatus(v) for k, v in data.get("phase_status", {}).items()},
        skip_risk_accepted=dict(data.get("skip_risk_accepted", {})),
        gate_strikes=dict(data.get("gate_strikes", {})),
        artifact_index=artifact_index,
        rework_history=[
            ReworkRecord(
                id=r["id"],
                timestamp=_str_to_dt(r["timestamp"]) or datetime.utcnow(),
                from_phase_id=r["from_phase_id"],
                to_phase_id=r["to_phase_id"],
                symptom=r["symptom"],
                reason=r["reason"],
                resolved=bool(r.get("resolved", False)),
                resolved_at=_str_to_dt(r.get("resolved_at")),
            )
            for r in data.get("rework_history", [])
        ],
        gate_history=[
            GateRecord(
                gate_id=g["gate_id"],
                phase_id=g["phase_id"],
                passed=bool(g["passed"]),
                timestamp=_str_to_dt(g["timestamp"]) or datetime.utcnow(),
                notes=g.get("notes", ""),
                evaluator=g.get("evaluator", "system"),
                user_approved=bool(g.get("user_approved", False)),
                metadata=dict(g.get("metadata", {})),
            )
            for g in data.get("gate_history", [])
        ],
        transition_history=[
            TransitionRecord(
                timestamp=_str_to_dt(t["timestamp"]) or datetime.utcnow(),
                from_phase_id=t["from_phase_id"],
                to_phase_id=t["to_phase_id"],
                gate_id=t.get("gate_id"),
                trigger=t["trigger"],
            )
            for t in data.get("transition_history", [])
        ],
        execution=execution,
        schema_version=data.get("schema_version", SCHEMA_VERSION),
    )


def save_state(path: Path, state: PipelineState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(state_to_dict(state), indent=2)
    temp = path.with_suffix(".tmp")
    temp.write_text(payload, encoding="utf-8")
    temp.replace(path)


def load_state(path: Path) -> PipelineState:
    if not path.is_file():
        raise StateCorruptError(f"State file missing: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StateCorruptError(str(exc)) from exc
    if not isinstance(data, dict):
        raise StateCorruptError("State file must contain a JSON object")
    return state_from_dict(data)
