"""CLI entry point: python -m mcp_platform"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .health import run_health_checks
from .resolver import resolve_capability
from .validator import validate_all

DEFAULT_ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI Company MCP Platform tools")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Project root")
    sub = parser.add_subparsers(dest="command", required=True)

    val_parser = sub.add_parser("validate", help="Run validation checks")
    val_parser.add_argument(
        "--check",
        action="append",
        choices=["registry", "mcp-json", "secrets"],
        help="Specific check (repeatable)",
    )

    health_parser = sub.add_parser("health", help="Run health checks")
    health_parser.add_argument("mcp_id", nargs="?", help="Specific MCP id")

    resolve_parser = sub.add_parser("resolve", help="Resolve capability to MCP")
    resolve_parser.add_argument("capability_id", help="Capability id")

    args = parser.parse_args(argv)
    root: Path = args.root

    if args.command == "validate":
        checks = args.check or None
        results = validate_all(root, checks)
        failed = [r for r in results if not r.passed]
        for r in results:
            status = "PASS" if r.passed else "FAIL"
            print(f"[{status}] {r.check}: {r.message}")
        return 1 if failed else 0

    if args.command == "health":
        results = run_health_checks(args.mcp_id, root)
        failed = [r for r in results if not r.passed]
        for r in results:
            status = "PASS" if r.passed else "FAIL"
            print(f"[{status}] {r.message}")
        return 1 if failed else 0

    if args.command == "resolve":
        res = resolve_capability(args.capability_id, root)
        print(f"Capability: {res.capability_id}")
        print(f"MCP: {res.mcp_id}")
        print(f"Source: {res.source}")
        print(f"Message: {res.message}")
        return 0 if res.mcp_id else 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
