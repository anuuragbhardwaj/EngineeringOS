"""Shared Framework API result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class VersionInfo:
    framework_version: str
    framework_api_version: str
    cli_version: str
    manifest_version: str | None = None
    instance_id: str | None = None


@dataclass
class DoctorCheck:
    name: str
    passed: bool
    message: str


@dataclass
class DoctorReport:
    checks: list[DoctorCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)


@dataclass
class CompanyInstance:
    instance_id: str
    root: Path
    manifest_path: Path


@dataclass
class CompanyStatus:
    instance_id: str | None
    workspace_id: str | None
    project_id: str | None
    phase: str | None
    message: str


@dataclass
class ValidationReport:
    passed: bool
    checks: list[DoctorCheck] = field(default_factory=list)


@dataclass
class Workspace:
    workspace_id: str
    root: Path


@dataclass
class WorkspaceInfo:
    workspace_id: str
    project_count: int = 0


@dataclass
class Project:
    project_id: str
    root: Path


@dataclass
class ProjectInfo:
    project_id: str
    status: str = "unknown"


@dataclass
class CapabilityInfo:
    capability_id: str
    description: str


@dataclass
class McpInfo:
    mcp_id: str
    category: str
    installation_status: str


@dataclass
class HealthReport:
    passed: bool
    checks: list[DoctorCheck] = field(default_factory=list)


@dataclass
class EmployeeInfo:
    employee_id: str
    role: str
    phase: str | None = None
