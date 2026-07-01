"""Build execution dependency graphs from workflow and artifacts."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import yaml

from parallel_execution.errors import DependencyCycleError
from parallel_execution.types import DependencyGraph, GraphNode

# Known parallel phases and their independent employees
PARALLEL_PHASE_AGENTS: dict[str, list[dict[str, str]]] = {
    "implementation": [
        {"employee_id": "senior-backend-engineer", "deliverable": "source_code", "subsystem": "backend"},
        {"employee_id": "senior-frontend-engineer", "deliverable": "source_code", "subsystem": "frontend"},
        {"employee_id": "documentation-engineer", "deliverable": "implementation-notes.md", "subsystem": "docs"},
    ],
}


class DependencyGraphBuilder:
    """Build graphs from workflow, tasks, architecture, and runtime state."""

    def __init__(self, framework_root: Path | None = None) -> None:
        self._framework_root = framework_root

    def build_phase_graph(
        self,
        phase_id: str,
        *,
        workflow: Any | None = None,
        artifact_root: Path | None = None,
        runtime_state: dict | None = None,
    ) -> DependencyGraph:
        if phase_id in PARALLEL_PHASE_AGENTS:
            return self._build_parallel_phase(phase_id)

        # Default: single-node sequential graph
        employee_id = "engineering-manager"
        deliverable = phase_id
        if workflow:
            phase = workflow.phase_by_id(phase_id) if hasattr(workflow, "phase_by_id") else None
            if phase:
                employee_id = getattr(phase.owner, "agent", employee_id)
                deliverable = phase.primary_artifact

        node = GraphNode(
            node_id=f"node-{phase_id}",
            employee_id=employee_id,
            phase_id=phase_id,
            deliverable=deliverable,
        )
        return DependencyGraph(nodes=[node], phase_id=phase_id, parallel_groups=[])

    def build_pipeline_graph(self, workflow: Any) -> list[DependencyGraph]:
        graphs: list[DependencyGraph] = []
        if not hasattr(workflow, "ordered_phases"):
            return graphs
        for phase in workflow.ordered_phases():
            graphs.append(self.build_phase_graph(phase.id, workflow=workflow))
        return graphs

    def from_workflow_yaml(self, workflow_path: Path, phase_id: str) -> DependencyGraph:
        if not workflow_path.is_file():
            return self.build_phase_graph(phase_id)
        with workflow_path.open(encoding="utf-8") as handle:
            raw = yaml.safe_load(handle) or {}
        phases = raw.get("phases", [])
        for item in phases:
            if item.get("id") == phase_id and item.get("parallel_allowed"):
                agents = item.get("owner", {}).get("agents", [])
                if len(agents) > 1:
                    return self._build_from_agents(phase_id, agents, item)
        return self.build_phase_graph(phase_id)

    def _build_parallel_phase(self, phase_id: str) -> DependencyGraph:
        agents = PARALLEL_PHASE_AGENTS[phase_id]
        return self._build_from_agent_specs(phase_id, agents)

    def _build_from_agents(self, phase_id: str, agents: list[str], phase_item: dict) -> DependencyGraph:
        specs = []
        outputs = phase_item.get("outputs", {}).get("required", ["source_and_tests"])
        for i, agent_id in enumerate(agents):
            deliverable = outputs[0] if len(outputs) == 1 else outputs[min(i, len(outputs) - 1)]
            specs.append({"employee_id": agent_id, "deliverable": deliverable, "subsystem": agent_id})
        return self._build_from_agent_specs(phase_id, specs)

    def _build_from_agent_specs(self, phase_id: str, specs: list[dict]) -> DependencyGraph:
        nodes: list[GraphNode] = []
        node_ids: list[str] = []
        for spec in specs:
            node_id = f"node-{spec['employee_id']}-{uuid.uuid4().hex[:6]}"
            nodes.append(
                GraphNode(
                    node_id=node_id,
                    employee_id=spec["employee_id"],
                    phase_id=phase_id,
                    deliverable=spec["deliverable"],
                    metadata={"subsystem": spec.get("subsystem", "")},
                )
            )
            node_ids.append(node_id)
        return DependencyGraph(nodes=nodes, phase_id=phase_id, parallel_groups=[node_ids])

    def validate_acyclic(self, graph: DependencyGraph) -> None:
        visited: set[str] = set()
        stack: set[str] = set()
        node_map = {n.node_id: n for n in graph.nodes}

        def visit(node_id: str) -> None:
            if node_id in stack:
                raise DependencyCycleError(f"Cycle detected at {node_id}")
            if node_id in visited:
                return
            stack.add(node_id)
            node = node_map.get(node_id)
            if node:
                for dep in node.dependencies:
                    visit(dep)
            stack.remove(node_id)
            visited.add(node_id)

        for node in graph.nodes:
            visit(node.node_id)
