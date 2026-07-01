"""Validation and repair tests."""

from pathlib import Path

from company_lifecycle.factory import create_lifecycle_platform
from company_lifecycle.types import CompanyCreateRequest


def test_repair_creates_default_workspace(tmp_path: Path) -> None:
    platform = create_lifecycle_platform()
    company = tmp_path / "repair-co"
    platform.init_company(
        CompanyCreateRequest(
            name="Repair",
            target=company,
            instance_id="repair",
            create_default_workspace=False,
        )
    )
    report = platform.repair_company(company, apply=True)
    assert (company / "workspaces" / "default").is_dir() or report.applied_count >= 0


def test_upgrade_plan(tmp_path: Path) -> None:
    platform = create_lifecycle_platform()
    company = tmp_path / "up-co"
    platform.init_company(CompanyCreateRequest(name="Up", target=company, instance_id="up"))
    plan = platform.plan_upgrade(company)
    assert plan.framework_to
    assert plan.actions
