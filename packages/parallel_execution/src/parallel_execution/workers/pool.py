"""Worker pool — concurrent execution with deterministic merge."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable

from parallel_execution.conflicts.detector import ConflictDetector
from parallel_execution.coordination.sync import SynchronizationEngine
from parallel_execution.errors import ExecutionCancelledError
from parallel_execution.locks.manager import ArtifactLockManager
from parallel_execution.merger.merger import OutputMerger
from parallel_execution.resource_manager.manager import ResourceManager
from parallel_execution.types import ExecutionPlan, ExecutionSummary, WorkerStatus, WorkerTask
from parallel_execution.workers.worker import Worker


class WorkerPool:
    """Spawn and track workers across parallel groups."""

    def __init__(
        self,
        resources: ResourceManager | None = None,
        conflicts: ConflictDetector | None = None,
        sync: SynchronizationEngine | None = None,
        merger: OutputMerger | None = None,
    ) -> None:
        self._resources = resources or ResourceManager()
        self._conflicts = conflicts or ConflictDetector()
        self._sync = sync or SynchronizationEngine()
        self._merger = merger or OutputMerger()
        self._locks = ArtifactLockManager()
        self._cancelled = False
        self._paused = False

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    @property
    def paused(self) -> bool:
        return self._paused

    def cancel(self) -> None:
        self._cancelled = True

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def execute_plan(
        self,
        plan: ExecutionPlan,
        invoke_fn: Callable[..., Any],
        *,
        publish_event: Callable[[str, dict], None] | None = None,
        **invoke_kwargs,
    ) -> ExecutionSummary:
        if self._cancelled:
            raise ExecutionCancelledError("Execution cancelled")

        self._conflicts.check_and_escalate(plan.workers)
        start = time.perf_counter()
        completed = failed = cancelled = 0

        for group in plan.groups:
            if self._cancelled:
                break
            group_workers = [w for w in plan.workers if w.worker_id in group.worker_ids]

            if publish_event:
                publish_event(
                    "ParallelGroupStarted",
                    {"group_id": group.group_id, "workers": group.worker_ids},
                )

            self._execute_group(group_workers, invoke_fn, publish_event, invoke_kwargs)

            if publish_event:
                publish_event(
                    "ParallelGroupCompleted",
                    {"group_id": group.group_id, "workers": group.worker_ids},
                )

            if not self._sync.barrier_complete(group_workers, group.barrier):
                failed += sum(1 for w in group_workers if w.status == WorkerStatus.FAILED.value)

        for w in plan.workers:
            if w.status == WorkerStatus.COMPLETED.value:
                completed += 1
            elif w.status == WorkerStatus.FAILED.value:
                failed += 1
            elif w.status == WorkerStatus.CANCELLED.value:
                cancelled += 1

        merge_result = self._merger.merge(plan.workers)
        if publish_event and merge_result.merged:
            publish_event("ExecutionMerged", {"artifacts": merge_result.artifacts})

        return ExecutionSummary(
            plan_id=plan.plan_id,
            completed=completed,
            failed=failed,
            cancelled=cancelled,
            duration_ms=(time.perf_counter() - start) * 1000,
            merge_result=merge_result,
        )

    def _execute_group(
        self,
        workers: list[WorkerTask],
        invoke_fn: Callable,
        publish_event: Callable | None,
        invoke_kwargs: dict,
    ) -> None:
        max_workers = min(len(workers), self._resources.limits.max_workers)

        def run_worker(task: WorkerTask):
            if self._cancelled:
                task.status = WorkerStatus.CANCELLED.value
                return
            if self._paused:
                task.status = WorkerStatus.PAUSED.value
                return
            if not self._resources.acquire_worker():
                task.status = WorkerStatus.FAILED.value
                return
            if publish_event:
                publish_event(
                    "WorkerStarted",
                    {"worker_id": task.worker_id, "employee_id": task.employee_id},
                )
            try:
                worker = Worker(task, self._locks)
                result = worker.execute(invoke_fn, **invoke_kwargs)
                if publish_event:
                    event = "WorkerCompleted" if result.status == WorkerStatus.COMPLETED.value else "WorkerFailed"
                    publish_event(event, {"worker_id": task.worker_id, "error": result.error})
            finally:
                self._resources.release_worker()

        if len(workers) == 1:
            run_worker(workers[0])
            return

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(run_worker, w): w for w in sorted(workers, key=lambda x: x.worker_id)}
            for future in as_completed(futures):
                future.result()
