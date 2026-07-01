"""Orchestrator error taxonomy."""

from __future__ import annotations


class OrchestratorError(Exception):
    pass


class ApprovalRequiredError(OrchestratorError):
    """Execution paused pending human approval."""


class CheckpointPausedError(OrchestratorError):
    """Execution paused at checkpoint."""


class PolicyViolationError(OrchestratorError):
    pass


class ContextAssemblyError(OrchestratorError):
    pass
