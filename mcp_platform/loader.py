"""Load registry.yaml and capabilities.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import CapabilityEntry, McpEntry

DEFAULT_ROOT = Path(__file__).resolve().parent.parent


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_registry(root: Path | None = None) -> dict[str, McpEntry]:
    root = root or DEFAULT_ROOT
    data = load_yaml(root / "mcp" / "registry.yaml")
    mcps: dict[str, McpEntry] = {}
    for mcp_id, entry in (data.get("mcps") or {}).items():
        mcps[mcp_id] = McpEntry(
            id=mcp_id,
            name=entry.get("name", mcp_id),
            category=entry.get("category", "unknown"),
            integration_type=entry.get("integration_type", "stdio"),
            capabilities=entry.get("capabilities") or [],
            installation_status=entry.get("installation_status", "not_installed"),
            health_status=entry.get("health_status", "unknown"),
            fallback_mcp=entry.get("fallback_mcp"),
            raw=entry,
        )
    return mcps


def load_capabilities(root: Path | None = None) -> dict[str, CapabilityEntry]:
    root = root or DEFAULT_ROOT
    data = load_yaml(root / "mcp" / "capabilities.yaml")
    caps: dict[str, CapabilityEntry] = {}
    for cap_id, entry in (data.get("capabilities") or {}).items():
        caps[cap_id] = CapabilityEntry(
            id=cap_id,
            description=entry.get("description", ""),
            primary_mcp=entry.get("primary_mcp", ""),
            fallback_chain=entry.get("fallback_chain") or [],
            evidence_required=bool(entry.get("evidence_required", False)),
            policy_only=bool(entry.get("policy_only", False)),
            raw=entry,
        )
    return caps


def load_mcp_json(root: Path | None = None) -> dict[str, Any]:
    root = root or DEFAULT_ROOT
    path = root / "mcp.json"
    if not path.exists():
        return {}
    return load_yaml(path)
