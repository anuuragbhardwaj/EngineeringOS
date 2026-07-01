"""Lifecycle platform types."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CompanyCreateRequest:
    """Non-interactive company creation parameters."""

    name: str
    target: Path
    instance_id: str
    framework_install_path: Path | None = None
    default_editor: str = "cursor"
    preferred_ai_provider: str = "cursor"
    preferred_mcp_profile: str = "default"
    default_language: str = "en"
    init_git: bool = False
    init_github: bool = False
    documentation_enabled: bool = True
    template_profile: str = "production"
    create_default_workspace: bool = True


@dataclass
class ProjectCreateOptions:
    """Project scaffolding options (lifecycle layer)."""

    name: str
    description: str
    platform: str
    production: bool
    technology_stack: str
    template_profile: str = "production"
    workspace_id: str | None = None
    location: Path | None = None
    run_planning_pipeline: bool = True


@dataclass
class MigrationPlan:
    """Planned migration steps — never overwrites user modifications."""

    from_version: str
    to_version: str
    steps: list[str] = field(default_factory=list)
    dry_run: bool = True
    safe: bool = True


@dataclass
class UpgradePlan:
    """Framework/company upgrade plan."""

    framework_from: str
    framework_to: str
    company_from: str
    company_to: str
    actions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class RepairAction:
    """Single repair action with guidance."""

    check: str
    action: str
    applied: bool = False
    message: str = ""


@dataclass
class RepairReport:
    """Repair results."""

    actions: list[RepairAction] = field(default_factory=list)

    @property
    def applied_count(self) -> int:
        return sum(1 for a in self.actions if a.applied)
