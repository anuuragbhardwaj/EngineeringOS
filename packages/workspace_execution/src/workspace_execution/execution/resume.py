"""Intelligent resume — restore context, pipeline, checkpoint."""

from __future__ import annotations

from pathlib import Path

from workspace_execution.history.recorder import record_event
from workspace_execution.resolver.resolver import ContextResolver
from workspace_execution.session.store import load_session, save_session


def resume_execution(instance_root: Path, project_id: str | None = None) -> dict:
    resolver = ContextResolver()
    ctx = resolver.resolve(instance_root)
    pid = project_id or ctx.session.project_id
    if not pid:
        from workspace_execution.errors import NoActiveProjectError

        raise NoActiveProjectError("No active project to resume")

    from runtime_engine.factory import create_runtime
    from company_core.config.loader import discover_framework_root

    runtime = create_runtime(framework_root=discover_framework_root(instance_root))

    if not runtime._store.exists(pid):  # noqa: SLF001
        from company_core.models.errors import ProjectNotFoundError

        raise ProjectNotFoundError(f"Project not found: {pid}")

    view = runtime.status(pid)
    session = load_session(instance_root)

    if session.execution_status == "pending_approval":
        return {
            "project_id": pid,
            "status": "pending_approval",
            "message": "Human approval required before resume",
        }

    if view.status.value == "PAUSED" or session.execution_status == "paused":
        state = runtime.resume(pid)
    elif session.execution_status in {"interrupted", "active", "blocked"}:
        stop = state_stop_phase(runtime, pid)
        state = runtime.execute_planning_pipeline(pid, stop_after_phase=stop)
    elif session.execution_status == "completed":
        return {"project_id": pid, "status": "completed", "message": "Pipeline already completed"}
    else:
        state = runtime.resume(pid)

    session.project_id = pid
    session.execution_status = "active"
    session.current_phase = state.current_phase_id
    session.pipeline = "planning"
    save_session(instance_root, session)
    record_event(
        instance_root,
        event_type="resume",
        project_id=pid,
        phase_id=state.current_phase_id,
        status="active",
    )
    resolver.sync_runtime(instance_root)
    return {
        "project_id": pid,
        "status": "active",
        "phase_id": state.current_phase_id,
        "resumed": True,
    }


def continue_execution(instance_root: Path) -> dict:
    """Continue from last active context — OS-style continue."""
    resolver = ContextResolver()
    ctx = resolver.resolve(instance_root)
    if not ctx.session.project_id:
        if ctx.session.workspace_id and ctx.session.recent_projects:
            resolver.set_project(ctx.session.recent_projects[0], instance_root)
            ctx = resolver.resolve(instance_root)
        else:
            return {"status": "idle", "message": "No project to continue — use engineeringos project use <id>"}
    return resume_execution(instance_root, ctx.session.project_id)


def detect_resume_points(instance_root: Path) -> list[dict]:
    resolver = ContextResolver()
    ctx = resolver.resolve(instance_root)
    points: list[dict] = []
    if ctx.session.execution_status == "paused":
        points.append({"type": "paused_pipeline", "project_id": ctx.session.project_id})
    if ctx.session.execution_status == "pending_approval":
        points.append({"type": "pending_approval", "project_id": ctx.session.project_id})
    if ctx.session.execution_status == "interrupted":
        points.append({"type": "interrupted", "project_id": ctx.session.project_id})
    if ctx.session.execution_status == "completed":
        points.append({"type": "completed", "project_id": ctx.session.project_id})
    return points


def state_stop_phase(runtime: object, project_id: str) -> str:
    try:
        state = runtime.load_project(project_id)
        return state.execution.pipeline_stop_phase or "architecture"
    except Exception:
        return "architecture"
