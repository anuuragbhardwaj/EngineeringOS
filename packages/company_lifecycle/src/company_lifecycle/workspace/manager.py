"""Workspace lifecycle management."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml

from company_core.config.loader import MANIFEST_FILENAME, load_manifest
from company_lifecycle.errors import WorkspaceExistsError, WorkspaceNotFoundError
from company_lifecycle.manifest.generator import update_manifest_workspaces


def workspace_root(instance_root: Path, workspace_id: str, workspaces_root: str = "workspaces/") -> Path:
    return instance_root / workspaces_root.strip("/") / workspace_id


def create_workspace(instance_root: Path, workspace_id: str) -> Path:
    instance_root = instance_root.resolve()
    manifest = load_manifest(instance_root / MANIFEST_FILENAME)
    root = workspace_root(instance_root, workspace_id, manifest.workspaces_root)

    if root.exists():
        raise WorkspaceExistsError(f"Workspace already exists: {workspace_id}")

    root.mkdir(parents=True)
    (root / "projects").mkdir()
    (root / "extensions").mkdir(exist_ok=True)
    (root / "user").mkdir(exist_ok=True)

    company_dir = root / ".company"
    company_dir.mkdir()
    (company_dir / "state").mkdir()
    (company_dir / "cache").mkdir()
    (company_dir / "events").mkdir(exist_ok=True)

    workspace_yaml = company_dir / "workspace.yaml"
    workspace_yaml.write_text(
        yaml.safe_dump(
            {
                "workspace": {
                    "id": workspace_id,
                    "status": "active",
                    "created_at": datetime.utcnow().isoformat(),
                    "projects": [],
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    existing = list_workspaces(instance_root)
    if workspace_id not in existing:
        existing.append(workspace_id)
    update_manifest_workspaces(instance_root / MANIFEST_FILENAME, existing)
    return root


def list_workspaces(instance_root: Path) -> list[str]:
    instance_root = instance_root.resolve()
    manifest_path = instance_root / MANIFEST_FILENAME
    if not manifest_path.is_file():
        return []
    manifest = load_manifest(manifest_path)
    registered = manifest.raw.get("company", {}).get("workspaces") or []
    ws_root = instance_root / manifest.workspaces_root.strip("/")
    if not ws_root.is_dir():
        return list(registered)
    on_disk = [p.name for p in ws_root.iterdir() if p.is_dir() and not p.name.startswith(".")]
    return sorted(set(registered) | set(on_disk))


def workspace_info(instance_root: Path, workspace_id: str) -> dict:
    manifest = load_manifest(instance_root / MANIFEST_FILENAME)
    root = workspace_root(instance_root, workspace_id, manifest.workspaces_root)
    if not root.is_dir():
        raise WorkspaceNotFoundError(f"Workspace not found: {workspace_id}")
    projects_dir = root / "projects"
    count = len([p for p in projects_dir.iterdir() if p.is_dir()]) if projects_dir.is_dir() else 0
    return {"workspace_id": workspace_id, "root": root, "project_count": count}


def archive_workspace(instance_root: Path, workspace_id: str) -> Path:
    manifest = load_manifest(instance_root / MANIFEST_FILENAME)
    root = workspace_root(instance_root, workspace_id, manifest.workspaces_root)
    if not root.is_dir():
        raise WorkspaceNotFoundError(f"Workspace not found: {workspace_id}")
    meta = root / ".company" / "workspace.yaml"
    data: dict = {}
    if meta.is_file():
        with meta.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    data.setdefault("workspace", {})["status"] = "archived"
    data["workspace"]["archived_at"] = datetime.utcnow().isoformat()
    with meta.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)
    return root


def remove_workspace(instance_root: Path, workspace_id: str) -> None:
    import shutil

    manifest = load_manifest(instance_root / MANIFEST_FILENAME)
    root = workspace_root(instance_root, workspace_id, manifest.workspaces_root)
    if not root.is_dir():
        raise WorkspaceNotFoundError(f"Workspace not found: {workspace_id}")
    shutil.rmtree(root)
    remaining = [w for w in list_workspaces(instance_root) if w != workspace_id]
    update_manifest_workspaces(instance_root / MANIFEST_FILENAME, remaining)


def validate_workspace(instance_root: Path, workspace_id: str) -> list[dict]:
    from company_lifecycle.validation.checks import check_workspace_layout

    manifest = load_manifest(instance_root / MANIFEST_FILENAME)
    root = workspace_root(instance_root, workspace_id, manifest.workspaces_root)
    return check_workspace_layout(root, workspace_id)
