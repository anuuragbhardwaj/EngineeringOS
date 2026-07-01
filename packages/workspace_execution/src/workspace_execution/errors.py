"""Workspace execution errors."""

from __future__ import annotations


class ExecutionContextError(Exception):
    """Base execution context error."""


class NoActiveCompanyError(ExecutionContextError):
    """No active company session."""


class NoActiveWorkspaceError(ExecutionContextError):
    """No active workspace in session."""


class NoActiveProjectError(ExecutionContextError):
    """No active project in session."""


class SessionNotFoundError(ExecutionContextError):
    """Execution session file not found."""
