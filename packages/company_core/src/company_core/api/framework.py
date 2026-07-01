"""Framework API aggregate — single entry point for all consumers."""

from __future__ import annotations

from pathlib import Path

from company_core.api.company import CompanyAPI
from company_core.api.context import ContextAPI
from company_core.api.knowledge import KnowledgeAPI
from company_core.api.manifest import ManifestAPI
from company_core.api.mcp import McpAPI
from company_core.api.project import ProjectAPI
from company_core.api.stubs import EmployeeAPI, IntegrationAPI
from company_core.api.autonomous_company import AutonomousCompanyAPI
from company_core.api.parallel_execution import ParallelExecutionAPI
from company_core.api.source_control import SourceControlAPI
from company_core.api.workspace import WorkspaceAPI
from company_core.config.loader import discover_instance_root
from company_core.models.common import DoctorCheck, ValidationReport
from company_lifecycle.factory import create_lifecycle_platform
from workspace_execution.factory import create_execution_platform


class FrameworkAPI:
    """Unified Framework API facade per framework-api.md."""

    def __init__(
        self,
        instance_root: Path | None = None,
        cli_version: str = "0.1.0",
    ) -> None:
        root = instance_root or discover_instance_root()
        self.manifest = ManifestAPI(instance_root=root)
        self.company = CompanyAPI(self.manifest, cli_version=cli_version)
        self.workspace = WorkspaceAPI(instance_root=root)
        self.project = ProjectAPI(manifest=self.manifest.try_load())
        self.context = ContextAPI(instance_root=root)
        self.mcp = McpAPI()
        self.employee = EmployeeAPI()
        self.integration = IntegrationAPI()
        self.lifecycle = create_lifecycle_platform()
        self.execution = create_execution_platform()
        self.knowledge = KnowledgeAPI(instance_root=root)
        self.source_control = SourceControlAPI(instance_root=root)
        self.parallel_execution = ParallelExecutionAPI(instance_root=root)
        self.autonomous = AutonomousCompanyAPI(instance_root=root)

    def validate_all(self) -> ValidationReport:
        """Run lifecycle + manifest + MCP validation suite."""
        checks: list[DoctorCheck] = []

        root = self.manifest.instance_root or discover_instance_root()
        lifecycle_report = self.lifecycle.validate(root)
        checks.extend(lifecycle_report.checks)

        manifest = self.manifest.try_load()
        if manifest is None and not any(c.name == "company_manifest" for c in checks):
            checks.append(
                DoctorCheck("manifest", False, "company.yaml not found")
            )
        elif manifest is not None:
            errors = self.manifest.validate()
            if errors:
                for err in errors:
                    checks.append(
                        DoctorCheck(f"manifest:{err.field}", False, err.message)
                    )

        mcp_report = self.mcp.validate()
        checks.extend(mcp_report.checks)

        return ValidationReport(
            passed=all(c.passed for c in checks),
            checks=checks,
        )
