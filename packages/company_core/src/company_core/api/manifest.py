"""ManifestAPI implementation."""

from __future__ import annotations

from pathlib import Path

from company_core.config.loader import (
    discover_instance_root,
    load_manifest,
    validate_manifest_structure,
)
from company_core.models.errors import KeyNotFoundError, ManifestNotFoundError
from company_core.models.manifest import CompanyManifest, ValidationError
from company_core.version import FRAMEWORK_VERSION

_RESOLVABLE_KEYS = {
    "employees": ("company", "employees", "directory"),
    "handbook": ("company", "policies", "handbook"),
    "templates": ("company", "templates", "directory"),
    "workflow": ("company", "standards", "workflow"),
    "workspaces_root": ("company", "configuration", "workspaces_root"),
    "mcp_profile": ("company", "mcp_profiles", "default"),
}


class ManifestAPI:
    """Load and validate company.yaml; resolve manifest paths."""

    def __init__(self, instance_root: Path | None = None) -> None:
        self._instance_root = instance_root
        self._manifest: CompanyManifest | None = None

    @property
    def instance_root(self) -> Path | None:
        return self._instance_root

    def load(self, path: Path | None = None) -> CompanyManifest:
        if path is not None:
            self._manifest = load_manifest(path)
        elif self._instance_root is not None:
            self._manifest = load_manifest(self._instance_root / "company.yaml")
        else:
            self._manifest = load_manifest()
        return self._manifest

    def try_load(self) -> CompanyManifest | None:
        try:
            return self.load()
        except ManifestNotFoundError:
            return None

    def resolve(self, key: str) -> Path:
        manifest = self._manifest or self.load()
        root = manifest.root or discover_instance_root()
        if root is None:
            raise ManifestNotFoundError("Cannot resolve paths without instance root")

        if key == "instance_root":
            return root

        path_parts = _RESOLVABLE_KEYS.get(key)
        if path_parts is None:
            raise KeyNotFoundError(f"Unknown manifest key: {key}")

        value: object = manifest.raw
        for part in path_parts:
            if not isinstance(value, dict) or part not in value:
                raise KeyNotFoundError(f"Manifest key not found: {key}")
            value = value[part]

        return (root / str(value)).resolve()

    def framework_version(self) -> str:
        manifest = self._manifest or self.try_load()
        if manifest is None:
            return FRAMEWORK_VERSION
        return manifest.framework_version

    def validate(self) -> list[ValidationError]:
        manifest = self.load()
        return validate_manifest_structure(manifest)
