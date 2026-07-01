"""Validation checks for lifecycle platform."""

from __future__ import annotations

from pathlib import Path

from company_core.config.loader import MANIFEST_FILENAME, discover_framework_root, load_manifest, validate_manifest_structure
from company_lifecycle.filesystem.boundaries import FRAMEWORK_OWNED
from company_lifecycle.installation.detector import discover_installed_framework, is_framework_installed


def check_framework_installation() -> list[dict]:
    checks: list[dict] = []
    installed = is_framework_installed()
    root = discover_installed_framework()
    checks.append(
        {
            "name": "framework_installed",
            "passed": installed,
            "message": f"Framework root: {root}" if root else "Install EngineeringOS: pip install -e .",
        }
    )
    if root:
        for required in ("workflow.yaml", "runtime/interfaces.md", "packages"):
            path = root / required
            checks.append(
                {
                    "name": f"framework:{required}",
                    "passed": path.exists(),
                    "message": str(path),
                }
            )
    return checks


def check_company(instance_root: Path) -> list[dict]:
    checks: list[dict] = []
    manifest_path = instance_root / MANIFEST_FILENAME
    if not manifest_path.is_file():
        return [{"name": "company_manifest", "passed": False, "message": "company.yaml missing"}]

    checks.append({"name": "company_manifest", "passed": True, "message": str(manifest_path)})
    manifest = load_manifest(manifest_path)
    for err in validate_manifest_structure(manifest):
        checks.append({"name": f"manifest:{err.field}", "passed": False, "message": err.message})

    install_path = manifest.install_path
    if install_path and install_path.is_dir():
        checks.append(
            {
                "name": "framework_reference",
                "passed": True,
                "message": f"References framework at {install_path}",
            }
        )
    else:
        resolved = discover_framework_root(instance_root)
        checks.append(
            {
                "name": "framework_reference",
                "passed": resolved is not None,
                "message": (
                    f"Resolved framework: {resolved}"
                    if resolved
                    else "Set framework.install_path in company.yaml"
                ),
            }
        )

    for forbidden in FRAMEWORK_OWNED:
        bad = instance_root / forbidden
        if bad.exists() and forbidden in {"packages", "runtime_engine", "orchestrator"}:
            checks.append(
                {
                    "name": f"ownership:{forbidden}",
                    "passed": False,
                    "message": f"Framework asset must not exist in company: {forbidden}",
                }
            )

    ws_root = instance_root / manifest.workspaces_root.strip("/")
    checks.append(
        {
            "name": "workspaces_directory",
            "passed": ws_root.is_dir(),
            "message": str(ws_root),
        }
    )
    return checks


def check_workspace_layout(workspace_root: Path, workspace_id: str) -> list[dict]:
    checks: list[dict] = []
    if not workspace_root.is_dir():
        return [{"name": "workspace", "passed": False, "message": f"Missing workspace: {workspace_id}"}]
    checks.append({"name": "workspace", "passed": True, "message": str(workspace_root)})
    for rel in (".company/workspace.yaml", "projects"):
        path = workspace_root / rel
        checks.append(
            {
                "name": f"workspace:{rel}",
                "passed": path.exists(),
                "message": str(path),
            }
        )
    return checks


def check_project(project_root: Path, project_id: str) -> list[dict]:
    checks: list[dict] = []
    if not project_root.is_dir():
        return [{"name": "project", "passed": False, "message": f"Missing project: {project_id}"}]
    checks.append({"name": "project", "passed": True, "message": str(project_root)})
    meta = project_root / ".company-project.yaml"
    checks.append(
        {
            "name": "project_manifest",
            "passed": meta.is_file(),
            "message": str(meta),
        }
    )
    return checks


def run_full_validation(instance_root: Path | None) -> list[dict]:
    checks = check_framework_installation()
    if instance_root and (instance_root / MANIFEST_FILENAME).is_file():
        checks.extend(check_company(instance_root))
    return checks
