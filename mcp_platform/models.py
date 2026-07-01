"""Data models for MCP Platform."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class McpEntry:
    id: str
    name: str
    category: str
    integration_type: str
    capabilities: list[str]
    installation_status: str
    health_status: str
    fallback_mcp: str | None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class CapabilityEntry:
    id: str
    description: str
    primary_mcp: str
    fallback_chain: list[str]
    evidence_required: bool
    policy_only: bool = False
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Resolution:
    capability_id: str
    mcp_id: str | None
    source: str  # primary | fallback | unavailable
    message: str


@dataclass
class ValidationResult:
    check: str
    passed: bool
    message: str
