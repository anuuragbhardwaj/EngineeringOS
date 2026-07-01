"""Engineering Manager approval for source control operations."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml

from source_control.errors import ApprovalRequiredError
from source_control.types import ApprovalAction, ApprovalRecord

APPROVAL_DIR = Path(".company") / "source_control"
APPROVAL_FILE = APPROVAL_DIR / "approvals.yaml"


class SourceControlApproval:
    """EM owns approval — no automatic commits without approval."""

    def _path(self, instance_root: Path) -> Path:
        return instance_root / APPROVAL_FILE

    def _load(self, instance_root: Path) -> dict:
        path = self._path(instance_root)
        if not path.is_file():
            return {}
        with path.open(encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def _save(self, instance_root: Path, data: dict) -> None:
        path = self._path(instance_root)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(data, handle, sort_keys=False)

    def approval_key(self, project_id: str, action: str) -> str:
        return f"{project_id}:{action}"

    def request(self, instance_root: Path, project_id: str, action: str, reason: str = "") -> ApprovalRecord:
        data = self._load(instance_root)
        key = self.approval_key(project_id, action)
        record = ApprovalRecord(
            action=action,
            project_id=project_id,
            approved=False,
            reason=reason,
            timestamp=datetime.utcnow().isoformat(),
        )
        data[key] = record.__dict__
        self._save(instance_root, data)
        return record

    def approve(
        self,
        instance_root: Path,
        project_id: str,
        action: str,
        *,
        approved_by: str = "engineering-manager",
        reason: str = "",
    ) -> ApprovalRecord:
        data = self._load(instance_root)
        key = self.approval_key(project_id, action)
        record = ApprovalRecord(
            action=action,
            project_id=project_id,
            approved=True,
            approved_by=approved_by,
            reason=reason,
            timestamp=datetime.utcnow().isoformat(),
        )
        data[key] = record.__dict__
        self._save(instance_root, data)
        return record

    def is_approved(self, instance_root: Path, project_id: str, action: str) -> bool:
        data = self._load(instance_root)
        key = self.approval_key(project_id, action)
        entry = data.get(key)
        if entry is None:
            return False
        return bool(entry.get("approved", False))

    def require(self, instance_root: Path, project_id: str, action: str) -> None:
        if not self.is_approved(instance_root, project_id, action):
            self.request(instance_root, project_id, action)
            raise ApprovalRequiredError(
                f"Engineering Manager approval required for {action} on project {project_id}. "
                f"Approve via api.source_control.approve('{action}')."
            )

    def reject(
        self,
        instance_root: Path,
        project_id: str,
        action: str,
        reason: str = "",
    ) -> ApprovalRecord:
        data = self._load(instance_root)
        key = self.approval_key(project_id, action)
        record = ApprovalRecord(
            action=action,
            project_id=project_id,
            approved=False,
            reason=reason,
            timestamp=datetime.utcnow().isoformat(),
        )
        data[key] = record.__dict__
        self._save(instance_root, data)
        return record
