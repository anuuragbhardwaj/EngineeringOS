"""Worker abstraction — provider-independent execution unit."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from parallel_execution.locks.manager import ArtifactLockManager
from parallel_execution.types import WorkerStatus, WorkerTask


@dataclass
class WorkerResult:
    worker_id: str
    status: str
    duration_ms: float
    error: str | None = None
    metadata: dict = field(default_factory=dict)


class Worker:
    """Executes a single employee task with context, knowledge, and artifacts."""

    def __init__(self, task: WorkerTask, locks: ArtifactLockManager | None = None) -> None:
        self.task = task
        self._locks = locks or ArtifactLockManager()

    def execute(self, invoke_fn: Callable[..., Any], **kwargs) -> WorkerResult:
        self.task.status = WorkerStatus.RUNNING.value
        start = time.perf_counter()
        try:
            with self._locks.acquire(self.task.deliverable):
                invoke_fn(
                    specialist=self.task.specialist,
                    employee_id=self.task.employee_id,
                    deliverable=self.task.deliverable,
                    worker_id=self.task.worker_id,
                    **kwargs,
                )
            self.task.status = WorkerStatus.COMPLETED.value
            return WorkerResult(
                worker_id=self.task.worker_id,
                status=WorkerStatus.COMPLETED.value,
                duration_ms=(time.perf_counter() - start) * 1000,
            )
        except Exception as exc:
            self.task.status = WorkerStatus.FAILED.value
            return WorkerResult(
                worker_id=self.task.worker_id,
                status=WorkerStatus.FAILED.value,
                duration_ms=(time.perf_counter() - start) * 1000,
                error=str(exc),
            )
