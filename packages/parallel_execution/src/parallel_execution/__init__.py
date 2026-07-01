"""EngineeringOS Parallel Execution Engine."""

from parallel_execution.version import PARALLEL_EXECUTION_VERSION, __version__

__all__ = ["PARALLEL_EXECUTION_VERSION", "__version__", "create_parallel_execution_platform"]


def create_parallel_execution_platform(*args, **kwargs):
    from parallel_execution.factory import create_parallel_execution_platform as _create

    return _create(*args, **kwargs)
