"""Unified approval engine."""

from __future__ import annotations

import uuid
from pathlib import Path

from autonomous_company.policies.store import AutonomousStore
from autonomous_company.types import ApprovalRequest, utc_now

DEFAULT_GATES = ("architecture", "implementation", "review", "documentation", "commit", "push", "release")


class ApprovalEngine:
    """EM-controlled approvals — execution resumes automatically after approval."""

    def __init__(self, store: AutonomousStore | None = None) -> None:
        self._store = store or AutonomousStore()

    def approval_key(self, project_id: str, gate: str) -> str:
        return f"{project_id}:{gate}"

    def request(self, instance_root: Path, project_id: str, gate: str, reason: str = "") -> ApprovalRequest:
        data = self._store.load_approvals(instance_root)
        key = self.approval_key(project_id, gate)
        req = ApprovalRequest(
            approval_id=f"apr-{uuid.uuid4().hex[:8]}",
            gate=gate,
            project_id=project_id,
            approved=False,
            reason=reason,
            timestamp=utc_now(),
        )
        data[key] = req.to_dict()
        self._store.save_approvals(instance_root, data)
        self._sync_session_pending(instance_root)
        return req

    def approve(
        self,
        instance_root: Path,
        project_id: str,
        gate: str,
        *,
        approved_by: str = "engineering-manager",
        reason: str = "",
    ) -> ApprovalRequest:
        data = self._store.load_approvals(instance_root)
        key = self.approval_key(project_id, gate)
        req = ApprovalRequest(
            approval_id=data.get(key, {}).get("approval_id", f"apr-{uuid.uuid4().hex[:8]}"),
            gate=gate,
            project_id=project_id,
            approved=True,
            approved_by=approved_by,
            reason=reason,
            timestamp=utc_now(),
        )
        data[key] = req.to_dict()
        self._store.save_approvals(instance_root, data)

        # Also approve orchestrator gate if applicable
        try:
            from runtime_engine.factory import create_runtime
            from company_core.config.loader import discover_framework_root

            runtime = create_runtime(framework_root=discover_framework_root(instance_root))
            runtime._orchestrator.approve(project_id, gate.upper() if gate.startswith("G") else f"G{gate}")  # noqa: SLF001
        except Exception:
            pass

        # Source control approval
        if gate in ("commit", "push", "release"):
            try:
                from source_control.factory import create_source_control_platform

                sc = create_source_control_platform()
                sc.approve(instance_root, gate, project_id, reason=reason)
            except Exception:
                pass

        self._clear_session_pending(instance_root)
        return req

    def is_approved(self, instance_root: Path, project_id: str, gate: str) -> bool:
        data = self._store.load_approvals(instance_root)
        key = self.approval_key(project_id, gate)
        entry = data.get(key)
        return bool(entry and entry.get("approved"))

    def pending(self, instance_root: Path) -> list[ApprovalRequest]:
        data = self._store.load_approvals(instance_root)
        pending: list[ApprovalRequest] = []
        for entry in data.values():
            if not entry.get("approved"):
                pending.append(ApprovalRequest(**entry))
        return pending

    def requires_approval(self, instance_root: Path, gate: str) -> bool:
        policy = self._store.load_policy(instance_root)
        return gate in policy.approval_gates

    def _sync_session_pending(self, instance_root: Path) -> None:
        try:
            from workspace_execution.session.store import load_session, save_session

            session = load_session(instance_root)
            session.execution_status = "pending_approval"
            save_session(instance_root, session)
        except Exception:
            pass

    def _clear_session_pending(self, instance_root: Path) -> None:
        try:
            from workspace_execution.session.store import load_session, save_session

            session = load_session(instance_root)
            if session.execution_status == "pending_approval":
                session.execution_status = "active"
            save_session(instance_root, session)
        except Exception:
            pass
