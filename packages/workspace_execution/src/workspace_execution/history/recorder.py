"""Execution history recorder."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml

from workspace_execution.session.store import company_paths, ensure_company_dirs


def record_event(
    instance_root: Path,
    *,
    event_type: str,
    project_id: str | None = None,
    workspace_id: str | None = None,
    phase_id: str | None = None,
    employee_id: str | None = None,
    provider_id: str | None = None,
    command: str | None = None,
    status: str | None = None,
    detail: str | None = None,
) -> dict:
    ensure_company_dirs(instance_root)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "project_id": project_id,
        "workspace_id": workspace_id,
        "phase_id": phase_id,
        "employee_id": employee_id,
        "provider_id": provider_id,
        "command": command,
        "status": status,
        "detail": detail,
    }
    path = company_paths(instance_root)["history"] / "execution.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(yaml.safe_dump(entry, default_flow_style=True).replace("\n", " ").strip() + "\n")
    return entry


def load_history(
    instance_root: Path,
    *,
    project_id: str | None = None,
    event_type: str | None = None,
    limit: int = 100,
) -> list[dict]:
    path = company_paths(instance_root)["history"] / "execution.jsonl"
    if not path.is_file():
        return []
    entries: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entry = yaml.safe_load(line)
        except yaml.YAMLError:
            continue
        if not isinstance(entry, dict):
            continue
        if project_id and entry.get("project_id") != project_id:
            continue
        if event_type and entry.get("event_type") != event_type:
            continue
        entries.append(entry)
    return entries[-limit:]
