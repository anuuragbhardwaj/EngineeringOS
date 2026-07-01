"""Fallback and placeholder provider tests."""

import pytest

from ai_execution.errors import ProviderPlaceholderError
from ai_execution.factory import create_platform
from ai_execution.types import ExecutionContext, ExecutionRequest

REPO_ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]


def test_placeholder_provider_raises() -> None:
    platform = create_platform(REPO_ROOT)
    openai = platform._registry.get("openai")  # noqa: SLF001
    assert openai is not None
    request = ExecutionRequest(
        request_id="r1",
        context=ExecutionContext(
            project_id="p",
            phase_id="idea",
            employee_id="em",
            employee_role="EM",
            artifact_root=".",
            deliverable="idea.md",
            delegation_brief="",
            project_metadata={},
            workflow_state={},
            required_inputs=[],
            artifact_paths=[],
            employee_prompt_path=None,
            employee_prompt=None,
            mcp_evidence={},
            execution_history=[],
            company_config={},
            capabilities_required=["reasoning"],
        ),
        conversation_id="c1",
        session_id="s1",
        capabilities=["reasoning"],
    )
    with pytest.raises(ProviderPlaceholderError):
        openai.execute(request)


def test_fallback_to_scaffold_when_cursor_unavailable(tmp_path) -> None:
    from ai_execution.capabilities import CapabilityResolver
    from ai_execution.conversation.manager import ConversationManager
    from ai_execution.providers.scaffold import ScaffoldProvider
    from ai_execution.registry.provider_registry import ProviderRegistry

    registry = ProviderRegistry()
    registry.load_config(REPO_ROOT / "packages" / "ai_execution" / "providers.yaml")
    registry.register(ScaffoldProvider())
    resolver = CapabilityResolver(registry)
    provider = resolver.select_provider(["planning"])
    assert provider.provider_id == "scaffold"
