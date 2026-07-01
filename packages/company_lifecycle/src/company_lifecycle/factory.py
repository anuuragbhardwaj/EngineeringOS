"""Lifecycle platform factory."""

from __future__ import annotations

from pathlib import Path

from company_lifecycle.installation.detector import discover_installed_framework
from company_lifecycle.platform import LifecyclePlatform


def create_lifecycle_platform(framework_root: Path | None = None) -> LifecyclePlatform:
    return LifecyclePlatform(framework_root=framework_root or discover_installed_framework())
