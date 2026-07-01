"""Lifecycle platform facade."""

from __future__ import annotations

from pathlib import Path

from company_core.config.loader import discover_instance_root
from company_core.models.common import CompanyInstance, DoctorCheck, DoctorReport, Workspace, WorkspaceInfo
from company_lifecycle.company.generator import generate_company
from company_lifecycle.installation.detector import discover_installed_framework, framework_version, is_framework_installed
from company_lifecycle.project.manager import (
    archive_project,
    clone_project,
    list_projects,
    remove_project,
    scaffold_project,
)
from company_lifecycle.templates.engine import list_profiles
from company_lifecycle.types import (
    CompanyCreateRequest,
    MigrationPlan,
    ProjectCreateOptions,
    RepairReport,
    UpgradePlan,
)
from company_lifecycle.upgrade.planner import apply_upgrade_manifest_pin, plan_migration, plan_upgrade
from company_lifecycle.validation.checks import run_full_validation
from company_lifecycle.validation.repair import repair
from company_lifecycle.workspace.manager import (
    archive_workspace,
    create_workspace,
    list_workspaces,
    remove_workspace,
    validate_workspace,
    workspace_info,
)
from workspace_execution.factory import create_execution_platform


class LifecyclePlatform:
    """Installation & lifecycle operations for EngineeringOS."""

    def __init__(self, framework_root: Path | None = None) -> None:
        self._framework_root = framework_root or discover_installed_framework()
        self._execution = create_execution_platform()

    @property
    def framework_root(self) -> Path | None:
        return self._framework_root

    def is_framework_installed(self) -> bool:
        return is_framework_installed()

    def init_company(self, request: CompanyCreateRequest) -> CompanyInstance:
        manifest_path = generate_company(request)
        instance = CompanyInstance(
            instance_id=request.instance_id,
            root=request.target.resolve(),
            manifest_path=manifest_path,
        )
        if request.create_default_workspace:
            create_workspace(instance.root, "default")
            self._execution.open_company(instance.root, workspace_id="default")
        return instance

    def open_company(self, instance_root: Path | None = None, workspace_id: str | None = None):
        root = (instance_root or discover_instance_root())
        if root is None:
            from company_core.models.errors import ManifestNotFoundError

            raise ManifestNotFoundError("company.yaml not found")
        return self._execution.open_company(root.resolve(), workspace_id=workspace_id)

    def doctor(self, instance_root: Path | None = None) -> DoctorReport:
        root = instance_root or discover_instance_root()
        checks = run_full_validation(root)
        return DoctorReport(
            checks=[
                DoctorCheck(c["name"], c["passed"], c["message"])
                for c in checks
            ]
        )

    def validate(self, instance_root: Path | None = None) -> DoctorReport:
        return self.doctor(instance_root)

    def repair_company(self, instance_root: Path | None = None, *, apply: bool = True) -> RepairReport:
        root = instance_root or discover_instance_root()
        if root is None:
            from company_core.models.errors import ManifestNotFoundError

            raise ManifestNotFoundError("company.yaml not found")
        return repair(root.resolve(), apply=apply)

    def plan_upgrade(self, instance_root: Path | None = None, version: str | None = None) -> UpgradePlan:
        root = instance_root or discover_instance_root()
        if root is None:
            from company_core.models.errors import ManifestNotFoundError

            raise ManifestNotFoundError("company.yaml not found")
        return plan_upgrade(root.resolve(), version)

    def upgrade(self, instance_root: Path | None = None, version: str | None = None) -> UpgradePlan:
        root = instance_root or discover_instance_root()
        if root is None:
            from company_core.models.errors import ManifestNotFoundError

            raise ManifestNotFoundError("company.yaml not found")
        plan = plan_upgrade(root.resolve(), version)
        apply_upgrade_manifest_pin(root.resolve(), plan.framework_to)
        return plan

    def migrate(self, instance_root: Path | None = None, *, dry_run: bool = True) -> MigrationPlan:
        root = instance_root or discover_instance_root()
        if root is None:
            from company_core.models.errors import ManifestNotFoundError

            raise ManifestNotFoundError("company.yaml not found")
        return plan_migration(root.resolve(), dry_run=dry_run)

    def uninstall_company(self, instance_root: Path) -> None:
        """Remove generated company — never touches installed framework."""
        import shutil

        target = instance_root.resolve()
        framework = self._framework_root
        if framework and target.resolve() == framework.resolve():
            raise ValueError("Cannot uninstall the EngineeringOS framework directory")
        if target.is_dir():
            shutil.rmtree(target)

    # Workspace
    def create_workspace(self, workspace_id: str, instance_root: Path | None = None) -> Workspace:
        root = (instance_root or discover_instance_root())
        if root is None:
            from company_core.models.errors import ManifestNotFoundError

            raise ManifestNotFoundError("company.yaml not found")
        path = create_workspace(root.resolve(), workspace_id)
        return Workspace(workspace_id=workspace_id, root=path)

    def list_workspaces(self, instance_root: Path | None = None) -> list[WorkspaceInfo]:
        root = instance_root or discover_instance_root()
        if root is None:
            return []
        return [
            WorkspaceInfo(
                workspace_id=wid,
                project_count=workspace_info(root, wid)["project_count"],
            )
            for wid in list_workspaces(root.resolve())
        ]

    def archive_workspace(self, workspace_id: str, instance_root: Path | None = None) -> Workspace:
        root = (instance_root or discover_instance_root())
        if root is None:
            from company_core.models.errors import ManifestNotFoundError

            raise ManifestNotFoundError("company.yaml not found")
        path = archive_workspace(root.resolve(), workspace_id)
        return Workspace(workspace_id=workspace_id, root=path)

    def remove_workspace(self, workspace_id: str, instance_root: Path | None = None) -> None:
        root = (instance_root or discover_instance_root())
        if root is None:
            from company_core.models.errors import ManifestNotFoundError

            raise ManifestNotFoundError("company.yaml not found")
        remove_workspace(root.resolve(), workspace_id)

    def validate_workspace(self, workspace_id: str, instance_root: Path | None = None) -> DoctorReport:
        root = (instance_root or discover_instance_root())
        if root is None:
            from company_core.models.errors import ManifestNotFoundError

            raise ManifestNotFoundError("company.yaml not found")
        checks = validate_workspace(root.resolve(), workspace_id)
        return DoctorReport(
            checks=[DoctorCheck(c["name"], c["passed"], c["message"]) for c in checks]
        )

    # Project scaffolding
    def scaffold_project(self, instance_root: Path, options: ProjectCreateOptions) -> tuple[Path, str, str]:
        return scaffold_project(instance_root.resolve(), options)

    def clone_project(
        self,
        source: Path,
        name: str,
        workspace_id: str | None = None,
        instance_root: Path | None = None,
    ) -> Path:
        root = instance_root or discover_instance_root()
        if root is None:
            from company_core.models.errors import ManifestNotFoundError

            raise ManifestNotFoundError("company.yaml not found")
        return clone_project(root.resolve(), source, name, workspace_id)

    def list_projects(self, workspace_id: str | None = None, instance_root: Path | None = None) -> list[dict]:
        root = instance_root or discover_instance_root()
        if root is None:
            return []
        return list_projects(root.resolve(), workspace_id)

    def archive_project(
        self,
        project_id: str,
        workspace_id: str | None = None,
        instance_root: Path | None = None,
    ) -> Path:
        root = instance_root or discover_instance_root()
        if root is None:
            from company_core.models.errors import ManifestNotFoundError

            raise ManifestNotFoundError("company.yaml not found")
        return archive_project(root.resolve(), project_id, workspace_id)

    def remove_project(
        self,
        project_id: str,
        workspace_id: str | None = None,
        instance_root: Path | None = None,
    ) -> None:
        root = instance_root or discover_instance_root()
        if root is None:
            from company_core.models.errors import ManifestNotFoundError

            raise ManifestNotFoundError("company.yaml not found")
        remove_project(root.resolve(), project_id, workspace_id)

    def list_template_profiles(self) -> list[str]:
        return list_profiles()

    def framework_version(self) -> str:
        return framework_version()
