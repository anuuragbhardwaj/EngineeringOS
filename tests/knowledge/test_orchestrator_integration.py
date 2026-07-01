"""Orchestrator knowledge integration tests."""

from pathlib import Path

from orchestrator.context.engine import ContextEngine
from orchestrator.prompt_builder.builder import PromptBuilder
from orchestrator.types import AssembledContext
from knowledge.factory import create_knowledge_platform


def test_prompt_includes_knowledge_snippets() -> None:
    context = AssembledContext(
        project_id="p1",
        phase_id="implementation",
        employee_id="developer",
        employee_role="Developer",
        artifact_root=".",
        project_metadata={"name": "Test"},
        workflow_state={},
        artifacts={},
        execution_history=[],
        company_config={},
        mcp_evidence={},
        deliverable="source_and_tests",
        knowledge_snippets={
            "fact:kn-1": "[fact] Use pytest\nAlways write tests.\n(relevance: 0.9)"
        },
    )
    prompt = PromptBuilder().build(context, None, "Build the feature")
    assert "Relevant Engineering Knowledge" in prompt
    assert "Use pytest" in prompt


def test_context_engine_passes_knowledge() -> None:
    engine = ContextEngine()
    assembled = engine.assemble(
        project_id="p1",
        phase_id="idea",
        employee_id="em",
        employee_role="EM",
        artifact_root=".",
        project_metadata={},
        workflow_state={},
        required_inputs=[],
        deliverable="idea.md",
        execution_history=[],
        knowledge_snippets={"lesson:1": "Prior lesson learned"},
    )
    assert assembled.knowledge_snippets["lesson:1"] == "Prior lesson learned"


def test_retrieve_for_prompt_with_company(tmp_path: Path) -> None:
    (tmp_path / "company.yaml").write_text(
        "company:\n  instance_id: co\n  instance_version: '1.0.0'\n"
        "  schema_version: '1.0.0'\n  framework:\n    version: '2.0.0'\n"
        "  configuration:\n    workspaces_root: workspaces/\n    default_workspace: default\n",
        encoding="utf-8",
    )
    platform = create_knowledge_platform()
    platform.capture(
        tmp_path,
        title="Project convention",
        content="Follow SDLC workflow.",
        origin="em",
        owner="em",
        reason="workflow",
        project_id="eos",
        confidence=0.9,
        auto_activate=True,
    )
    snippets = platform.retrieve_for_prompt(tmp_path, project_id="eos")
    assert snippets
    assert any("SDLC" in s for s in snippets.values())
