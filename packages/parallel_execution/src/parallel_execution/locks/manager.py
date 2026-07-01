"""Artifact locks for parallel workers."""

from __future__ import annotations

import threading
from contextlib import contextmanager


class ArtifactLockManager:
    """Per-artifact locks to prevent concurrent edits."""

    def __init__(self) -> None:
        self._locks: dict[str, threading.Lock] = {}
        self._master = threading.Lock()

    def _get_lock(self, artifact: str) -> threading.Lock:
        with self._master:
            if artifact not in self._locks:
                self._locks[artifact] = threading.Lock()
            return self._locks[artifact]

    @contextmanager
    def acquire(self, artifact: str):
        lock = self._get_lock(artifact)
        lock.acquire()
        try:
            yield
        finally:
            lock.release()

    def is_locked(self, artifact: str) -> bool:
        lock = self._locks.get(artifact)
        return lock.locked() if lock else False
