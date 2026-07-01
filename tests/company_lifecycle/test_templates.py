"""Template engine tests."""

from pathlib import Path

from company_lifecycle.templates.engine import apply_template, list_profiles


def test_list_profiles() -> None:
    profiles = list_profiles()
    assert "production" in profiles
    assert "prototype" in profiles
    assert "fullstack" in profiles


def test_apply_template(tmp_path: Path) -> None:
    written = apply_template(
        tmp_path / "proj",
        "production",
        variables={
            "project_name": "Demo",
            "description": "Test",
            "platform": "web",
            "technology_stack": "Python",
            "mode": "production",
            "template_profile": "production",
        },
    )
    assert written
    assert (tmp_path / "proj" / ".company-project.yaml").is_file()
