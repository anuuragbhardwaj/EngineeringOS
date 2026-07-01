"""Workspace Execution Platform."""

from workspace_execution.version import EXECUTION_PLATFORM_VERSION

__version__ = EXECUTION_PLATFORM_VERSION

__all__ = [
    "EXECUTION_PLATFORM_VERSION",
    "__version__",
    "create_execution_platform",
    "WorkspaceExecutionPlatform",
    "ContextResolver",
]


def __getattr__(name: str):
    if name == "create_execution_platform":
        from workspace_execution.factory import create_execution_platform as _create

        return _create
    if name == "WorkspaceExecutionPlatform":
        from workspace_execution.platform import WorkspaceExecutionPlatform as _Platform

        return _Platform
    if name == "ContextResolver":
        from workspace_execution.resolver.resolver import ContextResolver as _Resolver

        return _Resolver
    raise AttributeError(name)
