"""AI Execution Platform error taxonomy."""

from __future__ import annotations


class ExecutionError(Exception):
    """Base execution platform error."""


class ProviderNotFoundError(ExecutionError):
    pass


class ProviderUnavailableError(ExecutionError):
    pass


class CapabilityNotSupportedError(ExecutionError):
    pass


class ExecutionTimeoutError(ExecutionError):
    pass


class RateLimitError(ExecutionError):
    pass


class InvalidResponseError(ExecutionError):
    pass


class ConversationCorruptError(ExecutionError):
    pass


class ProviderPlaceholderError(ExecutionError):
    """Provider exists as placeholder only — not yet implemented."""
