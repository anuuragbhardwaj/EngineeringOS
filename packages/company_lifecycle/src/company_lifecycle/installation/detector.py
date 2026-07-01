"""Detect installed EngineeringOS framework."""

from __future__ import annotations

import os
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def discover_installed_framework() -> Path | None:
    """Resolve the installed EngineeringOS framework root."""
    env_root = os.environ.get("ENGINEERINGOS_FRAMEWORK_ROOT")
    if env_root:
        path = Path(env_root).expanduser().resolve()
        if _is_framework_root(path):
            return path

    # Editable / dev install: walk from company_core package location
    try:
        import company_core

        package_dir = Path(company_core.__file__).resolve().parent
        candidates = [
            package_dir.parents[3],  # packages/company_core/src/company_core -> repo root
            package_dir.parents[2],
            package_dir.parents[1],
        ]
        for candidate in candidates:
            if _is_framework_root(candidate):
                return candidate
    except ImportError:
        pass

    # Heuristic from cwd
    cwd = Path.cwd().resolve()
    for directory in [cwd, *cwd.parents]:
        if _is_framework_root(directory):
            return directory

    return None


def framework_version() -> str:
    """Return installed framework package version."""
    try:
        return version("ai-company")
    except PackageNotFoundError:
        return "2.0.0"


def is_framework_installed() -> bool:
    """True when EngineeringOS framework root is discoverable."""
    return discover_installed_framework() is not None


def python_info() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def _is_framework_root(path: Path) -> bool:
    return (
        path.is_dir()
        and (path / "workflow.yaml").is_file()
        and (path / "runtime" / "interfaces.md").is_file()
        and (path / "packages").is_dir()
    )
