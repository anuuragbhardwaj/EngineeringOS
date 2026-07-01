"""Runtime factory bridge — composition root wires runtime_engine without company_core importing it."""

from __future__ import annotations

from typing import Any, Callable

_RUNTIME_FACTORY: Callable[..., Any] | None = None


def configure_runtime_factory(factory: Callable[..., Any]) -> None:
    """Register Runtime factory (called from CLI/tests composition root)."""
    global _RUNTIME_FACTORY
    _RUNTIME_FACTORY = factory


def reset_runtime_factory() -> None:
    global _RUNTIME_FACTORY
    _RUNTIME_FACTORY = None


def create_runtime(**kwargs: Any) -> Any:
    if _RUNTIME_FACTORY is None:
        raise RuntimeError(
            "Runtime factory not configured. Use engineeringos CLI or configure_runtime_factory()."
        )
    return _RUNTIME_FACTORY(**kwargs)
