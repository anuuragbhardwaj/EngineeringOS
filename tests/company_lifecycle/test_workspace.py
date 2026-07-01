"""Workspace lifecycle tests."""

from pathlib import Path

from company_lifecycle.factory import create_lifecycle_platform
from company_lifecycle.types import CompanyCreateRequest


def test_workspace_create_and_list(tmp_path: Path) -> None:
    platform = create_lifecycle_platform()
    company = tmp_path / "co"
    platform.init_company(
        CompanyCreateRequest(name="Co", target=company, instance_id="co", create_default_workspace=False)
    )
    platform.create_workspace("dev", company)
    workspaces = platform.list_workspaces(company)
    assert any(w.workspace_id == "dev" for w in workspaces)
    assert (company / "workspaces" / "dev" / "projects").is_dir()
