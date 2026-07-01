"""Lifecycle platform errors."""

from __future__ import annotations


class LifecycleError(Exception):
    """Base lifecycle error."""


class FrameworkNotInstalledError(LifecycleError):
    """EngineeringOS framework is not installed."""


class OwnershipViolationError(LifecycleError):
    """Attempted to copy framework-owned assets into a generated company."""


class WorkspaceExistsError(LifecycleError):
    """Workspace already exists."""


class WorkspaceNotFoundError(LifecycleError):
    """Workspace not found."""


class ProjectExistsError(LifecycleError):
    """Project already exists."""


class TemplateNotFoundError(LifecycleError):
    """Template profile not found."""


class RepairError(LifecycleError):
    """Repair operation failed."""
