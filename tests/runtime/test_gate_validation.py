"""Gate and validation tests."""

from pathlib import Path

from runtime_engine.factory import create_runtime

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_validate_fails_without_artifacts(tmp_path: Path) -> None:
    rt = create_runtime(framework_root=REPO_ROOT)
    project_dir = tmp_path / "validate-fail"
    rt.init_project("validate-fail", artifact_root=str(project_dir))
    report = rt.validate("validate-fail")
    assert report.passed is False


def test_gate_evaluation_after_artifacts(tmp_path: Path) -> None:
    rt = create_runtime(framework_root=REPO_ROOT)
    project_dir = tmp_path / "gate-pass"
    rt.init_project(
        "gate-pass",
        artifact_root=str(project_dir),
        metadata={"name": "Gate", "description": "d", "platform": "x", "mode": "production"},
    )
    rt.invoke_agent("gate-pass")
    report = rt.validate("gate-pass")
    assert report.passed is True
    evaluation = rt.evaluate_gate("gate-pass")
    assert evaluation.passed is True
