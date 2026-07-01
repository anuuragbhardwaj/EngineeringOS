"""Framework API error taxonomy."""

from __future__ import annotations


class FrameworkError(Exception):
    """Base error for Framework API."""


class ManifestError(FrameworkError):
    """Manifest loading or validation failed."""


class ManifestNotFoundError(ManifestError):
    """company.yaml not found."""


class KeyNotFoundError(ManifestError):
    """Manifest key could not be resolved."""


class CompanyNotFoundError(FrameworkError):
    """Company instance not found."""


class WorkspaceNotFoundError(FrameworkError):
    """Workspace not found."""


class ProjectNotFoundError(FrameworkError):
    """Project not found."""


class IntegrationError(FrameworkError):
    """Editor integration operation failed."""


class McpValidationError(FrameworkError):
    """MCP validation failed."""


class NotImplementedFeatureError(FrameworkError):
    """Feature is planned but not yet implemented."""
