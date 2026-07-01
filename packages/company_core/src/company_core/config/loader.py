"""Configuration loading and instance discovery."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from company_core.models.errors import ManifestNotFoundError
from company_core.models.manifest import CompanyManifest, ValidationError

MANIFEST_FILENAME = "company.yaml"
REQUIRED_TOP_LEVEL = ("company",)


def discover_instance_root(start: Path | None = None) -> Path | None:
    """Walk upward from start (or cwd) to find company.yaml."""
    current = (start or Path.cwd()).resolve()
    for directory in [current, *current.parents]:
        if (directory / MANIFEST_FILENAME).is_file():
            return directory
    return None


def discover_framework_root(instance_root: Path | None = None) -> Path | None:
    """Resolve framework install path from manifest or heuristics."""
    if instance_root:
        manifest_path = instance_root / MANIFEST_FILENAME
        if manifest_path.is_file():
            data = _load_yaml(manifest_path)
            install = (
                data.get("company", {})
                .get("framework", {})
                .get("install_path")
            )
            if install:
                path = Path(install).expanduser().resolve()
                if path.is_dir():
                    return path

    # Heuristic: ai-company repo layout (mcp/ + handbook/ at root)
    for candidate in _framework_candidates(instance_root):
        if (candidate / "mcp" / "registry.yaml").is_file() and (
            candidate / "handbook"
        ).is_dir():
            return candidate
    return None


def _framework_candidates(instance_root: Path | None) -> list[Path]:
    candidates: list[Path] = []
    if instance_root:
        candidates.append(instance_root)
    package_root = Path(__file__).resolve().parents[5]
    candidates.append(package_root)
    cwd = Path.cwd().resolve()
    if cwd not in candidates:
        candidates.append(cwd)
    return candidates


def load_manifest(path: Path | None = None) -> CompanyManifest:
    """Load company.yaml from path or discover from cwd."""
    if path is None:
        root = discover_instance_root()
        if root is None:
            raise ManifestNotFoundError(
                f"{MANIFEST_FILENAME} not found in current directory or parents"
            )
        path = root / MANIFEST_FILENAME
    else:
        path = path.resolve()
        if not path.is_file():
            raise ManifestNotFoundError(f"Manifest not found: {path}")

    data = _load_yaml(path)
    return parse_manifest(data, path)


def parse_manifest(data: dict[str, Any], path: Path) -> CompanyManifest:
    company = data.get("company", {})
    framework = company.get("framework", {})
    configuration = company.get("configuration", {})
    install_raw = framework.get("install_path")
    install_path = Path(install_raw).expanduser() if install_raw else None

    return CompanyManifest(
        instance_id=str(company.get("instance_id", "default")),
        instance_version=str(company.get("instance_version", "1.0.0")),
        schema_version=str(company.get("schema_version", "1.0.0")),
        framework_version=str(framework.get("version", "2.0.0")),
        install_path=install_path,
        workspaces_root=str(configuration.get("workspaces_root", "workspaces/")),
        default_workspace=str(configuration.get("default_workspace", "default")),
        raw=data,
        path=path,
    )


def validate_manifest_structure(manifest: CompanyManifest) -> list[ValidationError]:
    errors: list[ValidationError] = []
    company = manifest.raw.get("company")
    if not isinstance(company, dict):
        errors.append(ValidationError("company", "Missing or invalid 'company' section"))
        return errors

    if not company.get("instance_id"):
        errors.append(ValidationError("instance_id", "instance_id is required"))

    framework = company.get("framework")
    if not isinstance(framework, dict) or not framework.get("version"):
        errors.append(ValidationError("framework.version", "framework.version is required"))

    return errors


def manifest_template(instance_id: str = "default") -> dict[str, Any]:
    """Default company.yaml content per company-instance-model.md."""
    return {
        "company": {
            "instance_id": instance_id,
            "instance_version": "1.0.0",
            "schema_version": "1.0.0",
            "framework": {
                "version": "2.0.0",
                "install_path": None,
            },
            "employees": {"directory": "employees/"},
            "policies": {"handbook": "handbook/"},
            "templates": {"directory": "templates/", "version": "2.0.0"},
            "standards": {"workflow": "workflow.yaml"},
            "manifest": MANIFEST_FILENAME,
            "mcp_profiles": {"default": "mcp.json"},
            "configuration": {
                "workspaces_root": "workspaces/",
                "default_workspace": "default",
            },
            "workspaces": [],
        }
    }


def write_manifest(target: Path, instance_id: str = "default") -> Path:
    """Write company.yaml template to target directory."""
    target = target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    manifest_path = target / MANIFEST_FILENAME
    content = manifest_template(instance_id)
    with manifest_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(content, handle, sort_keys=False, default_flow_style=False)
    return manifest_path


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    if not isinstance(loaded, dict):
        raise ManifestNotFoundError(f"Invalid manifest format: {path}")
    return loaded
