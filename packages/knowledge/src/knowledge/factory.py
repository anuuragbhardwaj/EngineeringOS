"""Knowledge Platform factory."""

from __future__ import annotations

from knowledge.platform import KnowledgePlatform


def create_knowledge_platform() -> KnowledgePlatform:
    return KnowledgePlatform()
