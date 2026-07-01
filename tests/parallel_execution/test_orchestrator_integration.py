"""Orchestrator parallel integration tests."""

from pathlib import Path

from parallel_execution.factory import create_parallel_execution_platform


def test_parallel_platform_resolves_specialists() -> None:
    from runtime_engine.agents.registry import AgentRegistry
    from runtime_engine.workflow.loader import WorkflowLoader

    framework = Path(__file__).resolve().parents[2]
    registry = AgentRegistry(framework / "runtime" / "employee-registry.yaml")
    workflow = WorkflowLoader().load(str(framework / "workflow.yaml"))
    platform = create_parallel_execution_platform()
    specialists = platform.resolve_specialists(registry, "implementation", workflow)
    assert "senior-backend-engineer" in specialists
    assert "senior-frontend-engineer" in specialists


def test_parallel_policy_implementation() -> None:
    from orchestrator.policy.engine import PolicyEngine

    engine = PolicyEngine(Path(__file__).resolve().parents[2] / "packages" / "orchestrator" / "policies.yaml")
    policy = engine.resolve("implementation", "G5")
    assert policy.sequential is False
    assert policy.name == "parallel_ready"
