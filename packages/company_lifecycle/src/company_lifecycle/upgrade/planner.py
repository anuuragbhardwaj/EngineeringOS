"""Upgrade and migration planning."""

from __future__ import annotations

from pathlib import Path

import yaml

from company_core.config.loader import MANIFEST_FILENAME, load_manifest
from company_lifecycle.installation.detector import framework_version
from company_lifecycle.types import MigrationPlan, UpgradePlan


def plan_upgrade(instance_root: Path, target_version: str | None = None) -> UpgradePlan:
    """Generate upgrade plan — preserves user modifications."""
    instance_root = instance_root.resolve()
    manifest = load_manifest(instance_root / MANIFEST_FILENAME)
    fw_to = target_version or framework_version()
    fw_from = manifest.framework_version
    company_from = manifest.instance_version
    company_to = _bump_patch(company_from)

    actions = [
        "Compare framework version pin in company.yaml",
        "Run engineeringos doctor",
        "Run engineeringos validate",
        "Review docs/audit/release-readiness.md for breaking changes",
    ]
    if manifest.install_path and not manifest.install_path.is_dir():
        actions.insert(0, "Update framework.install_path to installed EngineeringOS location")

    warnings = [
        "User-owned files are never overwritten automatically",
        "Template profiles may be re-applied manually after upgrade",
    ]
    return UpgradePlan(
        framework_from=fw_from,
        framework_to=fw_to,
        company_from=company_from,
        company_to=company_to,
        actions=actions,
        warnings=warnings,
    )


def plan_migration(instance_root: Path, *, dry_run: bool = True) -> MigrationPlan:
    """Generate schema migration plan."""
    manifest = load_manifest(instance_root / MANIFEST_FILENAME)
    from_ver = manifest.schema_version
    to_ver = "1.0.0"
    steps = [
        "Backup company.yaml",
        "Validate manifest schema",
        "Migrate workspace registry entries if schema changed",
        "Migrate .company/session.yaml if present",
        "Run engineeringos doctor",
    ]
    if not dry_run:
        steps.append("Apply schema updates (manual review required)")
    return MigrationPlan(from_version=from_ver, to_version=to_ver, steps=steps, dry_run=dry_run)


def apply_upgrade_manifest_pin(instance_root: Path, target_version: str | None = None) -> Path:
    """Update only framework version pin — does not overwrite user content."""
    manifest_path = instance_root / MANIFEST_FILENAME
    with manifest_path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    fw = data.setdefault("company", {}).setdefault("framework", {})
    fw["version"] = target_version or framework_version()
    company = data["company"]
    company["instance_version"] = _bump_patch(str(company.get("instance_version", "1.0.0")))
    with manifest_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, default_flow_style=False)
    return manifest_path


def _bump_patch(version: str) -> str:
    parts = version.split(".")
    if len(parts) == 3 and parts[2].isdigit():
        parts[2] = str(int(parts[2]) + 1)
        return ".".join(parts)
    return version
