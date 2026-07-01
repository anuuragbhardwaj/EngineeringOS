"""Source Control Platform errors."""

from __future__ import annotations


class SourceControlError(Exception):
    """Base source control error."""


class RepositoryNotFoundError(SourceControlError):
    """No repository discovered for active context."""


class RepositoryValidationError(SourceControlError):
    """Repository failed validation."""


class ApprovalRequiredError(SourceControlError):
    """Engineering Manager approval required."""


class ProviderNotAvailableError(SourceControlError):
    """Requested provider is not available."""


class GitCommandError(SourceControlError):
    """Git command failed."""
