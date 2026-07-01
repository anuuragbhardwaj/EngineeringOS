"""Knowledge object types and scopes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class KnowledgeScope(str, Enum):
    FRAMEWORK = "framework"
    COMPANY = "company"
    WORKSPACE = "workspace"
    PROJECT = "project"
    EMPLOYEE = "employee"
    CONVERSATION = "conversation"


class KnowledgeType(str, Enum):
    FACT = "fact"
    DECISION = "decision"
    LESSON = "lesson"
    CONVENTION = "convention"
    PREFERENCE = "preference"
    CONSTRAINT = "constraint"
    ARCHITECTURE_DECISION = "architecture_decision"
    BUG_PATTERN = "bug_pattern"
    ANTI_PATTERN = "anti_pattern"
    CODE_PATTERN = "code_pattern"
    API_CONTRACT = "api_contract"
    DEPENDENCY = "dependency"
    RISK = "risk"
    REQUIREMENT = "requirement"
    IMPLEMENTATION_NOTE = "implementation_note"
    REVIEW_FINDING = "review_finding"
    QA_FINDING = "qa_finding"
    DOCUMENTATION_RULE = "documentation_rule"
    RELEASE_NOTE = "release_note"
    MIGRATION_RULE = "migration_rule"
    PROMPT_IMPROVEMENT = "prompt_improvement"
    ENGINEERING_PRINCIPLE = "engineering_principle"
    CUSTOM = "custom"


class KnowledgeStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    RETIRED = "retired"


class RelationType(str, Enum):
    DEPENDS_ON = "depends_on"
    IMPLEMENTS = "implements"
    SUPERSEDES = "supersedes"
    DUPLICATES = "duplicates"
    CONTRADICTS = "contradicts"
    REFERENCES = "references"
    CAUSED_BY = "caused_by"
    DERIVED_FROM = "derived_from"
    VERIFIED_BY = "verified_by"
    OWNED_BY = "owned_by"
    RELATED_TO = "related_to"


SCOPE_HIERARCHY = [
    KnowledgeScope.CONVERSATION,
    KnowledgeScope.EMPLOYEE,
    KnowledgeScope.PROJECT,
    KnowledgeScope.WORKSPACE,
    KnowledgeScope.COMPANY,
    KnowledgeScope.FRAMEWORK,
]


@dataclass
class KnowledgeObject:
    """Durable engineering knowledge — not chat history."""

    id: str
    knowledge_type: str
    scope: str
    title: str
    content: str
    origin: str
    owner: str
    reason: str
    confidence: float = 0.5
    status: str = KnowledgeStatus.DRAFT.value
    created_at: str = ""
    updated_at: str = ""
    version: int = 1
    source_artifacts: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    workspace_id: str | None = None
    project_id: str | None = None
    employee_id: str | None = None
    conversation_id: str | None = None
    usage_count: int = 0
    reviewer_approved: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "knowledge_type": self.knowledge_type,
            "scope": self.scope,
            "title": self.title,
            "content": self.content,
            "origin": self.origin,
            "owner": self.owner,
            "reason": self.reason,
            "confidence": self.confidence,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
            "source_artifacts": self.source_artifacts,
            "tags": self.tags,
            "metadata": self.metadata,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "employee_id": self.employee_id,
            "conversation_id": self.conversation_id,
            "usage_count": self.usage_count,
            "reviewer_approved": self.reviewer_approved,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeObject:
        return cls(
            id=str(data["id"]),
            knowledge_type=str(data.get("knowledge_type", KnowledgeType.FACT.value)),
            scope=str(data.get("scope", KnowledgeScope.PROJECT.value)),
            title=str(data.get("title", "")),
            content=str(data.get("content", "")),
            origin=str(data.get("origin", "unknown")),
            owner=str(data.get("owner", "system")),
            reason=str(data.get("reason", "")),
            confidence=float(data.get("confidence", 0.5)),
            status=str(data.get("status", KnowledgeStatus.DRAFT.value)),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
            version=int(data.get("version", 1)),
            source_artifacts=list(data.get("source_artifacts") or []),
            tags=list(data.get("tags") or []),
            metadata=dict(data.get("metadata") or {}),
            workspace_id=data.get("workspace_id"),
            project_id=data.get("project_id"),
            employee_id=data.get("employee_id"),
            conversation_id=data.get("conversation_id"),
            usage_count=int(data.get("usage_count", 0)),
            reviewer_approved=bool(data.get("reviewer_approved", False)),
        )


@dataclass
class KnowledgeRelation:
    """Edge in the knowledge graph."""

    id: str
    source_id: str
    target_id: str
    relation_type: str
    created_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeRelation:
        return cls(
            id=str(data["id"]),
            source_id=str(data["source_id"]),
            target_id=str(data["target_id"]),
            relation_type=str(data.get("relation_type", RelationType.RELATED_TO.value)),
            created_at=str(data.get("created_at", "")),
            metadata=dict(data.get("metadata") or {}),
        )


@dataclass
class RetrievalContext:
    """Context for knowledge retrieval."""

    company_id: str | None = None
    workspace_id: str | None = None
    project_id: str | None = None
    employee_id: str | None = None
    phase_id: str | None = None
    artifacts: list[str] = field(default_factory=list)
    technology_stack: list[str] = field(default_factory=list)
    max_items: int = 10
    min_confidence: float = 0.3


@dataclass
class RetrievalResult:
    """Single retrieved knowledge item with relevance score."""

    knowledge: KnowledgeObject
    relevance: float
    explanation: str


@dataclass
class ValidationResult:
    """Outcome of knowledge validation."""

    valid: bool
    knowledge_id: str
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    adjusted_confidence: float | None = None


@dataclass
class PromotionRecord:
    """Audit trail for knowledge promotion."""

    knowledge_id: str
    from_scope: str
    to_scope: str
    approved_by: str
    reason: str
    timestamp: str
    rejected: bool = False
    rejection_reason: str | None = None


@dataclass
class KnowledgeQuery:
    """Structured knowledge query."""

    text: str | None = None
    knowledge_type: str | None = None
    scope: str | None = None
    project_id: str | None = None
    workspace_id: str | None = None
    employee_id: str | None = None
    tags: list[str] = field(default_factory=list)
    status: str | None = KnowledgeStatus.ACTIVE.value
    min_confidence: float = 0.0
    limit: int = 50


@dataclass
class KnowledgeStats:
    """Aggregate knowledge statistics."""

    total: int = 0
    by_scope: dict[str, int] = field(default_factory=dict)
    by_type: dict[str, int] = field(default_factory=dict)
    by_status: dict[str, int] = field(default_factory=dict)
    avg_confidence: float = 0.0
    promotion_count: int = 0


def utc_now() -> str:
    return datetime.utcnow().isoformat()
