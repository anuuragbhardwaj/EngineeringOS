"""Project lifecycle — scaffolding and registry."""

from __future__ import annotations

import re
import shutil
from datetime import datetime
from pathlib import Path

import yaml

from company_core.config.loader import MANIFEST_FILENAME, load_manifest
from company_lifecycle.company.context import load_session
from company_lifecycle.errors import ProjectExistsError
from company_lifecycle.templates.engine import apply_template
from company_lifecycle.types import ProjectCreateOptions
from company_lifecycle.workspace.manager import create_workspace, list_workspaces, workspace_root


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "project"


def resolve_project_path(instance_root: Path, options: ProjectCreateOptions) -> tuple[Path, str, str]:
    manifest = load_manifest(instance_root / MANIFEST_FILENAME)
    session = load_session(instance_root)
    workspace_id = options.workspace_id or session.active_workspace or manifest.default_workspace
    project_id = slugify(options.name)

    if options.location:
        return options.location.resolve(), project_id, workspace_id

    root = workspace_root(instance_root, workspace_id, manifest.workspaces_root)
    return root / "projects" / project_id, project_id, workspace_id


def scaffold_project(instance_root: Path, options: ProjectCreateOptions) -> tuple[Path, str, str]:
    location, project_id, workspace_id = resolve_project_path(instance_root, options)

    if options.location is None:
        existing = list_workspaces(instance_root)
        if workspace_id not in existing:
            create_workspace(instance_root, workspace_id)

    if location.exists() and any(location.iterdir()):
        raise ProjectExistsError(f"Project directory already exists: {location}")

    location.mkdir(parents=True, exist_ok=True)
    variables = {
        "project_name": options.name,
        "description": options.description,
        "platform": options.platform,
        "technology_stack": options.technology_stack,
        "mode": "production" if options.production else "prototype",
        "template_profile": options.template_profile,
    }
    apply_template(location, options.template_profile, variables=variables)
    _register_project(instance_root, workspace_id, project_id, location)
    return location, project_id, workspace_id


def clone_project(
    instance_root: Path,
    source: Path,
    name: str,
    workspace_id: str | None = None,
) -> Path:
    manifest = load_manifest(instance_root / MANIFEST_FILENAME)
    session = load_session(instance_root)
    ws = workspace_id or session.active_workspace or manifest.default_workspace
    project_id = slugify(name)
    dest = workspace_root(instance_root, ws, manifest.workspaces_root) / "projects" / project_id
    if dest.exists():
        raise ProjectExistsError(f"Project already exists: {project_id}")
    shutil.copytree(source, dest)
    _register_project(instance_root, ws, project_id, dest)
    return dest


def list_projects(instance_root: Path, workspace_id: str | None = None) -> list[dict]:
    manifest = load_manifest(instance_root / MANIFEST_FILENAME)
    session = load_session(instance_root)
    ws = workspace_id or session.active_workspace or manifest.default_workspace
    root = workspace_root(instance_root, ws, manifest.workspaces_root)
    projects_dir = root / "projects"
    if not projects_dir.is_dir():
        return []
    results = []
    for entry in sorted(projects_dir.iterdir()):
        if not entry.is_dir():
            continue
        meta = entry / ".company-project.yaml"
        status = "active"
        if meta.is_file():
            with meta.open(encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
            status = data.get("project", {}).get("status", "active")
        results.append(
            {
                "project_id": entry.name,
                "root": entry,
                "workspace_id": ws,
                "status": status,
            }
        )
    return results


def archive_project(instance_root: Path, project_id: str, workspace_id: str | None = None) -> Path:
    manifest = load_manifest(instance_root / MANIFEST_FILENAME)
    session = load_session(instance_root)
    ws = workspace_id or session.active_workspace or manifest.default_workspace
    root = workspace_root(instance_root, ws, manifest.workspaces_root) / "projects" / project_id
    meta = root / ".company-project.yaml"
    data: dict = {"project": {"name": project_id, "status": "archived"}}
    if meta.is_file():
        with meta.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or data
    data.setdefault("project", {})["status"] = "archived"
    data["project"]["archived_at"] = datetime.utcnow().isoformat()
    with meta.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)
    return root


def remove_project(instance_root: Path, project_id: str, workspace_id: str | None = None) -> None:
    import shutil

    manifest = load_manifest(instance_root / MANIFEST_FILENAME)
    session = load_session(instance_root)
    ws = workspace_id or session.active_workspace or manifest.default_workspace
    root = workspace_root(instance_root, ws, manifest.workspaces_root) / "projects" / project_id
    if root.is_dir():
        shutil.rmtree(root)
    _unregister_project(instance_root, ws, project_id)


def _register_project(instance_root: Path, workspace_id: str, project_id: str, path: Path) -> None:
    manifest = load_manifest(instance_root / MANIFEST_FILENAME)
    ws_root = workspace_root(instance_root, workspace_id, manifest.workspaces_root)
    meta = ws_root / ".company" / "workspace.yaml"
    if not meta.is_file():
        create_workspace(instance_root, workspace_id)
        ws_root = workspace_root(instance_root, workspace_id, manifest.workspaces_root)
        meta = ws_root / ".company" / "workspace.yaml"
    data: dict = {"workspace": {"id": workspace_id, "projects": []}}
    if meta.is_file():
        with meta.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or data
    projects = data.setdefault("workspace", {}).setdefault("projects", [])
    try:
        rel_path = str(path.relative_to(instance_root))
    except ValueError:
        rel_path = str(path)
    entry = {"id": project_id, "path": rel_path, "created_at": datetime.utcnow().isoformat()}
    if not any(p.get("id") == project_id for p in projects):
        projects.append(entry)
    with meta.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)


def _unregister_project(instance_root: Path, workspace_id: str, project_id: str) -> None:
    manifest = load_manifest(instance_root / MANIFEST_FILENAME)
    ws_root = workspace_root(instance_root, workspace_id, manifest.workspaces_root)
    meta = ws_root / ".company" / "workspace.yaml"
    if not meta.is_file():
        return
    with meta.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    projects = data.get("workspace", {}).get("projects") or []
    data.setdefault("workspace", {})["projects"] = [p for p in projects if p.get("id") != project_id]
    with meta.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)
