"""Prompt builder tests."""

from pathlib import Path

from orchestrator.context.engine import ContextEngine
from orchestrator.prompt_builder.builder import PromptBuilder

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_prompt_build_deterministic(tmp_path: Path) -> None:
    engine = ContextEngine()
    builder = PromptBuilder(REPO_ROOT)

    ctx = engine.assemble(
        project_id="prompt-test",
        phase_id="requirements",
        employee_id="senior-product-manager",
        employee_role="Senior Product Manager",
        artifact_root=str(tmp_path),
        project_metadata={"name": "Prompt Test", "description": "Desc"},
        workflow_state={"current_phase_id": "requirements"},
        required_inputs=[],
        deliverable="requirements.md",
        execution_history=[],
    )

    p1 = builder.build(ctx, None, "Generate requirements")
    p2 = builder.build(ctx, None, "Generate requirements")
    assert p1 == p2
    assert "requirements.md" in p1
    assert "Prompt Test" in p1
