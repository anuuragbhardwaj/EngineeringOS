"""Configuration package."""

from company_core.config.loader import (
    MANIFEST_FILENAME,
    discover_framework_root,
    discover_framework_root_from_path,
    discover_instance_root,
    load_manifest,
    manifest_template,
    parse_manifest,
    validate_manifest_structure,
    write_manifest,
)

__all__ = [
    "MANIFEST_FILENAME",
    "discover_framework_root",
    "discover_framework_root_from_path",
    "discover_instance_root",
    "load_manifest",
    "manifest_template",
    "parse_manifest",
    "validate_manifest_structure",
    "write_manifest",
]
