"""Blocker detection."""

from __future__ import annotations

import uuid
from pathlib import Path

from autonomous_company.policies.store import AutonomousStore
from autonomous_company.types import Blocker, BlockerType, RunnerState


class BlockerDetector:
    """Detect recoverable and unrecoverable blockers."""

    def __init__(self, store: AutonomousStore | None = None) -> None:
        self._store = store or AutonomousStore()

    def detect(self, instance_root: Path, runner: RunnerState) -> list[Blocker]:
        blockers: list[Blocker] = []
        blockers.extend(self._session_blockers(instance_root))
        blockers.extend(self._runtime_blockers(instance_root, runner))
        blockers.extend(self._repository_blockers(instance_root))
        return blockers

    def has_blocking(self, blockers: list[Blocker]) -> bool:
        return any(not b.recoverable or b.blocker_type in {
            BlockerType.APPROVAL_REQUIRED.value,
            BlockerType.UNRECOVERABLE.value,
            BlockerType.CREDENTIALS_REQUIRED.value,
            BlockerType.SECURITY_POLICY.value,
            BlockerType.HUMAN_INPUT.value,
        } for b in blockers)

    def _session_blockers(self, instance_root: Path) -> list[Blocker]:
        blockers: list[Blocker] = []
        try:
            from workspace_execution.session.store import load_session

            session = load_session(instance_root)
            if session.execution_status == "pending_approval":
                blockers.append(self._make(
                    BlockerType.APPROVAL_REQUIRED,
                    "Engineering Manager approval required",
                    recoverable=True,
                    actionable="engineeringos approvals approve <gate>",
                    project_id=session.project_id,
                ))
        except Exception:
            pass
        return blockers

    def _runtime_blockers(self, instance_root: Path, runner: RunnerState) -> list[Blocker]:
        blockers: list[Blocker] = []
        if not runner.project_id:
            return blockers
        try:
            from runtime_engine.factory import create_runtime
            from company_core.config.loader import discover_framework_root

            runtime = create_runtime(framework_root=discover_framework_root(instance_root))
            if runtime._store.exists(runner.project_id):  # noqa: SLF001
                view = runtime.status(runner.project_id)
                if view.status.value == "BLOCKED":
                    blockers.append(self._make(
                        BlockerType.RUNTIME_FAILURE,
                        "Runtime reports project blocked",
                        recoverable=False,
                        project_id=runner.project_id,
                    ))
        except Exception as exc:
            blockers.append(self._make(
                BlockerType.RUNTIME_FAILURE,
                str(exc),
                recoverable=True,
                project_id=runner.project_id,
            ))
        return blockers

    def _repository_blockers(self, instance_root: Path) -> list[Blocker]:
        blockers: list[Blocker] = []
        try:
            from source_control.factory import create_source_control_platform

            sc = create_source_control_platform()
            report = sc.validate(instance_root)
            for issue in report.get("issues", []):
                if issue.get("severity") == "error" and issue.get("code") == "merge_conflicts":
                    blockers.append(self._make(
                        BlockerType.REPOSITORY_CONFLICT,
                        issue.get("message", "Repository conflict"),
                        recoverable=True,
                        actionable=issue.get("actionable", ""),
                    ))
        except Exception:
            pass
        return blockers

    def _make(
        self,
        blocker_type: BlockerType,
        message: str,
        *,
        recoverable: bool,
        actionable: str = "",
        project_id: str | None = None,
    ) -> Blocker:
        return Blocker(
            blocker_id=f"blk-{uuid.uuid4().hex[:8]}",
            blocker_type=blocker_type.value,
            message=message,
            recoverable=recoverable,
            actionable=actionable,
            project_id=project_id,
        )
