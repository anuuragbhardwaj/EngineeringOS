"""Pause execution and update session."""

from __future__ import annotations

from pathlib import Path

from workspace_execution.history.recorder import record_event
from workspace_execution.resolver.resolver import ContextResolver
from workspace_execution.session.store import load_session, save_session


def pause_execution(instance_root: Path, project_id: str | None = None) -> dict:
    resolver = ContextResolver()
    ctx = resolver.resolve(instance_root)
    pid = project_id or ctx.session.project_id
    if not pid:
        from workspace_execution.errors import NoActiveProjectError

        raise NoActiveProjectError("No active project to pause")

    from runtime_engine.factory import create_runtime
    from company_core.config.loader import discover_framework_root

    runtime = create_runtime(framework_root=discover_framework_root(instance_root))
    state = runtime.pause(pid)

    session = load_session(instance_root)
    session.project_id = pid
    session.execution_status = "paused"
    session.current_phase = state.current_phase_id
    save_session(instance_root, session)
    record_event(instance_root, event_type="pause", project_id=pid, phase_id=state.current_phase_id)
    return {"project_id": pid, "status": "paused", "phase_id": state.current_phase_id}
