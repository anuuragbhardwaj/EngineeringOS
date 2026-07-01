"""Orchestrator factory."""

from __future__ import annotations

from pathlib import Path

from orchestrator.orchestrator import Orchestrator
from orchestrator.types import IAgentAdapter


def create_orchestrator(
    adapter: IAgentAdapter,
    agent_registry: object,
    framework_root: Path | None = None,
    policies_path: Path | None = None,
    instance_root: Path | None = None,
) -> Orchestrator:
    root = framework_root or _discover_framework_root()
    policies = policies_path or (Path(__file__).resolve().parents[2] / "policies.yaml")
    knowledge_provider = _make_knowledge_provider(instance_root) if instance_root else None
    parallel_platform = _make_parallel_platform() if instance_root else None
    return Orchestrator(
        adapter,
        agent_registry,
        root,
        policies,
        knowledge_provider=knowledge_provider,
        parallel_platform=parallel_platform,
        instance_root=str(instance_root) if instance_root else None,
    )


def _make_parallel_platform():
    from parallel_execution.factory import create_parallel_execution_platform

    return create_parallel_execution_platform()


def _make_knowledge_provider(instance_root: Path):
    def provider(context: dict) -> dict[str, str]:
        from knowledge.factory import create_knowledge_platform

        platform = create_knowledge_platform()
        return platform.retrieve_for_prompt(
            instance_root,
            project_id=context.get("project_id"),
            employee_id=context.get("employee_id"),
            phase_id=context.get("phase_id"),
            artifacts=[context.get("deliverable", "")] + list(context.get("required_inputs") or []),
        )

    return provider


def _discover_framework_root() -> Path:
    from company_core.config.loader import discover_framework_root_from_path

    root = discover_framework_root_from_path()
    if root is not None:
        return root
    return Path(__file__).resolve().parents[4]
