"""Context engine tests."""

from pathlib import Path

from orchestrator.context.engine import ContextEngine

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_context_assembly(tmp_path: Path) -> None:
    engine = ContextEngine()
    (tmp_path / "idea.md").write_text("# Idea\n\n## Problem\nTest\n", encoding="utf-8")

    ctx = engine.assemble(
        project_id="p1",
        phase_id="requirements",
        employee_id="senior-product-manager",
        employee_role="PM",
        artifact_root=str(tmp_path),
        project_metadata={"name": "Test"},
        workflow_state={"current_phase_id": "requirements"},
        required_inputs=["idea.md"],
        deliverable="requirements.md",
        execution_history=[],
    )

    assert "idea.md" in ctx.artifacts
    assert ctx.project_metadata["name"] == "Test"


def test_context_compression() -> None:
    engine = ContextEngine()
    from orchestrator.types import AssembledContext

    ctx = AssembledContext(
        project_id="p",
        phase_id="idea",
        employee_id="em",
        employee_role="EM",
        artifact_root=".",
        project_metadata={},
        workflow_state={},
        artifacts={"big.md": "x" * 5000},
        execution_history=[{"i": j} for j in range(50)],
        company_config={},
        mcp_evidence={},
    )
    compressed = engine.compress(ctx, 1000)
    assert len(compressed.execution_history) <= 20
