"""Synchronization barriers and merge."""

from __future__ import annotations

from parallel_execution.types import BarrierType, MergeResult, WorkerTask, WorkerStatus


class SynchronizationEngine:
    """Barriers: wait_all, wait_any, merge."""

    def wait_all(self, workers: list[WorkerTask]) -> bool:
        return all(w.status == WorkerStatus.COMPLETED.value for w in workers)

    def wait_any(self, workers: list[WorkerTask]) -> bool:
        return any(w.status == WorkerStatus.COMPLETED.value for w in workers)

    def barrier_complete(self, workers: list[WorkerTask], barrier: str) -> bool:
        if barrier == BarrierType.WAIT_ANY.value:
            return self.wait_any(workers)
        return self.wait_all(workers)

    def merge_outputs(self, workers: list[WorkerTask]) -> MergeResult:
        completed = [w for w in workers if w.status == WorkerStatus.COMPLETED.value]
        failed = [w for w in workers if w.status == WorkerStatus.FAILED.value]
        artifacts = sorted({w.deliverable for w in completed})
        return MergeResult(
            merged=len(failed) == 0,
            artifacts=artifacts,
            conflicts=[],
        )
