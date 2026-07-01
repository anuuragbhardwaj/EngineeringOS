"""Source Control Platform factory."""

from __future__ import annotations

from source_control.platform import SourceControlPlatform


def create_source_control_platform() -> SourceControlPlatform:
    return SourceControlPlatform()
