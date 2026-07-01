"""Conflict detection for parallel workers."""

from __future__ import annotations

from collections import defaultdict

from parallel_execution.errors import ConflictDetectedError
from parallel_execution.types import ConflictReport, WorkerTask


class ConflictDetector:
    """Detect artifact, gate, and knowledge conflicts."""

    def detect_artifact_conflicts(self, workers: list[WorkerTask]) -> list[ConflictReport]:
        artifact_map: dict[str, list[str]] = defaultdict(list)
        for worker in workers:
            artifact_map[worker.deliverable].append(worker.worker_id)

        conflicts: list[ConflictReport] = []
        for artifact, worker_ids in artifact_map.items():
            if len(worker_ids) > 1:
                # Same deliverable by multiple workers — allowed only if different subsystems
                subsystems = {
                    w.metadata.get("subsystem", w.employee_id)
                    for w in workers
                    if w.worker_id in worker_ids
                }
                if len(subsystems) == 1:
                    conflicts.append(
                        ConflictReport(
                            conflict_type="artifact",
                            message=f"Multiple workers targeting same artifact: {artifact}",
                            workers=worker_ids,
                            artifacts=[artifact],
                        )
                    )
        return conflicts

    def detect_repository_conflicts(self, active_workers: list[str]) -> ConflictReport | None:
        sc_workers = [w for w in active_workers if "source-control" in w]
        if len(sc_workers) > 1:
            return ConflictReport(
                conflict_type="repository",
                message="Source Control Engineer cannot execute concurrently",
                workers=sc_workers,
            )
        return None

    def escalate(self, conflicts: list[ConflictReport]) -> None:
        if conflicts:
            messages = "; ".join(c.message for c in conflicts)
            raise ConflictDetectedError(
                f"Conflicts detected — escalated to Engineering Manager: {messages}"
            )

    def check_and_escalate(self, workers: list[WorkerTask]) -> list[ConflictReport]:
        conflicts = self.detect_artifact_conflicts(workers)
        repo = self.detect_repository_conflicts([w.worker_id for w in workers])
        if repo:
            conflicts.append(repo)
        for c in conflicts:
            c.escalated = True
        self.escalate(conflicts)
        return conflicts
