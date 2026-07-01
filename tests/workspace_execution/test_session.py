"""Session persistence tests."""

from pathlib import Path

from workspace_execution.resolver.resolver import ContextResolver
from workspace_execution.session.store import load_session, save_session
from workspace_execution.context.types import SessionContext


def test_session_persists_across_reload(tmp_path: Path) -> None:
    (tmp_path / "company.yaml").write_text(
        "company:\n  instance_id: test-co\n  instance_version: '1.0.0'\n"
        "  schema_version: '1.0.0'\n  framework:\n    version: '2.0.0'\n"
        "  configuration:\n    workspaces_root: workspaces/\n    default_workspace: default\n",
        encoding="utf-8",
    )
    session = SessionContext(company_id="test-co", workspace_id="dev", project_id="app")
    save_session(tmp_path, session)
    loaded = load_session(tmp_path)
    assert loaded.workspace_id == "dev"
    assert loaded.project_id == "app"


def test_context_resolver_workspace_project(tmp_path: Path) -> None:
    (tmp_path / "company.yaml").write_text(
        "company:\n  instance_id: test-co\n  instance_version: '1.0.0'\n"
        "  schema_version: '1.0.0'\n  framework:\n    version: '2.0.0'\n"
        "  configuration:\n    workspaces_root: workspaces/\n    default_workspace: default\n",
        encoding="utf-8",
    )
    (tmp_path / "workspaces" / "default" / "projects" / "my-app").mkdir(parents=True)
    resolver = ContextResolver()
    resolver.set_workspace("default", tmp_path)
    ctx = resolver.set_project("my-app", tmp_path)
    assert ctx.session.project_id == "my-app"
    assert ctx.session.workspace_id == "default"
