"""Deterministic output merger."""

from __future__ import annotations

from parallel_execution.types import MergeResult, WorkerTask, WorkerStatus


class OutputMerger:
    """Merge parallel worker outputs deterministically."""

    def merge(self, workers: list[WorkerTask]) -> MergeResult:
        sorted_workers = sorted(workers, key=lambda w: (w.group_id, w.employee_id, w.worker_id))
        artifacts: list[str] = []
        for worker in sorted_workers:
            if worker.status == WorkerStatus.COMPLETED.value:
                if worker.deliverable not in artifacts:
                    artifacts.append(worker.deliverable)
        failed = [w for w in sorted_workers if w.status == WorkerStatus.FAILED.value]
        return MergeResult(merged=len(failed) == 0, artifacts=sorted(artifacts))
