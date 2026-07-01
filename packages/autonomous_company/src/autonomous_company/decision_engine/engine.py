"""Autonomous decision engine."""

from __future__ import annotations

import uuid
from pathlib import Path

from autonomous_company.blockers.detector import BlockerDetector
from autonomous_company.policies.store import AutonomousStore
from autonomous_company.types import Decision, DecisionAction, ExecutionPolicy, RunnerState, utc_now


class DecisionEngine:
    """Determine continue, pause, retry, escalate — every decision is explainable."""

    def __init__(
        self,
        store: AutonomousStore | None = None,
        blockers: BlockerDetector | None = None,
    ) -> None:
        self._store = store or AutonomousStore()
        self._blockers = blockers or BlockerDetector(self._store)

    def decide(self, instance_root: Path, runner: RunnerState) -> Decision:
        policy = self._store.load_policy(instance_root)
        blockers = self._blockers.detect(instance_root, runner)

        if runner.stopped:
            return self._record(instance_root, DecisionAction.TERMINATE, "Runner stopped by user", runner)

        if self._blockers.has_blocking(blockers):
            blocker = blockers[0]
            if blocker.blocker_type == "approval_required":
                return self._record(
                    instance_root,
                    DecisionAction.WAIT,
                    f"Blocked: {blocker.message}",
                    runner,
                    {"blocker": blocker.to_dict()},
                )
            if not blocker.recoverable:
                return self._record(
                    instance_root,
                    DecisionAction.ESCALATE,
                    f"Unrecoverable: {blocker.message}",
                    runner,
                    {"blocker": blocker.to_dict()},
                )
            if runner.retry_count < policy.max_retries:
                return self._record(
                    instance_root,
                    DecisionAction.RETRY,
                    f"Recoverable blocker, retry {runner.retry_count + 1}/{policy.max_retries}",
                    runner,
                )
            return self._record(
                instance_root,
                DecisionAction.PAUSE,
                f"Max retries exceeded: {blocker.message}",
                runner,
            )

        if runner.status == "paused":
            return self._record(instance_root, DecisionAction.RESUME, "Runner paused — resuming", runner)

        knowledge_hint = self._knowledge_context(instance_root, runner)
        reason = "No blockers detected — continuing pipeline execution"
        if knowledge_hint:
            reason += f" (knowledge: {knowledge_hint[:80]})"

        return self._record(instance_root, DecisionAction.CONTINUE, reason, runner, {"knowledge": knowledge_hint})

    def _knowledge_context(self, instance_root: Path, runner: RunnerState) -> str:
        if not runner.project_id:
            return ""
        try:
            from knowledge.git_hooks.extension import GitKnowledgeExtension

            ext = GitKnowledgeExtension()
            hints = ext.commit_message_hints(instance_root, runner.project_id)
            return hints[0] if hints else ""
        except Exception:
            return ""

    def _record(
        self,
        instance_root: Path,
        action: DecisionAction,
        reason: str,
        runner: RunnerState,
        context: dict | None = None,
    ) -> Decision:
        decision = Decision(
            decision_id=f"dec-{uuid.uuid4().hex[:8]}",
            action=action.value,
            reason=reason,
            context=context or {},
            timestamp=utc_now(),
            project_id=runner.project_id,
        )
        self._store.record_decision(instance_root, decision)
        return decision
