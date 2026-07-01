"""Workspace execution factory."""

from __future__ import annotations

from workspace_execution.platform import WorkspaceExecutionPlatform


def create_execution_platform() -> WorkspaceExecutionPlatform:
    return WorkspaceExecutionPlatform()
