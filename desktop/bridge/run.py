"""Launch the Desktop Bridge server.

Usage:
    python -m desktop.bridge.run
    python -m desktop.bridge.run --port 9477 --reload
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure engineeringos packages and desktop module are importable.
_REPO = Path(__file__).resolve().parents[2]
_SRC_DIRS = [
    _REPO,
    _REPO / "packages" / "company_core" / "src",
    _REPO / "packages" / "company_simulation" / "src",
    _REPO / "packages" / "knowledge" / "src",
    _REPO / "packages" / "runtime_engine" / "src",
    _REPO / "packages" / "orchestrator" / "src",
    _REPO / "packages" / "ai_execution" / "src",
    _REPO / "packages" / "workspace_execution" / "src",
    _REPO / "packages" / "autonomous_company" / "src",
    _REPO / "packages" / "parallel_execution" / "src",
    _REPO / "packages" / "source_control" / "src",
    _REPO / "packages" / "company_lifecycle" / "src",
    _REPO / "packages" / "company_cli" / "src",
    _REPO / "mcp_platform",
]
for p in _SRC_DIRS:
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)


def main() -> None:
    parser = argparse.ArgumentParser(description="EngineeringOS Desktop Bridge")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9477)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    import uvicorn

    uvicorn.run(
        "desktop.bridge.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        factory=False,
    )


if __name__ == "__main__":
    main()
