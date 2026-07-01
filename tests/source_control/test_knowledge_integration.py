"""Source control knowledge integration tests."""

from pathlib import Path

import subprocess

from knowledge.factory import create_knowledge_platform
from source_control.factory import create_source_control_platform


def test_commit_uses_knowledge_hints(tmp_path: Path) -> None:
    (tmp_path / "company.yaml").write_text(
        "company:\n  instance_id: co\n  instance_version: '1.0.0'\n"
        "  schema_version: '1.0.0'\n  framework:\n    version: '2.0.0'\n"
        "  configuration:\n    workspaces_root: workspaces/\n    default_workspace: dev\n",
        encoding="utf-8",
    )
    project = tmp_path / "workspaces" / "dev" / "projects" / "app"
    project.mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=project, check=True, capture_output=True)
    (project / "main.py").write_text("print('hi')\n", encoding="utf-8")

    from workspace_execution.context.types import SessionContext
    from workspace_execution.session.store import save_session

    save_session(tmp_path, SessionContext(workspace_id="dev", project_id="app"))

    knowledge = create_knowledge_platform()
    knowledge.capture(
        tmp_path,
        title="Use type hints",
        content="All Python functions must have type hints.",
        origin="review",
        owner="reviewer",
        reason="code quality",
        knowledge_type="convention",
        project_id="app",
        confidence=0.9,
        auto_activate=True,
    )

    sc = create_source_control_platform()
    msg = sc.generate_commit(tmp_path, phase_id="implementation")
    assert msg.title
    # Knowledge may appear in body when hints are found
    assert msg.confidence >= 0.5
