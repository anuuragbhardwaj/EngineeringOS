"""Parallel Execution Platform factory."""

from __future__ import annotations

from parallel_execution.platform import ParallelExecutionPlatform


def create_parallel_execution_platform() -> ParallelExecutionPlatform:
    return ParallelExecutionPlatform()
