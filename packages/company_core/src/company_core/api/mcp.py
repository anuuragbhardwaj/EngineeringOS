"""McpAPI — delegates to mcp_platform."""

from __future__ import annotations

from pathlib import Path

from company_core.config.loader import discover_framework_root, discover_instance_root
from company_core.models.common import (
    CapabilityInfo,
    DoctorCheck,
    HealthReport,
    McpInfo,
    ValidationReport,
)
from company_core.models.errors import NotImplementedFeatureError


class McpAPI:
    """MCP registry operations via mcp_platform."""

    def _framework_root(self) -> Path | None:
        return discover_framework_root(discover_instance_root())

    def list_capabilities(self) -> list[CapabilityInfo]:
        root = self._framework_root()
        if root is None:
            return []
        try:
            from mcp_platform.loader import load_capabilities
        except ImportError:
            return []

        caps = load_capabilities(root)
        return [
            CapabilityInfo(capability_id=cap.id, description=cap.description)
            for cap in caps.values()
        ]

    def list_tools(self) -> list[McpInfo]:
        root = self._framework_root()
        if root is None:
            return []
        try:
            from mcp_platform.loader import load_registry
        except ImportError:
            return []

        registry = load_registry(root)
        return [
            McpInfo(
                mcp_id=entry.id,
                category=entry.category,
                installation_status=entry.installation_status,
            )
            for entry in registry.values()
        ]

    def resolve(self, capability_id: str) -> object:
        root = self._framework_root()
        if root is None:
            raise NotImplementedFeatureError("Framework root not found for MCP resolve")
        from mcp_platform.resolver import resolve_capability

        return resolve_capability(capability_id, root)

    def validate(self) -> ValidationReport:
        root = self._framework_root()
        if root is None:
            return ValidationReport(
                passed=False,
                checks=[
                    DoctorCheck(
                        "framework_root",
                        False,
                        "Framework root not found",
                    )
                ],
            )
        try:
            from mcp_platform.validator import validate_all
        except ImportError:
            return ValidationReport(
                passed=False,
                checks=[
                    DoctorCheck(
                        "mcp_platform",
                        False,
                        "mcp_platform package not installed",
                    )
                ],
            )

        results = validate_all(root)
        checks = [
            DoctorCheck(r.check, r.passed, r.message) for r in results
        ]
        return ValidationReport(
            passed=all(r.passed for r in results),
            checks=checks,
        )

    def doctor(self) -> HealthReport:
        root = self._framework_root()
        if root is None:
            return HealthReport(
                passed=False,
                checks=[
                    DoctorCheck(
                        "framework_root",
                        False,
                        "Framework root not found",
                    )
                ],
            )
        try:
            from mcp_platform.health import run_health_checks
        except ImportError:
            return HealthReport(
                passed=False,
                checks=[
                    DoctorCheck(
                        "mcp_platform",
                        False,
                        "mcp_platform package not installed",
                    )
                ],
            )

        results = run_health_checks(None, root)
        checks = [DoctorCheck("health", r.passed, r.message) for r in results]
        return HealthReport(passed=all(r.passed for r in results), checks=checks)
