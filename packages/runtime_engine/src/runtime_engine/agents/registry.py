"""Configuration-driven agent registry."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from runtime_engine.errors import PhaseNotFoundError
from runtime_engine.types import AgentDescriptor, WorkflowDefinition


class AgentRegistry:
    """IAgentRegistry — resolves employees from workflow + employee-registry.yaml."""

    def __init__(self, registry_path: str | Path) -> None:
        self._registry_path = Path(registry_path)
        self._config = self._load_registry(self._registry_path)

    def _load_registry(self, path: Path) -> dict[str, Any]:
        if not path.is_file():
            return {"agents": {}, "orchestrator": "engineering-manager"}
        with path.open(encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def resolve(
        self,
        phase_id: str,
        workflow: WorkflowDefinition,
    ) -> list[AgentDescriptor]:
        primary = self.resolve_primary(phase_id, workflow)
        return [primary] if primary else []

    def resolve_primary(
        self,
        phase_id: str,
        workflow: WorkflowDefinition,
    ) -> AgentDescriptor | None:
        phase = workflow.phase_by_id(phase_id)
        if phase is None:
            raise PhaseNotFoundError(phase_id)

        agent_id = phase.owner.agent
        agent_cfg = self._config.get("agents", {}).get(agent_id, {})
        framework_root = self._registry_path.parent.parent

        prompt_rel = agent_cfg.get("prompt_path", f".cursor/agents/{agent_id}.md")
        prompt_path = str((framework_root / prompt_rel).resolve())

        return AgentDescriptor(
            agent_id=agent_id,
            role=agent_cfg.get("role", phase.owner.role),
            phase_id=phase_id,
            primary_artifact=phase.primary_artifact,
            parallel=False,
            contributors=[c.agent for c in phase.contributors],
            prompt_path=prompt_path if Path(prompt_path).is_file() else prompt_rel,
            expected_inputs=list(phase.required_inputs),
            expected_outputs=list(phase.required_outputs) or [phase.primary_artifact],
        )

    def resolve_orchestrator(self, workflow: WorkflowDefinition) -> AgentDescriptor:
        orchestrator_id = (
            self._config.get("orchestrator")
            or workflow.defaults.orchestrator_agent
        )
        idea_phase = workflow.phase_by_id("idea")
        phase_id = idea_phase.id if idea_phase else workflow.ordered_phases()[0].id
        agent_cfg = self._config.get("agents", {}).get(orchestrator_id, {})
        framework_root = self._registry_path.parent.parent
        prompt_rel = agent_cfg.get("prompt_path", f".cursor/agents/{orchestrator_id}.md")
        prompt_path = str((framework_root / prompt_rel).resolve())

        return AgentDescriptor(
            agent_id=orchestrator_id,
            role=agent_cfg.get("role", "Engineering Manager"),
            phase_id=phase_id,
            primary_artifact="pipeline-status.md",
            prompt_path=prompt_path if Path(prompt_path).is_file() else prompt_rel,
            expected_outputs=["pipeline-status.md"],
        )

    def is_orchestrator(self, agent_id: str) -> bool:
        orchestrator = self._config.get("orchestrator", "engineering-manager")
        agent_cfg = self._config.get("agents", {}).get(agent_id, {})
        return agent_id == orchestrator or bool(agent_cfg.get("orchestrator"))
