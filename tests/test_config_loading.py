"""Configuration loading tests."""

from pathlib import Path

import yaml

from company_core.config.loader import (
    discover_framework_root_from_path,
    load_manifest,
    manifest_template,
    parse_manifest,
    validate_manifest_structure,
    write_manifest,
)


def test_manifest_template_structure() -> None:
    data = manifest_template("test-co")
    assert data["company"]["instance_id"] == "test-co"
    assert data["company"]["framework"]["version"] == "2.0.0"


def test_write_and_load_manifest(tmp_path: Path) -> None:
    write_manifest(tmp_path, instance_id="demo")
    manifest = load_manifest(tmp_path / "company.yaml")
    assert manifest.instance_id == "demo"
    assert manifest.framework_version == "2.0.0"


def test_validate_manifest_structure_valid() -> None:
    data = manifest_template()
    manifest = parse_manifest(data, Path("company.yaml"))
    errors = validate_manifest_structure(manifest)
    assert errors == []


def test_validate_manifest_structure_missing_instance_id() -> None:
    data = manifest_template()
    data["company"]["instance_id"] = ""
    manifest = parse_manifest(data, Path("company.yaml"))
    errors = validate_manifest_structure(manifest)
    assert any(e.field == "instance_id" for e in errors)


def test_repo_company_yaml_loads() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    manifest_path = repo_root / "company.yaml"
    if not manifest_path.is_file():
        return
    manifest = load_manifest(manifest_path)
    assert manifest.instance_id == "ai-company-dev"
    content = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert content["company"]["framework"]["version"] == "2.0.0"


def test_discover_framework_root_from_path_repo() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    root = discover_framework_root_from_path(repo_root)
    assert root is not None
    assert (root / "workflow.yaml").is_file()
