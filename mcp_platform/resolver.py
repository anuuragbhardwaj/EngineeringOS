"""Capability → MCP resolution."""

from __future__ import annotations

from pathlib import Path

from .loader import load_capabilities, load_registry
from .models import Resolution

INSTALLED_STATUSES = frozenset({"installed", "available"})


def is_usable(installation_status: str) -> bool:
    return installation_status in INSTALLED_STATUSES


def resolve_capability(capability_id: str, root: Path | None = None) -> Resolution:
    registry = load_registry(root)
    capabilities = load_capabilities(root)

    if capability_id not in capabilities:
        return Resolution(
            capability_id=capability_id,
            mcp_id=None,
            source="unavailable",
            message=f"Unknown capability: {capability_id}",
        )

    cap = capabilities[capability_id]
    if cap.policy_only:
        return Resolution(
            capability_id=capability_id,
            mcp_id=cap.primary_mcp,
            source="primary",
            message="policy_only — install not required for design references",
        )

    chain = [cap.primary_mcp] + cap.fallback_chain
    for i, mcp_id in enumerate(chain):
        if mcp_id not in registry:
            continue
        entry = registry[mcp_id]
        if is_usable(entry.installation_status):
            source = "primary" if i == 0 else "fallback"
            return Resolution(
                capability_id=capability_id,
                mcp_id=mcp_id,
                source=source,
                message=f"Resolved to {mcp_id} ({source})",
            )

    return Resolution(
        capability_id=capability_id,
        mcp_id=None,
        source="unavailable",
        message=f"No installed MCP for capability {capability_id}; chain: {chain}",
    )
