"""Knowledge Platform errors."""

from __future__ import annotations


class KnowledgeError(Exception):
    """Base knowledge platform error."""


class KnowledgeNotFoundError(KnowledgeError):
    """Requested knowledge object does not exist."""


class KnowledgeValidationError(KnowledgeError):
    """Knowledge failed validation."""


class KnowledgePromotionError(KnowledgeError):
    """Knowledge promotion rejected or failed."""


class KnowledgeConflictError(KnowledgeError):
    """Knowledge conflicts with existing records."""
