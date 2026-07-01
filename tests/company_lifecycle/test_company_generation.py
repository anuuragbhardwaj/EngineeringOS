"""Company generation tests."""

from pathlib import Path

from company_lifecycle.factory import create_lifecycle_platform
from company_lifecycle.filesystem.boundaries import FRAMEWORK_OWNED
from company_lifecycle.types import CompanyCreateRequest


def test_generated_company_has_no_framework_assets(tmp_path: Path) -> None:
    platform = create_lifecycle_platform()
    request = CompanyCreateRequest(
        name="Acme",
        target=tmp_path / "acme-co",
        instance_id="acme",
        init_git=False,
    )
    platform.init_company(request)
    root = tmp_path / "acme-co"
    assert (root / "company.yaml").is_file()
    assert (root / "README.md").is_file()
    assert (root / "workspaces").is_dir()
    for forbidden in FRAMEWORK_OWNED:
        if forbidden in {"packages", "runtime", "workflow.yaml"}:
            assert not (root / forbidden).exists()


def test_framework_reference_in_manifest(tmp_path: Path) -> None:
    platform = create_lifecycle_platform()
    request = CompanyCreateRequest(
        name="Ref Co",
        target=tmp_path / "ref-co",
        instance_id="ref-co",
    )
    platform.init_company(request)
    text = (tmp_path / "ref-co" / "company.yaml").read_text(encoding="utf-8")
    assert "install_path" in text
    assert "packages" not in text or "directory: null" in text.replace(" ", "")
