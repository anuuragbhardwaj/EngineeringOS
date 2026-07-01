"""Human approval hooks."""

from __future__ import annotations

from orchestrator.errors import ApprovalRequiredError


class ApprovalHooks:
    """Runtime may pause; user approves; execution resumes."""

    def __init__(self) -> None:
        self._approvals: dict[str, bool] = {}

    def request(self, approval_key: str) -> None:
        self._approvals.setdefault(approval_key, False)

    def approve(self, approval_key: str) -> None:
        self._approvals[approval_key] = True

    def is_approved(self, approval_key: str) -> bool:
        return self._approvals.get(approval_key, True)

    def require(self, approval_key: str) -> None:
        if not self.is_approved(approval_key):
            raise ApprovalRequiredError(
                f"Approval required for {approval_key}. "
                "Call orchestrator.approve() to continue."
            )

    def approval_key(self, project_id: str, gate_id: str) -> str:
        return f"{project_id}:{gate_id}"
