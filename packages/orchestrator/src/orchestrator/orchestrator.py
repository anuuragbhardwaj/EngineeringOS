"""EngineeringOS Orchestrator — operational brain."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from orchestrator.approval.hooks import ApprovalHooks
from orchestrator.checkpoint.manager import CheckpointManager
from orchestrator.context.engine import ContextEngine
from orchestrator.conversation.router import ConversationRouter
from orchestrator.execution.phase_executor import PhaseExecutor
from orchestrator.execution.pipeline_executor import PipelineExecutor
from orchestrator.history.recorder import HistoryRecorder
from orchestrator.policy.engine import PolicyEngine
from orchestrator.prompt_builder.builder import PromptBuilder
from orchestrator.scheduler.scheduler import ExecutionScheduler
from orchestrator.types import IAgentAdapter, LifecycleCallbacks


class Orchestrator:
    """Central intelligence layer — sequences employees, assembles context, never executes AI."""

    def __init__(
        self,
        adapter: IAgentAdapter,
        agent_registry: Any,
        framework_root: Path,
        policies_path: Path,
    ) -> None:
        self._adapter = adapter
        self._registry = agent_registry
        self._context = ContextEngine()
        self._prompts = PromptBuilder(framework_root)
        self._policies = PolicyEngine(policies_path)
        self._checkpoints = CheckpointManager()
        self._conversations = ConversationRouter()
        self._history = HistoryRecorder()
        self._approval = ApprovalHooks()
        self._scheduler = ExecutionScheduler()

        self._phase_executor = PhaseExecutor(
            adapter=adapter,
            agent_registry=agent_registry,
            context_engine=self._context,
            prompt_builder=self._prompts,
            policy_engine=self._policies,
            checkpoint_manager=self._checkpoints,
            conversation_router=self._conversations,
            history_recorder=self._history,
            approval_hooks=self._approval,
            scheduler=self._scheduler,
        )
        self._pipeline = PipelineExecutor(self._phase_executor)

    def execute_phase(
        self,
        state: Any,
        workflow: Any,
        *,
        publish_event: callable | None = None,
    ) -> Any:
        return self._phase_executor.execute(state, workflow, publish_event=publish_event)

    def execute_planning_pipeline(
        self,
        state: Any,
        workflow: Any,
        stop_after_phase: str,
        lifecycle: LifecycleCallbacks,
    ) -> Any:
        return self._pipeline.execute_planning_pipeline(
            state, workflow, stop_after_phase, lifecycle
        )

    def approve(self, project_id: str, gate_id: str) -> None:
        self._approval.approve(self._approval.approval_key(project_id, gate_id))

    def get_checkpoints(self, project_id: str) -> list:
        return self._checkpoints.list_history(project_id)

    def get_execution_history(self, project_id: str, runtime_history: list) -> list:
        return self._history.filter_project(project_id, runtime_history)

    def reset_conversation(self, project_id: str, employee_id: str, phase_id: str) -> str:
        return self._conversations.reset(project_id, employee_id, phase_id)

    @property
    def approval_hooks(self) -> ApprovalHooks:
        return self._approval
