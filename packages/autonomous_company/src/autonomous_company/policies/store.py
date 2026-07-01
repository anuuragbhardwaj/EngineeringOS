"""Persistent autonomous company state."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

import yaml

from autonomous_company.types import (
    ApprovalRequest,
    Blocker,
    Decision,
    ExecutionPolicy,
    Goal,
    RunnerState,
    utc_now,
)

AUTONOMOUS_DIR = Path(".company") / "autonomous"


def autonomous_paths(instance_root: Path) -> dict[str, Path]:
    base = instance_root / AUTONOMOUS_DIR
    return {
        "base": base,
        "state": base / "state.yaml",
        "goals": base / "goals.yaml",
        "policy": base / "policy.yaml",
        "approvals": base / "approvals.yaml",
        "decisions": base / "decisions.jsonl",
        "blockers": base / "blockers.jsonl",
        "checkpoints": base / "checkpoints",
    }


def ensure_dirs(instance_root: Path) -> None:
    for path in autonomous_paths(instance_root).values():
        path.mkdir(parents=True, exist_ok=True) if path.suffix != ".yaml" and path.suffix != ".jsonl" else path.parent.mkdir(parents=True, exist_ok=True)


class AutonomousStore:
    """Persist goals, decisions, blockers, runner state."""

    def load_runner_state(self, instance_root: Path) -> RunnerState:
        path = autonomous_paths(instance_root)["state"]
        if not path.is_file():
            return RunnerState()
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return RunnerState(
            status=data.get("status", "idle"),
            goal_id=data.get("goal_id"),
            project_id=data.get("project_id"),
            current_phase=data.get("current_phase"),
            retry_count=int(data.get("retry_count", 0)),
            started_at=data.get("started_at"),
            last_heartbeat=data.get("last_heartbeat"),
            stopped=bool(data.get("stopped", False)),
        )

    def save_runner_state(self, instance_root: Path, state: RunnerState) -> None:
        ensure_dirs(instance_root)
        path = autonomous_paths(instance_root)["state"]
        path.write_text(yaml.safe_dump(state.to_dict(), sort_keys=False), encoding="utf-8")

    def load_policy(self, instance_root: Path) -> ExecutionPolicy:
        path = autonomous_paths(instance_root)["policy"]
        if not path.is_file():
            return ExecutionPolicy()
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return ExecutionPolicy(
            max_retries=int(data.get("max_retries", 3)),
            retry_backoff_seconds=float(data.get("retry_backoff_seconds", 1.0)),
            checkpoint_interval_seconds=int(data.get("checkpoint_interval_seconds", 300)),
            max_execution_duration_seconds=int(data.get("max_execution_duration_seconds", 86400)),
            autonomous_depth=str(data.get("autonomous_depth", "pipeline")),
            auto_push=bool(data.get("auto_push", False)),
            night_mode=bool(data.get("night_mode", False)),
            cost_limit=data.get("cost_limit"),
            provider_priority=list(data.get("provider_priority") or []),
            approval_gates=list(data.get("approval_gates") or ["architecture", "implementation", "review", "commit"]),
        )

    def save_policy(self, instance_root: Path, policy: ExecutionPolicy) -> None:
        ensure_dirs(instance_root)
        path = autonomous_paths(instance_root)["policy"]
        path.write_text(yaml.safe_dump(policy.to_dict(), sort_keys=False), encoding="utf-8")

    def save_goal(self, instance_root: Path, goal: Goal) -> None:
        ensure_dirs(instance_root)
        path = autonomous_paths(instance_root)["goals"]
        goals = self.list_goals(instance_root)
        goals = [g for g in goals if g.goal_id != goal.goal_id]
        goals.append(goal)
        data = [g.to_dict() for g in goals]
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    def list_goals(self, instance_root: Path) -> list[Goal]:
        path = autonomous_paths(instance_root)["goals"]
        if not path.is_file():
            return []
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        return [Goal(**entry) for entry in data]

    def get_goal(self, instance_root: Path, goal_id: str) -> Goal | None:
        return next((g for g in self.list_goals(instance_root) if g.goal_id == goal_id), None)

    def new_goal_id(self) -> str:
        return f"goal-{uuid.uuid4().hex[:10]}"

    def record_decision(self, instance_root: Path, decision: Decision) -> None:
        ensure_dirs(instance_root)
        path = autonomous_paths(instance_root)["decisions"]
        if not decision.timestamp:
            decision.timestamp = utc_now()
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(decision.to_dict()) + "\n")

    def list_decisions(self, instance_root: Path, limit: int = 50) -> list[Decision]:
        path = autonomous_paths(instance_root)["decisions"]
        if not path.is_file():
            return []
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        decisions = []
        for line in lines[-limit:]:
            data = json.loads(line)
            decisions.append(Decision(**data))
        return decisions

    def record_blocker(self, instance_root: Path, blocker: Blocker) -> None:
        ensure_dirs(instance_root)
        path = autonomous_paths(instance_root)["blockers"]
        if not blocker.timestamp:
            blocker.timestamp = utc_now()
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(blocker.to_dict()) + "\n")

    def list_blockers(self, instance_root: Path, limit: int = 20) -> list[Blocker]:
        path = autonomous_paths(instance_root)["blockers"]
        if not path.is_file():
            return []
        blockers = []
        for line in path.read_text(encoding="utf-8").strip().splitlines()[-limit:]:
            data = json.loads(line)
            blockers.append(Blocker(**data))
        return blockers

    def save_approvals(self, instance_root: Path, approvals: dict) -> None:
        ensure_dirs(instance_root)
        path = autonomous_paths(instance_root)["approvals"]
        path.write_text(yaml.safe_dump(approvals, sort_keys=False), encoding="utf-8")

    def load_approvals(self, instance_root: Path) -> dict:
        path = autonomous_paths(instance_root)["approvals"]
        if not path.is_file():
            return {}
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
