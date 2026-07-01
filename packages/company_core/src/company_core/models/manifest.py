"""Company manifest models."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ValidationError:
    field: str
    message: str


@dataclass
class CompanyManifest:
    """Parsed company.yaml manifest."""

    instance_id: str
    instance_version: str
    schema_version: str
    framework_version: str
    install_path: Path | None
    workspaces_root: str
    default_workspace: str
    raw: dict[str, Any] = field(default_factory=dict)
    path: Path | None = None

    @property
    def root(self) -> Path | None:
        return self.path.parent if self.path else None
