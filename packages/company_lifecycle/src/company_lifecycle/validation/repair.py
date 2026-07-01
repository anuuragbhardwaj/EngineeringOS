"""Repair utilities with actionable guidance."""

from __future__ import annotations

from pathlib import Path

from company_core.config.loader import MANIFEST_FILENAME, load_manifest
from company_lifecycle.installation.detector import discover_installed_framework
from company_lifecycle.manifest.generator import write_company_manifest
from company_lifecycle.types import RepairAction, RepairReport
from company_lifecycle.validation.checks import run_full_validation
from company_lifecycle.workspace.manager import create_workspace, list_workspaces


def repair(instance_root: Path, *, apply: bool = True) -> RepairReport:
    """Repair common lifecycle issues — never overwrites user modifications."""
    instance_root = instance_root.resolve()
    actions: list[RepairAction] = []
    checks = run_full_validation(instance_root)

    for check in checks:
        if check["passed"]:
            continue
        name = check["name"]
        if name == "workspaces_directory" and apply:
            path = Path(check["message"])
            path.mkdir(parents=True, exist_ok=True)
            actions.append(
                RepairAction(name, "create_workspaces_directory", True, f"Created {path}")
            )
        elif name == "framework_reference" and apply:
            manifest = load_manifest(instance_root / MANIFEST_FILENAME)
            framework = discover_installed_framework()
            if framework:
                data = manifest.raw
                data.setdefault("company", {}).setdefault("framework", {})["install_path"] = str(framework)
                write_company_manifest(instance_root, data)
                actions.append(
                    RepairAction(
                        name,
                        "set_framework_install_path",
                        True,
                        f"Set framework.install_path to {framework}",
                    )
                )
            else:
                actions.append(
                    RepairAction(
                        name,
                        "set_framework_install_path",
                        False,
                        "Install EngineeringOS framework first",
                    )
                )
        else:
            actions.append(
                RepairAction(
                    name,
                    _guidance_for(name),
                    False,
                    check["message"],
                )
            )

    # Ensure default workspace exists
    if apply and (instance_root / MANIFEST_FILENAME).is_file():
        manifest = load_manifest(instance_root / MANIFEST_FILENAME)
        default_ws = manifest.default_workspace
        if default_ws not in list_workspaces(instance_root):
            create_workspace(instance_root, default_ws)
            actions.append(
                RepairAction(
                    "default_workspace",
                    "create_default_workspace",
                    True,
                    f"Created workspace '{default_ws}'",
                )
            )

    return RepairReport(actions=actions)


def _guidance_for(check_name: str) -> str:
    guidance = {
        "company_manifest": "Run engineeringos init in the target directory",
        "framework_installed": "pip install -e . from EngineeringOS repository",
        "workspace": "Run engineeringos workspace create <id>",
        "project_manifest": "Re-run engineeringos project create or repair",
    }
    return guidance.get(check_name, "Review docs/audit/ and engineeringos doctor")
