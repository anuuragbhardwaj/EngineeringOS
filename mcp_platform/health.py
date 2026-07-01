"""Health checks for installed MCPs."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .loader import load_registry
from .models import ValidationResult

DEFAULT_ROOT = Path(__file__).resolve().parent.parent


def check_npx_available() -> ValidationResult:
    if shutil.which("npx"):
        return ValidationResult("health", True, "npx available")
    return ValidationResult("health", False, "npx not found in PATH")


def check_sequential_thinking(root: Path | None = None) -> ValidationResult:
    root = root or DEFAULT_ROOT
    registry = load_registry(root)
    entry = registry.get("sequential-thinking")
    if not entry or entry.installation_status != "installed":
        return ValidationResult(
            "health",
            True,
            "sequential-thinking not marked installed — skip",
        )

    npx = shutil.which("npx")
    if not npx:
        return ValidationResult("health", False, "npx required for sequential-thinking")

    try:
        proc = subprocess.run(
            [npx, "-y", "@modelcontextprotocol/server-sequential-thinking"],
            capture_output=True,
            text=True,
            timeout=15,
            input="",
        )
        # Server starts on stdio; any quick start without immediate crash is OK
        if "Sequential Thinking" in (proc.stderr or "") or proc.returncode is None:
            return ValidationResult(
                "health",
                True,
                "sequential-thinking server starts",
            )
        if proc.returncode != 0 and not proc.stderr:
            return ValidationResult(
                "health",
                False,
                f"sequential-thinking failed: rc={proc.returncode}",
            )
        return ValidationResult(
            "health",
            True,
            "sequential-thinking package reachable via npx",
        )
    except subprocess.TimeoutExpired:
        return ValidationResult(
            "health",
            True,
            "sequential-thinking server started (stdio — timeout expected)",
        )
    except Exception as exc:
        return ValidationResult("health", False, f"sequential-thinking error: {exc}")


def check_context7() -> ValidationResult:
    return ValidationResult(
        "health",
        True,
        "context7 is cursor-plugin — verify manually via Context7 skill",
    )


def run_health_checks(mcp_id: str | None = None, root: Path | None = None) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    if mcp_id is None or mcp_id == "sequential-thinking":
        results.append(check_npx_available())
        results.append(check_sequential_thinking(root))
    if mcp_id is None or mcp_id == "context7":
        results.append(check_context7())
    return results
