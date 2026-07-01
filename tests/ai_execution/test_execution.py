"""Execution request/response tests."""

from pathlib import Path
from types import SimpleNamespace

from ai_execution.factory import create_platform

REPO_ROOT = Path(__file__).resolve().parents[2]


def _descriptor(agent_id: str = "senior-product-manager"):
    return SimpleNamespace(
        agent_id=agent_id,
        role="Senior Product Manager",
        phase_id="requirements",
        primary_artifact="requirements.md",
        prompt_path=str(REPO_ROOT / ".cursor/agents/senior-product-manager.md"),
        expected_inputs=["idea.md"],
        expected_outputs=["requirements.md"],
    )


def _context(tmp_path: Path):
    return SimpleNamespace(
        project_id="exec-test",
        phase_id="requirements",
        artifact_root=str(tmp_path),
        deliverable="requirements.md",
        delegation_brief="Generate requirements",
        metadata={"name": "Exec Test", "description": "Test"},
        required_inputs=[SimpleNamespace(name="idea.md")],
    )


def test_execution_request_and_response(tmp_path: Path) -> None:
    platform = create_platform(REPO_ROOT)
    response = platform.execute(_descriptor(), _context(tmp_path))
    assert response.result.status.value == "completed"
    assert response.provider_id in ("cursor", "scaffold")
    assert (tmp_path / "requirements.md").is_file()
    assert "provider_id" not in str(response.result.metadata.get("provider", ""))


def test_runtime_adapter_integration(tmp_path: Path) -> None:
    from ai_execution.adapter.runtime_adapter import create_runtime_adapter

    adapter = create_runtime_adapter(REPO_ROOT)
    result = adapter.invoke(_descriptor(), _context(tmp_path))
    assert result.status.value == "completed"
    assert "provider_id" in result.metadata
    assert result.metadata["provider_id"] in ("cursor", "scaffold")
