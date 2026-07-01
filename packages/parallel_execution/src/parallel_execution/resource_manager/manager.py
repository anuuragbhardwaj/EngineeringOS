"""Resource management for workers."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class ResourceLimits:
    max_workers: int = 4
    max_retries: int = 2
    timeout_seconds: int = 600
    rate_limit_per_minute: int = 60


class ResourceManager:
    """Manage provider capacity, rate limits, and timeouts."""

    def __init__(self, limits: ResourceLimits | None = None) -> None:
        self._limits = limits or ResourceLimits()
        self._active_workers: int = 0
        self._invocations: list[float] = []

    @property
    def limits(self) -> ResourceLimits:
        return self._limits

    def can_spawn(self) -> bool:
        return self._active_workers < self._limits.max_workers

    def acquire_worker(self) -> bool:
        if not self.can_spawn():
            return False
        self._active_workers += 1
        return True

    def release_worker(self) -> None:
        self._active_workers = max(0, self._active_workers - 1)

    def check_rate_limit(self) -> bool:
        now = time.time()
        self._invocations = [t for t in self._invocations if now - t < 60]
        if len(self._invocations) >= self._limits.rate_limit_per_minute:
            return False
        self._invocations.append(now)
        return True

    def should_retry(self, attempt: int, failed: bool) -> bool:
        return failed and attempt < self._limits.max_retries
