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
) -> Orchestrator:
    root = framework_root or _discover_framework_root()
    policies = policies_path or (Path(__file__).resolve().parents[2] / "policies.yaml")
    return Orchestrator(adapter, agent_registry, root, policies)


def _discover_framework_root() -> Path:
    current = Path.cwd().resolve()
    for directory in [current, *current.parents]:
        if (directory / "workflow.yaml").is_file():
            return directory
    return Path(__file__).resolve().parents[4]
