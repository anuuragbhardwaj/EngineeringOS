"""AI Execution Platform — permanent boundary between EngineeringOS and AI providers."""

from ai_execution.version import PLATFORM_VERSION

__version__ = PLATFORM_VERSION

__all__ = ["PLATFORM_VERSION", "__version__", "create_platform", "create_runtime_adapter"]


def create_platform(*args, **kwargs):
    from ai_execution.factory import create_platform as _create

    return _create(*args, **kwargs)


def create_runtime_adapter(*args, **kwargs):
    from ai_execution.adapter.runtime_adapter import create_runtime_adapter as _create

    return _create(*args, **kwargs)
