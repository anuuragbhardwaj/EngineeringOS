"""Built-in artifact validators."""

from __future__ import annotations

import re
from pathlib import Path

from runtime_engine.types import (
    ArtifactRef,
    ValidationCheckType,
    ValidationContext,
    ValidationError,
    ValidationResult,
    ValidationSeverity,
)

MIN_CONTENT_BYTES = 64
PLACEHOLDER_PATTERN = re.compile(r"TODO|FIXME|TBD", re.IGNORECASE)

SECTION_RULES: dict[str, list[str]] = {
    "idea.md": ["## Problem", "## Users", "## Value", "## Decision"],
    "requirements.md": [
        "## Problem",
        "## Users",
        "## Goals",
        "## MoSCoW",
        "## Success Metrics",
        "## Open Questions",
    ],
    "spec.md": ["## Functional Requirements", "## Non-Functional Requirements", "## Edge Cases"],
    "tasks.md": ["## Task Index", "## Tasks"],
    "architecture.md": [
        "## Overview",
        "## API Contracts",
        "## Data Model",
        "## Security",
    ],
    "pipeline-status.md": ["## Pipeline Status", "## Current Phase"],
}

MCP_EVIDENCE_MARKERS = {
    "tasks.md": "mcp-evidence: structured-reasoning",
    "architecture.md": "mcp-evidence: documentation-lookup",
}


class ExistenceValidator:
    name = "existence"

    @property
    def supported_artifacts(self) -> None:
        return None

    def validate(self, ref: ArtifactRef, context: ValidationContext) -> ValidationResult:
        root = Path(context.artifact_root)
        path = root / ref.path
        errors: list[ValidationError] = []
        if not path.is_file():
            errors.append(
                ValidationError(
                    code="artifact_missing",
                    message=f"Artifact not found: {ref.path}",
                    severity=ValidationSeverity.ERROR,
                    artifact=ref.name,
                    path=str(path),
                )
            )
        return ValidationResult(
            passed=not errors,
            errors=errors,
            checks_run=[ValidationCheckType.EXISTENCE.value],
        )


class NonEmptyValidator:
    name = "non_empty"

    @property
    def supported_artifacts(self) -> None:
        return None

    def validate(self, ref: ArtifactRef, context: ValidationContext) -> ValidationResult:
        root = Path(context.artifact_root)
        path = root / ref.path
        errors: list[ValidationError] = []
        if path.is_file():
            content = path.read_text(encoding="utf-8")
            if len(content.encode("utf-8")) < MIN_CONTENT_BYTES:
                errors.append(
                    ValidationError(
                        code="artifact_empty",
                        message=f"Artifact too small: {ref.path}",
                        severity=ValidationSeverity.ERROR,
                        artifact=ref.name,
                    )
                )
            if PLACEHOLDER_PATTERN.search(content):
                errors.append(
                    ValidationError(
                        code="placeholder_content",
                        message=f"Placeholder markers found in {ref.path}",
                        severity=ValidationSeverity.ERROR,
                        artifact=ref.name,
                    )
                )
        return ValidationResult(
            passed=not errors,
            errors=errors,
            checks_run=[ValidationCheckType.NON_EMPTY.value],
        )


class RequiredSectionsValidator:
    name = "required_sections"

    @property
    def supported_artifacts(self) -> None:
        return None

    def validate(self, ref: ArtifactRef, context: ValidationContext) -> ValidationResult:
        root = Path(context.artifact_root)
        path = root / ref.path
        errors: list[ValidationError] = []
        required = SECTION_RULES.get(ref.name, [])
        if path.is_file() and required:
            content = path.read_text(encoding="utf-8")
            for section in required:
                if section not in content:
                    errors.append(
                        ValidationError(
                            code="missing_section",
                            message=f"Missing section {section} in {ref.path}",
                            severity=ValidationSeverity.ERROR,
                            artifact=ref.name,
                        )
                    )
        return ValidationResult(
            passed=not errors,
            errors=errors,
            checks_run=[ValidationCheckType.REQUIRED_SECTIONS.value],
        )


class OwnershipValidator:
    name = "ownership"

    @property
    def supported_artifacts(self) -> None:
        return None

    def validate(self, ref: ArtifactRef, context: ValidationContext) -> ValidationResult:
        phase = context.workflow.phase_by_id(context.phase_id)
        errors: list[ValidationError] = []
        if phase and ref.owner_agent and ref.owner_agent != phase.owner.agent:
            errors.append(
                ValidationError(
                    code="ownership_mismatch",
                    message=(
                        f"Artifact {ref.name} owner {ref.owner_agent} "
                        f"does not match phase owner {phase.owner.agent}"
                    ),
                    severity=ValidationSeverity.WARNING,
                    artifact=ref.name,
                )
            )
        return ValidationResult(
            passed=True,
            warnings=errors,
            checks_run=[ValidationCheckType.OWNERSHIP.value],
        )


class McpEvidenceValidator:
    name = "mcp_evidence"

    @property
    def supported_artifacts(self) -> None:
        return None

    def validate(self, ref: ArtifactRef, context: ValidationContext) -> ValidationResult:
        marker = MCP_EVIDENCE_MARKERS.get(ref.name)
        errors: list[ValidationError] = []
        if marker:
            path = Path(context.artifact_root) / ref.path
            if path.is_file():
                content = path.read_text(encoding="utf-8")
                if marker not in content:
                    errors.append(
                        ValidationError(
                            code="mcp_evidence_missing",
                            message=f"Missing MCP evidence marker in {ref.path}",
                            severity=ValidationSeverity.ERROR,
                            artifact=ref.name,
                        )
                    )
        return ValidationResult(
            passed=not errors,
            errors=errors,
            checks_run=[ValidationCheckType.MCP_EVIDENCE.value],
        )
