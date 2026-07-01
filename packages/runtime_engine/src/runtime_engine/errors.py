"""Kernel error taxonomy."""

from __future__ import annotations


class KernelError(Exception):
    """Base kernel error."""


class WorkflowNotFoundError(KernelError):
    pass


class WorkflowParseError(KernelError):
    pass


class WorkflowSchemaError(KernelError):
    pass


class ProjectNotFoundError(KernelError):
    pass


class StateCorruptError(KernelError):
    pass


class StorageError(KernelError):
    pass


class TransitionError(KernelError):
    pass


class PhaseNotFoundError(KernelError):
    pass


class GateNotFoundError(KernelError):
    pass


class ProjectBlockedError(KernelError):
    pass


class ReworkRoutingError(KernelError):
    pass


class ReworkNotFoundError(KernelError):
    pass


class ArtifactNotFoundError(KernelError):
    pass


class AdapterInvocationError(KernelError):
    pass


class AdapterUnavailableError(KernelError):
    pass


class OrchestratorOnlyError(KernelError):
    """Runtime attempted to invoke a non-orchestrator agent directly."""
