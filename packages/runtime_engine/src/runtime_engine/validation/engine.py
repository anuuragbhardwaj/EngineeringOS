"""Artifact validation engine."""

from __future__ import annotations

from datetime import datetime

from runtime_engine.types import (
    ArtifactName,
    ArtifactRef,
    PipelineState,
    ValidationCheckType,
    ValidationContext,
    ValidationReport,
    ValidationResult,
    WorkflowDefinition,
)
from runtime_engine.validation.validators import (
    ExistenceValidator,
    McpEvidenceValidator,
    NonEmptyValidator,
    OwnershipValidator,
    RequiredSectionsValidator,
)


class ArtifactValidationEngine:
    """IArtifactValidationEngine implementation."""

    def __init__(self) -> None:
        self._validators: list = [
            ExistenceValidator(),
            NonEmptyValidator(),
            RequiredSectionsValidator(),
            OwnershipValidator(),
            McpEvidenceValidator(),
        ]

    def register(self, validator) -> None:
        self._validators.append(validator)

    def validate_phase_entry(
        self,
        state: PipelineState,
        workflow: WorkflowDefinition,
    ) -> ValidationReport:
        phase = workflow.phase_by_id(state.current_phase_id)
        if phase is None:
            return ValidationReport(phase_id=state.current_phase_id, passed=False)

        refs = self._input_refs(phase, state, workflow)
        return self._validate_refs(state, workflow, refs, state.current_phase_id)

    def validate_phase_exit(
        self,
        state: PipelineState,
        workflow: WorkflowDefinition,
    ) -> ValidationReport:
        phase = workflow.phase_by_id(state.current_phase_id)
        if phase is None:
            return ValidationReport(phase_id=state.current_phase_id, passed=False)

        refs = self._output_refs(phase, state, workflow)
        return self._validate_refs(state, workflow, refs, state.current_phase_id)

    def validate_artifact(
        self,
        state: PipelineState,
        artifact_name: ArtifactName,
        workflow: WorkflowDefinition,
    ) -> ValidationResult:
        record = state.artifact_index.get(artifact_name)
        if record is None:
            ref = ArtifactRef(name=artifact_name, path=artifact_name, owner_agent=None)
        else:
            ref = ArtifactRef(
                name=record.name,
                path=record.path,
                owner_agent=record.owner_agent,
            )
        return self._validate_single(state, workflow, ref, state.current_phase_id)

    def _validate_refs(
        self,
        state: PipelineState,
        workflow: WorkflowDefinition,
        refs: list[ArtifactRef],
        phase_id: str,
    ) -> ValidationReport:
        results = [
            self._validate_single(state, workflow, ref, phase_id) for ref in refs
        ]
        passed = all(r.passed for r in results)
        return ValidationReport(
            phase_id=phase_id,
            passed=passed,
            results=results,
            timestamp=datetime.utcnow(),
        )

    def _validate_single(
        self,
        state: PipelineState,
        workflow: WorkflowDefinition,
        ref: ArtifactRef,
        phase_id: str,
    ) -> ValidationResult:
        context = ValidationContext(
            project_id=state.project_id,
            phase_id=phase_id,
            artifact_root=state.artifact_root,
            workflow=workflow,
            state=state,
            check_types=list(ValidationCheckType),
        )
        merged = ValidationResult(passed=True, checks_run=[])
        for validator in self._validators:
            if (
                validator.supported_artifacts is not None
                and ref.name not in validator.supported_artifacts
            ):
                continue
            result = validator.validate(ref, context)
            merged.checks_run.extend(result.checks_run)
            merged.errors.extend(result.errors)
            merged.warnings.extend(result.warnings)
            if result.errors:
                merged.passed = False
        return merged

    def _input_refs(
        self,
        phase,
        state: PipelineState,
        workflow: WorkflowDefinition,
    ) -> list[ArtifactRef]:
        refs: list[ArtifactRef] = []
        for name in phase.required_inputs:
            record = state.artifact_index.get(name)
            path = record.path if record else name
            refs.append(ArtifactRef(name=name, path=path, owner_agent=None, required=True))
        return refs

    def _output_refs(
        self,
        phase,
        state: PipelineState,
        workflow: WorkflowDefinition,
    ) -> list[ArtifactRef]:
        refs: list[ArtifactRef] = []
        names = phase.required_outputs or [phase.primary_artifact]
        for name in names:
            record = state.artifact_index.get(name)
            path = record.path if record else name
            owner = record.owner_agent if record else phase.owner.agent
            refs.append(
                ArtifactRef(name=name, path=path, owner_agent=owner, required=True)
            )
        if workflow.artifacts.orchestration.required:
            orch = workflow.artifacts.orchestration
            refs.append(orch)
        return refs
