"""Workflow loader — reads workflow.yaml exclusively."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from runtime_engine.errors import WorkflowNotFoundError, WorkflowParseError, WorkflowSchemaError
from runtime_engine.types import (
    AgentAssignment,
    ArtifactManifest,
    ArtifactRef,
    GateDefinition,
    PhaseDefinition,
    RejectionPath,
    ReworkTarget,
    ValidationError,
    ValidationSeverity,
    WorkflowDefaults,
    WorkflowDefinition,
)


class WorkflowLoader:
    """IWorkflowLoader implementation."""

    def __init__(self) -> None:
        self._cached_path: str | None = None
        self._cached: WorkflowDefinition | None = None

    def load(self, path: str) -> WorkflowDefinition:
        workflow_path = Path(path)
        if not workflow_path.is_file():
            raise WorkflowNotFoundError(f"Workflow not found: {path}")

        try:
            with workflow_path.open(encoding="utf-8") as handle:
                raw = yaml.safe_load(handle)
        except yaml.YAMLError as exc:
            raise WorkflowParseError(str(exc)) from exc

        if not isinstance(raw, dict):
            raise WorkflowParseError("workflow.yaml root must be a mapping")

        definition = self._parse(raw, str(workflow_path.resolve()))
        errors = self._validate_definition(definition)
        if errors:
            raise WorkflowSchemaError(
                "; ".join(f"{e.code}: {e.message}" for e in errors)
            )

        self._cached_path = str(workflow_path.resolve())
        self._cached = definition
        return definition

    def reload(self) -> WorkflowDefinition:
        if self._cached_path is None:
            raise WorkflowNotFoundError("No workflow loaded yet")
        return self.load(self._cached_path)

    def validate_schema(self, path: str) -> list[ValidationError]:
        try:
            definition = self.load(path)
        except KernelError as exc:
            return [
                ValidationError(
                    code="workflow",
                    message=str(exc),
                    severity=ValidationSeverity.ERROR,
                )
            ]
        return self._validate_definition(definition)

    def _parse(self, raw: dict[str, Any], path: str) -> WorkflowDefinition:
        defaults_raw = raw.get("defaults", {})
        orchestrator = defaults_raw.get("orchestrator", {})
        escalation = defaults_raw.get("escalation", {})

        defaults = WorkflowDefaults(
            artifact_root=str(defaults_raw.get("artifact_root", ".")),
            max_gate_failures=int(escalation.get("max_gate_failures", 3)),
            orchestrator_agent=str(orchestrator.get("agent", "engineering-manager")),
        )

        phases = [self._parse_phase(item) for item in raw.get("phases", [])]

        rework_raw = raw.get("rework_routing", {})
        rework: dict[str, ReworkTarget] = {}
        for symptom, target in rework_raw.items():
            if isinstance(target, dict):
                rework[symptom] = ReworkTarget(
                    route_to=str(target.get("phase", target.get("route_to", ""))),
                    action=str(target.get("action", "")),
                    owner=str(target.get("owner", "")) if target.get("owner") else None,
                )

        artifacts_raw = raw.get("artifacts", {})
        orch = artifacts_raw.get("orchestration", {})
        orchestration = ArtifactRef(
            name="pipeline-status.md",
            path=str(orch.get("path", "pipeline-status.md")),
            owner_agent=str(orch.get("owner", defaults.orchestrator_agent)),
            required=bool(orch.get("required", True)),
        )
        phase_artifacts: dict[str, list[str]] = {}
        for artifact_name in artifacts_raw.get("phases", []):
            if artifact_name == "source_and_tests":
                continue
            for phase in phases:
                if phase.primary_artifact == artifact_name:
                    phase_artifacts.setdefault(phase.id, []).append(artifact_name)

        return WorkflowDefinition(
            version=str(raw.get("version", "0.0.0")),
            name=str(raw.get("name", "workflow")),
            phases=phases,
            rework_routing=rework,
            defaults=defaults,
            artifacts=ArtifactManifest(
                orchestration=orchestration,
                phases=phase_artifacts,
            ),
        )

    def _parse_phase(self, item: dict[str, Any]) -> PhaseDefinition:
        owner_raw = item.get("owner", {})
        if isinstance(owner_raw.get("agents"), list):
            agents = owner_raw["agents"]
            owner = AgentAssignment(agent=str(agents[0]), role=str(owner_raw.get("role", "")))
        else:
            owner = AgentAssignment(
                agent=str(owner_raw.get("agent", "")),
                role=str(owner_raw.get("role", "")),
            )

        contributors: list[AgentAssignment] = []
        for contrib in item.get("contributors", []):
            if isinstance(contrib, str):
                contributors.append(AgentAssignment(agent=contrib, role=contrib))
            elif isinstance(contrib, dict):
                contributors.append(
                    AgentAssignment(
                        agent=str(contrib.get("agent", "")),
                        role=str(contrib.get("role", "")),
                    )
                )

        gate_raw = item.get("gate", {})
        gate = GateDefinition(
            id=str(gate_raw.get("id", "")),
            name=str(gate_raw.get("name", "")),
            approver=str(gate_raw.get("approver", "")),
            facilitator=str(gate_raw.get("facilitator", "")),
            pass_when=str(gate_raw.get("pass_when", "")),
        )

        rejection_paths = [
            RejectionPath(
                condition=str(rp.get("condition", "")),
                route_to=str(rp.get("route_to", "")),
                action=str(rp.get("action", "")),
            )
            for rp in item.get("rejection_paths", [])
        ]

        inputs = item.get("inputs", {})
        outputs = item.get("outputs", {})
        mcp_raw = item.get("mcp_evidence", {})

        return PhaseDefinition(
            id=str(item.get("id", "")),
            order=int(item.get("order", 0)),
            name=str(item.get("name", "")),
            owner=owner,
            contributors=contributors,
            primary_artifact=str(item.get("primary_artifact", "")),
            entry_criteria=[str(c) for c in item.get("entry_criteria", [])],
            exit_criteria=[str(c) for c in item.get("exit_criteria", [])],
            gate=gate,
            rejection_paths=rejection_paths,
            next=item.get("next"),
            skippable=bool(item.get("skippable", False)),
            mcp_requirements=[
                str(c) for c in mcp_raw.get("capabilities", [])
            ],
            required_inputs=[str(i) for i in inputs.get("required", [])],
            required_outputs=[str(o) for o in outputs.get("required", [])],
        )

    def _validate_definition(self, definition: WorkflowDefinition) -> list[ValidationError]:
        errors: list[ValidationError] = []
        ids = [p.id for p in definition.phases]
        if len(ids) != len(set(ids)):
            errors.append(
                ValidationError(
                    code="duplicate_phase_id",
                    message="Phase IDs must be unique",
                    severity=ValidationSeverity.ERROR,
                )
            )

        id_set = set(ids)
        for phase in definition.phases:
            if phase.next and phase.next not in id_set and phase.next not in ("null",):
                errors.append(
                    ValidationError(
                        code="invalid_next",
                        message=f"Phase {phase.id} references unknown next: {phase.next}",
                        severity=ValidationSeverity.ERROR,
                    )
                )
            if not phase.gate.id:
                errors.append(
                    ValidationError(
                        code="missing_gate",
                        message=f"Phase {phase.id} missing gate id",
                        severity=ValidationSeverity.ERROR,
                    )
                )
        return errors


from runtime_engine.errors import KernelError  # noqa: E402 — circular guard
