"""Wire Runtime implementation at CLI composition root."""

from __future__ import annotations

from company_core.runtime_bridge import configure_runtime_factory


def bootstrap_runtime() -> None:
    from runtime_engine.factory import create_runtime

    configure_runtime_factory(create_runtime)


bootstrap_runtime()
