"""Framework API aggregate — single entry point for all consumers."""

from __future__ import annotations

from pathlib import Path

from company_core.api.company import CompanyAPI
from company_core.api.manifest import ManifestAPI
from company_core.api.mcp import McpAPI
from company_core.api.project import ProjectAPI
from company_core.api.stubs import EmployeeAPI, IntegrationAPI, WorkspaceAPI
from company_core.config.loader import discover_instance_root
from company_core.models.common import DoctorCheck, ValidationReport


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
        self.workspace = WorkspaceAPI()
        self.project = ProjectAPI()
        self.mcp = McpAPI()
        self.employee = EmployeeAPI()
        self.integration = IntegrationAPI()

    def validate_all(self) -> ValidationReport:
        """Run manifest + MCP validation suite."""
        checks: list[DoctorCheck] = []

        manifest = self.manifest.try_load()
        if manifest is None:
            checks.append(
                DoctorCheck(
                    "manifest",
                    False,
                    "company.yaml not found",
                )
            )
        else:
            errors = self.manifest.validate()
            if errors:
                for err in errors:
                    checks.append(
                        DoctorCheck(
                            f"manifest:{err.field}",
                            False,
                            err.message,
                        )
                    )
            else:
                checks.append(
                    DoctorCheck("manifest", True, "Manifest schema valid")
                )

        mcp_report = self.mcp.validate()
        checks.extend(mcp_report.checks)

        return ValidationReport(
            passed=all(c.passed for c in checks),
            checks=checks,
        )
