"""Unified status engine."""

from __future__ import annotations

from pathlib import Path

from company_core.config.loader import discover_framework_root, discover_instance_root
from workspace_execution.context.types import UnifiedStatus
from workspace_execution.execution.resume import detect_resume_points
from workspace_execution.resolver.resolver import ContextResolver


class StatusEngine:
    """Aggregates company, workspace, project, runtime, and MCP status."""

    def summarize(self, instance_root: Path | None = None) -> UnifiedStatus:
        resolver = ContextResolver()
        root = instance_root or discover_instance_root()
        ctx = resolver.sync_runtime(root) if root else resolver.resolve(None)

        pending_actions: list[str] = []
        pending_approvals: list[str] = []
        resume_points: list[str] = []
        recent_activity = list(ctx.session.recent_commands[:5])
        runtime_healthy = True
        mcp_healthy = True
        pipeline_progress = None
        current_phase = ctx.session.current_phase
        current_employee = ctx.session.current_employee

        if root:
            points = detect_resume_points(root)
            for point in points:
                resume_points.append(f"{point['type']}:{point.get('project_id', '')}")
                if point["type"] == "pending_approval":
                    pending_approvals.append(point.get("project_id", ""))

            if ctx.project:
                try:
                    from runtime_engine.factory import create_runtime

                    runtime = create_runtime(framework_root=discover_framework_root(root))
                    view = runtime.status(ctx.project.project_id)
                    current_phase = view.current_phase_id
                    current_employee = (view.metadata or {}).get("active_agent_id")
                    if view.blockers:
                        pending_actions.extend(view.blockers)
                        runtime_healthy = False
                    if view.current_gate_id:
                        pipeline_progress = f"phase={view.current_phase_id} gate={view.current_gate_id}"
                    else:
                        pipeline_progress = f"phase={view.current_phase_id}"
                except Exception:
                    runtime_healthy = False

            try:
                from mcp_platform.validator import validate_all

                framework = discover_framework_root(root)
                if framework:
                    results = validate_all(framework)
                    mcp_healthy = all(r.passed for r in results)
            except Exception:
                mcp_healthy = False

        return UnifiedStatus(
            company_id=ctx.company_id,
            workspace_id=ctx.session.workspace_id,
            project_id=ctx.session.project_id,
            current_phase=current_phase,
            current_employee=current_employee,
            pipeline_progress=pipeline_progress,
            execution_status=ctx.session.execution_status,
            runtime_healthy=runtime_healthy,
            mcp_healthy=mcp_healthy,
            pending_actions=pending_actions,
            pending_approvals=pending_approvals,
            resume_points=resume_points,
            recent_activity=recent_activity,
            message="EngineeringOS execution context active" if ctx.company_id else "No active company",
        )
