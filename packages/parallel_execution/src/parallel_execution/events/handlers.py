"""Event integration for parallel execution."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

PARALLEL_EVENTS = {
    "WorkerStarted",
    "WorkerCompleted",
    "WorkerFailed",
    "ParallelGroupStarted",
    "ParallelGroupCompleted",
    "ConflictDetected",
    "ExecutionMerged",
    "ExecutionCancelled",
}


class ParallelEventHandler:
    """Publish and handle parallel execution events."""

    def subscribe_runtime(self, runtime: Any, handler: Callable[[str, dict], None]) -> list[str]:
        ids: list[str] = []
        for event_type in PARALLEL_EVENTS:
            if hasattr(runtime, "subscribe"):
                ids.append(runtime.subscribe(event_type, lambda e, et=event_type: handler(et, dict(e.payload or {}))))
        return ids

    def record_conflict(self, instance_root: Path, conflict: dict) -> None:
        path = instance_root / ".company" / "parallel_execution" / "conflicts.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        import json

        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(conflict) + "\n")
