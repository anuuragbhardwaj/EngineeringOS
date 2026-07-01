"""Versioned template application engine."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from company_lifecycle.errors import TemplateNotFoundError

_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
_TEMPLATES_ROOT = _PACKAGE_ROOT / "templates_catalog"
_CATALOG_PATH = _TEMPLATES_ROOT / "catalog.yaml"


def load_catalog() -> dict[str, Any]:
    with _CATALOG_PATH.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def list_profiles() -> list[str]:
    return sorted((load_catalog().get("profiles") or {}).keys())


def resolve_profile_files(profile_id: str) -> list[str]:
    catalog = load_catalog()
    profiles = catalog.get("profiles") or {}
    if profile_id not in profiles:
        raise TemplateNotFoundError(f"Unknown template profile: {profile_id}")

    seen: set[str] = set()
    ordered: list[str] = []

    def collect(pid: str) -> None:
        if pid in seen:
            return
        seen.add(pid)
        profile = profiles.get(pid)
        if not profile:
            return
        parent = profile.get("extends")
        if parent:
            collect(str(parent))
        for rel in profile.get("files") or []:
            if rel not in ordered:
                ordered.append(str(rel))

    collect(profile_id)
    return ordered


def apply_template(
    target: Path,
    profile_id: str,
    *,
    variables: dict[str, str],
) -> list[Path]:
    """Apply template files to target — never copies framework packages."""
    target.mkdir(parents=True, exist_ok=True)
    files = resolve_profile_files(profile_id)
    written: list[Path] = []

    for rel in files:
        source = _find_template_source(profile_id, rel)
        if source is None:
            source = _find_template_source("production", rel)
        if source is None:
            continue
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        content = source.read_text(encoding="utf-8")
        content = _render(content, variables)
        if not dest.exists():
            dest.write_text(content, encoding="utf-8")
            written.append(dest)

    project_meta = target / ".company-project.yaml"
    if not project_meta.exists():
        meta = {
            "project": {
                "name": variables.get("project_name", "project"),
                "template_profile": profile_id,
                "template_version": (load_catalog().get("profiles") or {})
                .get(profile_id, {})
                .get("version", "1.0.0"),
            }
        }
        with project_meta.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(meta, handle, sort_keys=False, default_flow_style=False)
        written.append(project_meta)

    return written


def _find_template_source(profile_id: str, rel: str) -> Path | None:
    catalog = load_catalog()
    profiles = catalog.get("profiles") or {}
    profile = profiles.get(profile_id) or {}
    chain = [profile_id]
    parent = profile.get("extends")
    if parent:
        chain.append(str(parent))
    chain.append("production")
    for pid in chain:
        candidate = _TEMPLATES_ROOT / "profiles" / pid / rel
        if candidate.is_file():
            return candidate
    return None


def _render(content: str, variables: dict[str, str]) -> str:
    def replacer(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        return variables.get(key, match.group(0))

    return re.sub(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}", replacer, content)
