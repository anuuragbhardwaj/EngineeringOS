"""Company manifest generation for generated companies."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from company_core.config.loader import MANIFEST_FILENAME
from company_lifecycle.types import CompanyCreateRequest


def build_company_manifest(request: CompanyCreateRequest, framework_version: str) -> dict[str, Any]:
    """Build company.yaml — references installed framework, never embeds framework assets."""
    install_path = str(request.framework_install_path) if request.framework_install_path else None
    return {
        "company": {
            "name": request.name,
            "instance_id": request.instance_id,
            "instance_version": "1.0.0",
            "schema_version": "1.0.0",
            "framework": {
                "version": framework_version,
                "install_path": install_path,
            },
            "employees": {"directory": None},
            "policies": {"handbook": None},
            "templates": {
                "directory": None,
                "version": framework_version,
                "default_profile": request.template_profile,
            },
            "standards": {"workflow": None},
            "manifest": MANIFEST_FILENAME,
            "mcp_profiles": {"default": request.preferred_mcp_profile},
            "configuration": {
                "workspaces_root": "workspaces/",
                "default_workspace": "default",
                "default_editor": request.default_editor,
                "preferred_ai_provider": request.preferred_ai_provider,
                "default_language": request.default_language,
                "documentation_enabled": request.documentation_enabled,
            },
            "integrations": {
                "git": {"enabled": request.init_git},
                "github": {"enabled": request.init_github},
            },
            "workspaces": [],
        }
    }


def write_company_manifest(target: Path, data: dict[str, Any]) -> Path:
    target.mkdir(parents=True, exist_ok=True)
    manifest_path = target / MANIFEST_FILENAME
    with manifest_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, default_flow_style=False)
    return manifest_path


def update_manifest_workspaces(manifest_path: Path, workspace_ids: list[str]) -> None:
    with manifest_path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    company = data.setdefault("company", {})
    company["workspaces"] = sorted(set(workspace_ids))
    with manifest_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, default_flow_style=False)
