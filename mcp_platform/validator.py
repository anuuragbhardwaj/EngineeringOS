"""MCP Platform validation checks."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .loader import load_capabilities, load_mcp_json, load_registry
from .models import ValidationResult

DEFAULT_ROOT = Path(__file__).resolve().parent.parent
SECRET_PATTERN = re.compile(
    r"(api[_-]?key|token|password|secret)\s*[:=]\s*['\"]?[a-zA-Z0-9_\-]{8,}",
    re.IGNORECASE,
)
REQUIRED_MCP_FIELDS = (
    "name",
    "category",
    "integration_type",
    "capabilities",
    "employees",
    "installation_status",
    "health_status",
    "permissions",
    "configuration",
    "runtime_compatibility",
)


def validate_registry(root: Path | None = None) -> list[ValidationResult]:
    root = root or DEFAULT_ROOT
    results: list[ValidationResult] = []
    registry_path = root / "mcp" / "registry.yaml"
    caps_path = root / "mcp" / "capabilities.yaml"

    if not registry_path.exists():
        return [ValidationResult("registry", False, f"Missing {registry_path}")]

    registry = load_registry(root)
    capabilities = load_capabilities(root)

    if len(registry) < 30:
        results.append(
            ValidationResult(
                "registry",
                False,
                f"Expected >=30 MCPs, found {len(registry)}",
            )
        )
    else:
        results.append(
            ValidationResult("registry", True, f"{len(registry)} MCPs in registry")
        )

    for mcp_id, entry in registry.items():
        for field in REQUIRED_MCP_FIELDS:
            if field not in entry.raw and field not in (
                "employees",
                "permissions",
                "configuration",
            ):
                # employees/permissions/configuration are nested in raw
                if field == "employees" and "employees" not in entry.raw:
                    results.append(
                        ValidationResult(
                            "registry",
                            False,
                            f"{mcp_id}: missing employees",
                        )
                    )

        for cap in entry.capabilities:
            if cap not in capabilities:
                results.append(
                    ValidationResult(
                        "registry",
                        False,
                        f"{mcp_id}: capability '{cap}' not in capabilities.yaml",
                    )
                )

        fb = entry.fallback_mcp
        if fb and fb not in registry:
            results.append(
                ValidationResult(
                    "registry",
                    False,
                    f"{mcp_id}: fallback_mcp '{fb}' not in registry",
                )
            )

    for cap_id, cap in capabilities.items():
        if cap.primary_mcp not in registry:
            results.append(
                ValidationResult(
                    "capabilities",
                    False,
                    f"{cap_id}: primary_mcp '{cap.primary_mcp}' not in registry",
                )
            )
        for fb in cap.fallback_chain:
            if fb not in registry:
                results.append(
                    ValidationResult(
                        "capabilities",
                        False,
                        f"{cap_id}: fallback '{fb}' not in registry",
                    )
                )

    if len(capabilities) < 20:
        results.append(
            ValidationResult(
                "capabilities",
                False,
                f"Expected >=20 capabilities, found {len(capabilities)}",
            )
        )
    else:
        results.append(
            ValidationResult(
                "capabilities",
                True,
                f"{len(capabilities)} capabilities defined",
            )
        )

    return results


def validate_mcp_json(root: Path | None = None) -> list[ValidationResult]:
    root = root or DEFAULT_ROOT
    results: list[ValidationResult] = []
    registry = load_registry(root)
    mcp_json = load_mcp_json(root)
    servers = mcp_json.get("mcpServers") or {}

    for mcp_id in servers:
        if mcp_id not in registry:
            results.append(
                ValidationResult(
                    "mcp-json",
                    False,
                    f"mcp.json server '{mcp_id}' not in registry",
                )
            )
            continue
        entry = registry[mcp_id]
        if entry.installation_status not in ("installed", "available"):
            results.append(
                ValidationResult(
                    "mcp-json",
                    False,
                    f"mcp.json includes '{mcp_id}' but registry status is {entry.installation_status}",
                )
            )
        else:
            results.append(
                ValidationResult(
                    "mcp-json",
                    True,
                    f"'{mcp_id}' synced with registry",
                )
            )

    installed = [
        mcp_id
        for mcp_id, e in registry.items()
        if e.installation_status == "installed"
        and e.integration_type == "stdio"
    ]
    for mcp_id in installed:
        if mcp_id not in servers:
            results.append(
                ValidationResult(
                    "mcp-json",
                    False,
                    f"Registry marks '{mcp_id}' installed but missing from mcp.json",
                )
            )

    cursor_path = root / ".cursor" / "mcp.json"
    if cursor_path.exists():
        cursor_data = json.loads(cursor_path.read_text(encoding="utf-8"))
        cursor_servers = set((cursor_data.get("mcpServers") or {}).keys())
        json_servers = set(servers.keys())
        missing = json_servers - cursor_servers
        if missing:
            results.append(
                ValidationResult(
                    "mcp-json",
                    False,
                    f".cursor/mcp.json missing servers: {sorted(missing)}",
                )
            )
        else:
            results.append(
                ValidationResult("mcp-json", True, ".cursor/mcp.json in sync")
            )

    return results


def validate_secrets(root: Path | None = None) -> list[ValidationResult]:
    root = root or DEFAULT_ROOT
    results: list[ValidationResult] = []
    for path in [root / "mcp.json", root / ".cursor" / "mcp.json"]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if SECRET_PATTERN.search(text):
            results.append(
                ValidationResult("secrets", False, f"Possible secret in {path.name}")
            )
        else:
            results.append(
                ValidationResult("secrets", True, f"No secrets detected in {path.name}")
            )
    return results


def validate_all(root: Path | None = None, checks: list[str] | None = None) -> list[ValidationResult]:
    root = root or DEFAULT_ROOT
    all_checks = checks or ["registry", "mcp-json", "secrets"]
    results: list[ValidationResult] = []
    if "registry" in all_checks:
        results.extend(validate_registry(root))
    if "mcp-json" in all_checks:
        results.extend(validate_mcp_json(root))
    if "secrets" in all_checks:
        results.extend(validate_secrets(root))
    return results
