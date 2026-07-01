"""CompanyAPI implementation — delegates lifecycle to company_lifecycle."""

from __future__ import annotations

from pathlib import Path

from company_core.api.manifest import ManifestAPI
from company_core.config.loader import discover_instance_root
from company_core.models.common import (
    CompanyInstance,
    CompanyStatus,
    DoctorReport,
    VersionInfo,
)
from company_core.models.errors import ManifestNotFoundError
from company_core.version import FRAMEWORK_API_VERSION, FRAMEWORK_VERSION
from company_lifecycle.factory import create_lifecycle_platform
from company_lifecycle.types import CompanyCreateRequest, MigrationPlan, UpgradePlan


class CompanyAPI:
    """Company instance operations."""

    def __init__(self, manifest_api: ManifestAPI, cli_version: str = "0.1.0") -> None:
        self._manifest = manifest_api
        self._cli_version = cli_version
        self._lifecycle = create_lifecycle_platform()
        self._active_instance: CompanyInstance | None = None

    def init(self, target: Path, template: str | None = None) -> CompanyInstance:
        request = CompanyCreateRequest(
            name=template or "default",
            target=target,
            instance_id=template or "default",
        )
        instance = self._lifecycle.init_company(request)
        self._active_instance = instance
        return instance

    def create(self, request: CompanyCreateRequest) -> CompanyInstance:
        instance = self._lifecycle.init_company(request)
        self._active_instance = instance
        return instance

    def open(self, instance_id: str | None = None, workspace_id: str | None = None) -> CompanyInstance:
        root = self._manifest.instance_root or discover_instance_root()
        if root is None:
            raise ManifestNotFoundError("company.yaml not found")
        self._lifecycle.open_company(root, workspace_id=workspace_id)
        manifest = self._manifest.load()
        if instance_id and manifest.instance_id != instance_id:
            raise ManifestNotFoundError(f"Company instance not found: {instance_id}")
        instance = CompanyInstance(
            instance_id=manifest.instance_id,
            root=root,
            manifest_path=root / "company.yaml",
        )
        self._active_instance = instance
        return instance

    def doctor(self) -> DoctorReport:
        root = self._manifest.instance_root or discover_instance_root()
        report = self._lifecycle.doctor(root)
        if root is not None:
            mcp_checks = self._run_mcp_validate_from_root(root)
            report.checks.extend(mcp_checks)
        return report

    def status(self) -> CompanyStatus:
        manifest = self._manifest.try_load()
        if manifest is None:
            return CompanyStatus(
                instance_id=None,
                workspace_id=None,
                project_id=None,
                phase=None,
                message="No company instance found. Run `engineeringos init`.",
            )
        from workspace_execution.factory import create_execution_platform

        unified = create_execution_platform().status(manifest.root)
        return CompanyStatus(
            instance_id=manifest.instance_id,
            workspace_id=unified.workspace_id,
            project_id=unified.project_id,
            phase=unified.current_phase,
            message=unified.message,
        )

    def upgrade(self, version: str | None = None) -> UpgradePlan:
        root = self._manifest.instance_root or discover_instance_root()
        if root is None:
            raise ManifestNotFoundError("company.yaml not found")
        return self._lifecycle.upgrade(root, version)

    def plan_upgrade(self, version: str | None = None) -> UpgradePlan:
        root = self._manifest.instance_root or discover_instance_root()
        if root is None:
            raise ManifestNotFoundError("company.yaml not found")
        return self._lifecycle.plan_upgrade(root, version)

    def migrate(self, dry_run: bool = True) -> MigrationPlan:
        root = self._manifest.instance_root or discover_instance_root()
        if root is None:
            raise ManifestNotFoundError("company.yaml not found")
        return self._lifecycle.migrate(root, dry_run=dry_run)

    def repair(self, *, apply: bool = True) -> object:
        root = self._manifest.instance_root or discover_instance_root()
        if root is None:
            raise ManifestNotFoundError("company.yaml not found")
        return self._lifecycle.repair_company(root, apply=apply)

    def uninstall(self, target: Path) -> None:
        self._lifecycle.uninstall_company(target)

    def version(self) -> VersionInfo:
        manifest = self._manifest.try_load()
        return VersionInfo(
            framework_version=FRAMEWORK_VERSION,
            framework_api_version=FRAMEWORK_API_VERSION,
            cli_version=self._cli_version,
            manifest_version=manifest.instance_version if manifest else None,
            instance_id=manifest.instance_id if manifest else None,
        )

    def _run_mcp_validate_from_root(self, instance_root: Path) -> list:
        from company_core.config.loader import discover_framework_root
        from company_core.models.common import DoctorCheck

        framework_root = discover_framework_root(instance_root)
        if framework_root is None:
            return []
        try:
            from mcp_platform.validator import validate_all
        except ImportError:
            return [
                DoctorCheck("mcp_platform", False, "mcp_platform package not installed")
            ]
        return [
            DoctorCheck(f"mcp:{r.check}", r.passed, r.message)
            for r in validate_all(framework_root)
        ]
