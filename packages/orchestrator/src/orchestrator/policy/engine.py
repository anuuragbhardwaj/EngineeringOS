"""Execution policy engine."""

from __future__ import annotations

from pathlib import Path

import yaml

from orchestrator.types import ExecutionPolicy


class PolicyEngine:
    """Configuration-driven execution policies."""

    def __init__(self, config_path: Path | None = None) -> None:
        self._defaults: dict = {}
        self._phase_policies: dict[str, dict] = {}
        self._policies: dict[str, dict] = {}
        if config_path and config_path.is_file():
            self.load(config_path)

    def load(self, path: Path) -> None:
        with path.open(encoding="utf-8") as handle:
            raw = yaml.safe_load(handle) or {}
        self._defaults = raw.get("defaults", {})
        self._phase_policies = raw.get("phases", {})
        self._policies = raw.get("policies", {})

    def resolve(self, phase_id: str, gate_id: str | None = None) -> ExecutionPolicy:
        phase_cfg = self._phase_policies.get(phase_id, {})
        policy_name = phase_cfg.get("policy", "sequential")
        policy_cfg = self._policies.get(policy_name, {})

        approval_gates = self._defaults.get("approval_required_gates", [])
        approval_required = bool(phase_cfg.get("approval_required", False))
        if gate_id and gate_id in approval_gates:
            approval_required = True

        return ExecutionPolicy(
            name=policy_name,
            sequential=bool(
                policy_cfg.get("sequential", self._defaults.get("sequential", True))
            ),
            max_retries=int(
                policy_cfg.get("max_retries", self._defaults.get("max_retries", 2))
            ),
            timeout_seconds=int(
                policy_cfg.get(
                    "timeout_seconds", self._defaults.get("timeout_seconds", 300)
                )
            ),
            approval_required=approval_required
            or bool(policy_cfg.get("approval_required", False)),
            context_max_chars=int(self._defaults.get("context_max_chars", 32000)),
            mcp_evidence_required=bool(phase_cfg.get("mcp_evidence_required", False)),
        )

    def should_retry(self, policy: ExecutionPolicy, attempt: int, failed: bool) -> bool:
        return failed and attempt < policy.max_retries
