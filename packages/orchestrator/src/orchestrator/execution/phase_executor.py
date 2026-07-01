"""Single-phase employee execution."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any

from orchestrator.approval.hooks import ApprovalHooks
from orchestrator.checkpoint.manager import CheckpointManager
from orchestrator.context.engine import ContextEngine
from orchestrator.conversation.router import ConversationRouter
from orchestrator.errors import ApprovalRequiredError, CheckpointPausedError
from orchestrator.history.recorder import HistoryRecorder
from orchestrator.policy.engine import PolicyEngine
from orchestrator.prompt_builder.builder import PromptBuilder
from orchestrator.scheduler.scheduler import ExecutionScheduler
from orchestrator.types import ExecutionPolicy, IAgentAdapter


class PhaseExecutor:
    """Executes all employee work for one workflow phase."""

    def __init__(
        self,
        adapter: IAgentAdapter,
        agent_registry: Any,
        context_engine: ContextEngine,
        prompt_builder: PromptBuilder,
        policy_engine: PolicyEngine,
        checkpoint_manager: CheckpointManager,
        conversation_router: ConversationRouter,
        history_recorder: HistoryRecorder,
        approval_hooks: ApprovalHooks,
        scheduler: ExecutionScheduler,
    ) -> None:
        self._adapter = adapter
        self._registry = agent_registry
        self._context = context_engine
        self._prompts = prompt_builder
        self._policies = policy_engine
        self._checkpoints = checkpoint_manager
        self._conversations = conversation_router
        self._history = history_recorder
        self._approval = approval_hooks
        self._scheduler = scheduler

    def execute(
        self,
        state: Any,
        workflow: Any,
        *,
        publish_event: callable | None = None,
    ) -> Any:
        from runtime_engine.types import (
            AdapterStatus,
            ArtifactRecord,
            ArtifactRef,
            InvocationContext,
            PhaseStatus,
            ProjectStatus,
        )

        phase_id = state.current_phase_id
        phase = workflow.phase_by_id(phase_id)
        if phase is None:
            return state

        orchestrator_desc = self._registry.resolve_orchestrator(workflow)
        specialist = self._registry.resolve_primary(phase_id, workflow)
        if specialist is None:
            return state

        policy = self._policies.resolve(phase_id, phase.gate.id)
        approval_key = self._approval.approval_key(state.project_id, phase.gate.id)

        if policy.approval_required:
            self._approval.request(approval_key)
            if not self._approval.is_approved(approval_key):
                checkpoint = self._checkpoints.create(
                    state.project_id,
                    phase_id,
                    specialist.agent_id,
                    {"reason": "approval_required", "gate_id": phase.gate.id},
                )
                self._checkpoints.pause(checkpoint.checkpoint_id)
                state.status = ProjectStatus.PAUSED
                if publish_event:
                    publish_event("PipelinePaused", {"phase_id": phase_id, "gate_id": phase.gate.id})
                raise ApprovalRequiredError(f"Approval required for gate {phase.gate.id}")

        checkpoint = self._checkpoints.create(
            state.project_id, phase_id, specialist.agent_id
        )

        state.phase_status[phase_id] = PhaseStatus.IN_PROGRESS
        state.execution.active_agent_id = orchestrator_desc.agent_id
        state.execution.last_invocation_at = datetime.utcnow()
        state.execution.invocation_count += 1

        if publish_event:
            publish_event(
                "AgentInvoked",
                {
                    "agent_id": orchestrator_desc.agent_id,
                    "phase_id": phase_id,
                    "adapter_status": AdapterStatus.DELEGATED.value,
                    "delegating_to": specialist.agent_id,
                },
            )

        workflow_state = {
            "current_phase_id": state.current_phase_id,
            "phase_status": {k: v.value for k, v in state.phase_status.items()},
            "gate_strikes": dict(state.gate_strikes),
        }

        plans = self._scheduler.plan_phase(
            orchestrator=orchestrator_desc,
            specialist=specialist,
            phase=phase,
        )

        for plan in plans:
            for artifact_name in plan.deliverables:
                self._execute_artifact(
                    state=state,
                    workflow=workflow,
                    phase=phase,
                    orchestrator_desc=orchestrator_desc,
                    specialist=specialist,
                    artifact_name=artifact_name,
                    policy=policy,
                    checkpoint_id=checkpoint.checkpoint_id,
                    workflow_state=workflow_state,
                    publish_event=publish_event,
                    plan_template=plan.delegation_template,
                )

        if workflow.artifacts.orchestration.required:
            self._execute_artifact(
                state=state,
                workflow=workflow,
                phase=phase,
                orchestrator_desc=orchestrator_desc,
                specialist=orchestrator_desc,
                artifact_name=workflow.artifacts.orchestration.name,
                policy=policy,
                checkpoint_id=checkpoint.checkpoint_id,
                workflow_state=workflow_state,
                publish_event=publish_event,
                plan_template="EM maintains {artifact}",
                orchestration_path=workflow.artifacts.orchestration.path,
            )

        self._checkpoints.complete(checkpoint.checkpoint_id)
        state.updated_at = datetime.utcnow()
        return state

    def _execute_artifact(
        self,
        *,
        state: Any,
        workflow: Any,
        phase: Any,
        orchestrator_desc: Any,
        specialist: Any,
        artifact_name: str,
        policy: ExecutionPolicy,
        checkpoint_id: str,
        workflow_state: dict,
        publish_event: callable | None,
        plan_template: str,
        orchestration_path: str | None = None,
    ) -> None:
        from runtime_engine.types import ArtifactRecord, ArtifactRef, InvocationContext

        phase_id = state.current_phase_id
        delegation_brief = plan_template.format(
            phase_name=phase.name,
            role=specialist.role,
            artifact=artifact_name,
        )

        conversation_id = self._conversations.resolve(
            state.project_id, specialist.agent_id, phase_id
        )

        assembled = self._context.assemble(
            project_id=state.project_id,
            phase_id=phase_id,
            employee_id=specialist.agent_id,
            employee_role=specialist.role,
            artifact_root=state.artifact_root,
            project_metadata=state.metadata,
            workflow_state=workflow_state,
            required_inputs=list(specialist.expected_inputs),
            deliverable=artifact_name,
            execution_history=list(state.execution.history),
            mcp_evidence=state.metadata.get("mcp_evidence", {}),
            conversation_id=conversation_id,
        )
        assembled = self._context.compress(assembled, policy.context_max_chars)

        assembled_prompt = self._prompts.build(
            assembled,
            getattr(specialist, "prompt_path", None),
            delegation_brief,
        )

        invocation = InvocationContext(
            project_id=state.project_id,
            phase_id=phase_id,
            artifact_root=state.artifact_root,
            required_inputs=[
                ArtifactRef(name=n, path=n, owner_agent=None)
                for n in specialist.expected_inputs
            ],
            deliverable=artifact_name,
            delegation_brief=assembled_prompt,
            metadata={
                **state.metadata,
                "assembled_prompt": assembled_prompt,
                "execution_policy": policy.name,
                "checkpoint_id": checkpoint_id,
                "conversation_id": conversation_id,
            },
        )

        attempt = 0
        result = None
        start = time.perf_counter()
        while True:
            result = self._adapter.invoke(specialist, invocation)
            failed = result.status.value == "failed"
            if not self._policies.should_retry(policy, attempt, failed):
                break
            attempt += 1

        duration_ms = (time.perf_counter() - start) * 1000
        rel_path = orchestration_path or artifact_name

        state.artifact_index[artifact_name] = ArtifactRecord(
            name=artifact_name,
            path=rel_path,
            owner_agent=specialist.agent_id,
            last_validated_at=None,
            approved=False,
        )

        if publish_event:
            publish_event(
                "ArtifactCreated",
                {
                    "artifact_name": artifact_name,
                    "phase_id": phase_id,
                    "agent_id": specialist.agent_id,
                    "delegated_by": orchestrator_desc.agent_id,
                },
            )

        state.execution.history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "orchestrator": orchestrator_desc.agent_id,
                "specialist": specialist.agent_id,
                "phase_id": phase_id,
                "artifact": artifact_name,
                "status": result.status.value,
                "provider_id": result.metadata.get("provider_id"),
                "policy": policy.name,
                "checkpoint_id": checkpoint_id,
                "conversation_id": conversation_id,
            }
        )

        self._history.record(
            project_id=state.project_id,
            employee_id=specialist.agent_id,
            orchestrator_id=orchestrator_desc.agent_id,
            phase_id=phase_id,
            provider_id=result.metadata.get("provider_id"),
            duration_ms=duration_ms,
            input_artifacts=list(specialist.expected_inputs),
            output_artifacts=[artifact_name],
            status=result.status.value,
            retry_count=attempt,
            policy=policy.name,
            checkpoint_id=checkpoint_id,
        )
