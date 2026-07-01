"""Autonomous company errors."""

from __future__ import annotations


class AutonomousError(Exception):
    """Base autonomous platform error."""


class BlockerError(AutonomousError):
    """Execution blocked — human intervention required."""


class GoalNotFoundError(AutonomousError):
    """Goal not found."""


class AutonomousStoppedError(AutonomousError):
    """Autonomous execution stopped by user."""
