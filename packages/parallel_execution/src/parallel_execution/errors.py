"""Parallel execution errors."""

from __future__ import annotations


class ParallelExecutionError(Exception):
    """Base parallel execution error."""


class DependencyCycleError(ParallelExecutionError):
    """Dependency graph contains a cycle."""


class ConflictDetectedError(ParallelExecutionError):
    """Execution conflict requires EM escalation."""


class WorkerTimeoutError(ParallelExecutionError):
    """Worker exceeded timeout."""


class ExecutionCancelledError(ParallelExecutionError):
    """Execution was cancelled."""
