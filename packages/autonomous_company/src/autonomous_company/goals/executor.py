"""Goal-based execution."""

from __future__ import annotations

import re
from pathlib import Path

from autonomous_company.policies.store import AutonomousStore
from autonomous_company.types import Goal, RunnerState, RunnerStatus, utc_now


class GoalExecutor:
    """Execute from high-level CEO goals."""

    def __init__(self, store: AutonomousStore | None = None) -> None:
        self._store = store or AutonomousStore()

    def create_goal(self, instance_root: Path, goal_text: str) -> Goal:
        goal = Goal(
            goal_id=self._store.new_goal_id(),
            title=goal_text[:80],
            description=goal_text,
            created_at=utc_now(),
            status="active",
        )
        self._store.save_goal(instance_root, goal)
        return goal

    def plan_from_goal(self, instance_root: Path, goal: Goal) -> dict:
        """Determine projects, employees, execution order from goal."""
        slug = re.sub(r"[^a-z0-9]+", "-", goal.title.lower()).strip("-")[:40] or "goal-project"
        return {
            "goal_id": goal.goal_id,
            "suggested_project_id": slug,
            "phases": ["idea", "requirements", "specification", "planning", "architecture", "implementation", "testing", "review", "documentation", "release"],
            "parallel_phases": ["implementation"],
            "employees": [
                "engineering-manager",
                "senior-product-manager",
                "senior-software-architect",
                "senior-backend-engineer",
                "senior-frontend-engineer",
                "senior-qa-engineer",
                "senior-code-reviewer",
                "documentation-engineer",
                "source-control-engineer",
            ],
            "artifacts": ["requirements.md", "architecture.md", "source_and_tests", "qa-report.md", "documentation-report.md"],
        }

    def bind_goal_to_project(self, instance_root: Path, goal_id: str, project_id: str) -> Goal:
        goal = self._store.get_goal(instance_root, goal_id)
        if goal is None:
            from autonomous_company.errors import GoalNotFoundError

            raise GoalNotFoundError(f"Goal not found: {goal_id}")
        goal.project_id = project_id
        self._store.save_goal(instance_root, goal)
        runner = self._store.load_runner_state(instance_root)
        runner.goal_id = goal_id
        runner.project_id = project_id
        self._store.save_runner_state(instance_root, runner)
        return goal

    def complete_goal(self, instance_root: Path, goal_id: str) -> Goal:
        goal = self._store.get_goal(instance_root, goal_id)
        if goal:
            goal.status = "completed"
            goal.completed_at = utc_now()
            self._store.save_goal(instance_root, goal)
        return goal
