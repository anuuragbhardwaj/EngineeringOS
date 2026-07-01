"""Kernel shared types per runtime/interfaces.md."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

PhaseId = str
GateId = str
ProjectId = str
AgentId = str
ArtifactName = str
SymptomId = str
PluginId = str
SubscriptionId = str


class ProjectStatus(Enum):
    ACTIVE = "active"
    AT_RISK = "at_risk"
    BLOCKED = "blocked"
    RELEASED = "released"
    CLOSED = "closed"
    PAUSED = "paused"


class PhaseStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASS = "pass"
    FAIL = "fail"
    SKIPPED = "skipped"


class ValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class AdapterStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    DELEGATED = "delegated"


class ValidationCheckType(Enum):
    EXISTENCE = "existence"
    NON_EMPTY = "non_empty"
    REQUIRED_SECTIONS = "required_sections"
    OWNERSHIP = "ownership"
    VERSION = "version"
    APPROVAL_STATUS = "approval_status"
    CROSS_REFERENCE = "cross_reference"
    SCHEMA = "schema"
    MCP_EVIDENCE = "mcp_evidence"


@dataclass
class ArtifactRef:
    name: ArtifactName
    path: str
    owner_agent: AgentId | None
    required: bool = True


@dataclass
class TransitionDecision:
    allowed: bool
    reason: str | None = None
    blockers: list[str] = field(default_factory=list)


@dataclass
class ValidationError:
    code: str
    message: str
    severity: ValidationSeverity
    artifact: ArtifactName | None = None
    path: str | None = None


@dataclass
class ValidationResult:
    passed: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    checks_run: list[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    phase_id: PhaseId
    passed: bool
    results: list[ValidationResult] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GateEvaluation:
    gate_id: GateId
    phase_id: PhaseId
    passed: bool
    errors: list[str] = field(default_factory=list)
    artifact_results: list[ValidationResult] = field(default_factory=list)
    strike_count: int = 0
    max_strikes: int = 3


@dataclass
class GateRecord:
    gate_id: GateId
    phase_id: PhaseId
    passed: bool
    timestamp: datetime
    notes: str
    evaluator: str
    user_approved: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReworkRecord:
    id: str
    timestamp: datetime
    from_phase_id: PhaseId
    to_phase_id: PhaseId
    symptom: SymptomId
    reason: str
    resolved: bool = False
    resolved_at: datetime | None = None


@dataclass
class AgentDescriptor:
    agent_id: AgentId
    role: str
    phase_id: PhaseId
    primary_artifact: ArtifactName
    parallel: bool = False
    contributors: list[AgentId] = field(default_factory=list)
    prompt_path: str | None = None
    expected_inputs: list[str] = field(default_factory=list)
    expected_outputs: list[str] = field(default_factory=list)


@dataclass
class AdapterResult:
    status: AdapterStatus
    agent_id: AgentId
    phase_id: PhaseId
    message: str
    job_id: str | None = None
    artifacts_touched: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectStatusView:
    project_id: ProjectId
    status: ProjectStatus
    current_phase_id: PhaseId
    current_gate_id: GateId | None
    phase_status: dict[PhaseId, PhaseStatus]
    gate_strikes: dict[GateId, int]
    blockers: list[str]
    last_gate: GateRecord | None
    open_rework: ReworkRecord | None
    next_agent: AgentDescriptor | None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ArtifactRecord:
    name: ArtifactName
    path: str
    owner_agent: AgentId | None
    last_validated_at: datetime | None = None
    validation_status: PhaseStatus | None = None
    version: str | None = None
    approved: bool = False


@dataclass
class TransitionRecord:
    timestamp: datetime
    from_phase_id: PhaseId
    to_phase_id: PhaseId
    gate_id: GateId | None
    trigger: str


@dataclass
class ParallelTrack:
    track_id: str
    agent_id: AgentId
    phase_id: PhaseId
    status: PhaseStatus
    merge_complete: bool = False


@dataclass
class ExecutionState:
    parallel_tracks: list[ParallelTrack] = field(default_factory=list)
    active_agent_id: AgentId | None = None
    last_invocation_at: datetime | None = None
    invocation_count: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)
    pipeline_completed: bool = False
    pipeline_stop_phase: PhaseId | None = None


@dataclass
class PipelineState:
    project_id: ProjectId
    status: ProjectStatus
    artifact_root: str
    workflow_version: str
    workflow_path: str
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any]
    current_phase_id: PhaseId
    phase_status: dict[PhaseId, PhaseStatus]
    skip_risk_accepted: dict[GateId, bool]
    gate_strikes: dict[GateId, int]
    artifact_index: dict[ArtifactName, ArtifactRecord]
    rework_history: list[ReworkRecord]
    gate_history: list[GateRecord]
    transition_history: list[TransitionRecord]
    execution: ExecutionState
    schema_version: str


@dataclass
class KernelEvent:
    type: str
    project_id: ProjectId
    timestamp: datetime
    contract_version: str
    payload: dict[str, Any]
    correlation_id: str | None = None


@dataclass
class InvocationContext:
    project_id: ProjectId
    phase_id: PhaseId
    artifact_root: str
    required_inputs: list[ArtifactRef]
    deliverable: ArtifactName
    delegation_brief: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationContext:
    project_id: ProjectId
    phase_id: PhaseId
    artifact_root: str
    workflow: Any
    state: PipelineState
    check_types: list[ValidationCheckType]


@dataclass
class AdapterHealth:
    available: bool
    message: str


@dataclass
class AgentAssignment:
    agent: AgentId
    role: str


@dataclass
class GateDefinition:
    id: GateId
    name: str
    approver: str
    facilitator: AgentId
    pass_when: str


@dataclass
class RejectionPath:
    condition: str
    route_to: str
    action: str = ""


@dataclass
class PhaseDefinition:
    id: PhaseId
    order: int
    name: str
    owner: AgentAssignment
    contributors: list[AgentAssignment]
    primary_artifact: ArtifactName
    entry_criteria: list[str]
    exit_criteria: list[str]
    gate: GateDefinition
    rejection_paths: list[RejectionPath]
    next: PhaseId | None
    skippable: bool = False
    mcp_requirements: list[str] = field(default_factory=list)
    required_inputs: list[str] = field(default_factory=list)
    required_outputs: list[str] = field(default_factory=list)


@dataclass
class ReworkTarget:
    route_to: str
    action: str
    owner: str | None = None


@dataclass
class WorkflowDefaults:
    artifact_root: str
    max_gate_failures: int
    orchestrator_agent: AgentId


@dataclass
class ArtifactManifest:
    orchestration: ArtifactRef
    phases: dict[PhaseId, list[ArtifactName]]


@dataclass
class WorkflowDefinition:
    version: str
    name: str
    phases: list[PhaseDefinition]
    rework_routing: dict[SymptomId, ReworkTarget]
    defaults: WorkflowDefaults
    artifacts: ArtifactManifest

    def phase_by_id(self, phase_id: PhaseId) -> PhaseDefinition | None:
        for phase in self.phases:
            if phase.id == phase_id:
                return phase
        return None

    def ordered_phases(self) -> list[PhaseDefinition]:
        return sorted(self.phases, key=lambda p: p.order)

    def planning_phases(self) -> list[PhaseDefinition]:
        """Phases from idea through architecture (Runtime v1 scope)."""
        return [p for p in self.ordered_phases() if p.order <= 4]
