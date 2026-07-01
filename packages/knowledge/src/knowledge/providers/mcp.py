"""MCP provider integration for knowledge verification."""

from __future__ import annotations

from knowledge.types import KnowledgeObject


class McpKnowledgeProvider:
    """Optional external verification via MCP — degrades gracefully."""

    def verify(self, knowledge: KnowledgeObject, mcp_available: bool = True) -> tuple[float, str]:
        if not mcp_available:
            reduced = max(0.1, knowledge.confidence - 0.15)
            return reduced, "MCP unavailable — confidence reduced"
        return knowledge.confidence, "MCP verification not configured"

    def enrich_from_context7(self, knowledge: KnowledgeObject, docs_snippet: str | None) -> KnowledgeObject:
        if docs_snippet:
            knowledge.metadata["context7_verified"] = True
            knowledge.metadata["context7_snippet"] = docs_snippet[:500]
            knowledge.confidence = min(1.0, knowledge.confidence + 0.1)
        return knowledge
