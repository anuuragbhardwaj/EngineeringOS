"""CompanyAPI implementation."""

from __future__ import annotations

from pathlib import Path

from company_core.api.manifest import ManifestAPI
from company_core.config.loader import (
    discover_framework_root,
    discover_instance_root,
    write_manifest,
)
from company_core.models.common import (
    CompanyInstance,
    CompanyStatus,
    DoctorCheck,
    DoctorReport,
    VersionInfo,
)
from company_core.models.errors import ManifestNotFoundError, NotImplementedFeatureError
from company_core.version import FRAMEWORK_API_VERSION, FRAMEWORK_VERSION


class CompanyAPI:
    """Company instance operations — delegates manifest to ManifestAPI."""

    def __init__(self, manifest_api: ManifestAPI, cli_version: str = "0.1.0") -> None:
        self._manifest = manifest_api
        self._cli_version = cli_version
        self._active_instance: CompanyInstance | None = None

    def init(self, target: Path, template: str | None = None) -> CompanyInstance:
        target = target.resolve()
        manifest_path = target / "company.yaml"
        if manifest_path.exists():
            raise FileExistsError(f"Company already exists at {target}")

        instance_id = template or "default"
        write_manifest(target, instance_id=instance_id)
        workspaces_dir = target / "workspaces"
        workspaces_dir.mkdir(parents=True, exist_ok=True)

        instance = CompanyInstance(
            instance_id=instance_id,
            root=target,
            manifest_path=manifest_path,
        )
        self._active_instance = instance
        return instance

    def create(self, instance_id: str, config: object = None) -> CompanyInstance:
        raise NotImplementedFeatureError("company create is not yet implemented")

    def open(self, instance_id: str | None = None) -> CompanyInstance:
        raise NotImplementedFeatureError("company open is not yet implemented")

    def doctor(self) -> DoctorReport:
        checks: list[DoctorCheck] = []
        root = discover_instance_root()

        if root is None:
            checks.append(
                DoctorCheck(
                    "manifest",
                    False,
                    "company.yaml not found — run `engineeringos init`",
                )
            )
            return DoctorReport(checks=checks)

        checks.append(
            DoctorCheck("manifest", True, f"Found company.yaml at {root}")
        )

        manifest = self._manifest.load(root / "company.yaml")
        validation = self._manifest.validate()
        if validation:
            for err in validation:
                checks.append(
                    DoctorCheck("manifest_schema", False, f"{err.field}: {err.message}")
                )
        else:
            checks.append(DoctorCheck("manifest_schema", True, "Manifest schema valid"))

        workspaces = root / manifest.workspaces_root.rstrip("/")
        if workspaces.is_dir():
            checks.append(
                DoctorCheck("workspaces", True, f"Workspaces directory exists: {workspaces}")
            )
        else:
            checks.append(
                DoctorCheck(
                    "workspaces",
                    False,
                    f"Missing workspaces directory: {workspaces}",
                )
            )

        framework_root = discover_framework_root(root)
        if framework_root is None:
            checks.append(
                DoctorCheck(
                    "framework",
                    False,
                    "Framework root not found — set framework.install_path in company.yaml",
                )
            )
        else:
            checks.append(
                DoctorCheck(
                    "framework",
                    True,
                    f"Framework root: {framework_root}",
                )
            )
            mcp_report = self._run_mcp_validate(framework_root)
            checks.extend(mcp_report)

        return DoctorReport(checks=checks)

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
        return CompanyStatus(
            instance_id=manifest.instance_id,
            workspace_id=manifest.default_workspace,
            project_id=None,
            phase=None,
            message="Status summary — full runtime status not yet implemented.",
        )

    def upgrade(self, version: str | None = None) -> object:
        raise NotImplementedFeatureError("company upgrade is not yet implemented")

    def migrate(self, dry_run: bool = False) -> object:
        raise NotImplementedFeatureError("company migrate is not yet implemented")

    def version(self) -> VersionInfo:
        manifest = self._manifest.try_load()
        return VersionInfo(
            framework_version=FRAMEWORK_VERSION,
            framework_api_version=FRAMEWORK_API_VERSION,
            cli_version=self._cli_version,
            manifest_version=manifest.instance_version if manifest else None,
            instance_id=manifest.instance_id if manifest else None,
        )

    def _run_mcp_validate(self, framework_root: Path) -> list[DoctorCheck]:
        try:
            from mcp_platform.validator import validate_all
        except ImportError:
            return [
                DoctorCheck(
                    "mcp_platform",
                    False,
                    "mcp_platform package not installed",
                )
            ]

        results = validate_all(framework_root)
        return [
            DoctorCheck(
                f"mcp:{r.check}",
                r.passed,
                r.message,
            )
            for r in results
        ]
