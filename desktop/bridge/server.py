"""FastAPI bridge: exposes CompanyDashboard over HTTP and WebSocket.

The bridge contains zero business logic. It forwards read-model calls and
event subscriptions from the Desktop to the in-process SimulationAPI.
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from company_core.api.framework import FrameworkAPI
from knowledge.intelligence import DecisionRequest

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared simulation instance (one company, one truth)
# ---------------------------------------------------------------------------

_api: FrameworkAPI | None = None
_sub_id: int | None = None
_ws_clients: set[WebSocket] = set()
_loop: asyncio.AbstractEventLoop | None = None


def _get_api() -> FrameworkAPI:
    global _api
    if _api is None:
        _api = FrameworkAPI()
    return _api


def _on_simulation_event(event) -> None:
    """Called from the simulation bus (sync). Fan-out to async WebSocket clients."""
    data = json.dumps({"kind": "event", "data": event.to_dict()})
    loop = _loop
    if loop is None or not loop.is_running():
        return
    for ws in list(_ws_clients):
        asyncio.run_coroutine_threadsafe(_safe_send(ws, data), loop)


async def _safe_send(ws: WebSocket, data: str) -> None:
    try:
        await ws.send_text(data)
    except Exception:
        _ws_clients.discard(ws)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _sub_id, _loop
    _loop = asyncio.get_running_loop()
    api = _get_api()
    _sub_id = api.simulation.subscribe_all(_on_simulation_event)
    logger.info("Subscribed to simulation event bus (id=%s)", _sub_id)
    yield
    if _sub_id is not None:
        api.simulation.unsubscribe(_sub_id)
        _sub_id = None
    _ws_clients.clear()
    _loop = None


app = FastAPI(
    title="EngineeringOS Desktop Bridge",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class RunProjectRequest(BaseModel):
    objective: str
    risk: float = Field(default=0.3, ge=0.0, le=1.0)
    capability_hint: str | None = None
    technology_stack: list[str] = Field(default_factory=list)
    project_id: str | None = None
    context: str = ""


# ---------------------------------------------------------------------------
# REST — read model (mirrors CompanyDashboard)
# ---------------------------------------------------------------------------


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "engineeringos-desktop-bridge"}


@app.get("/snapshot")
def snapshot() -> dict[str, Any]:
    return _get_api().simulation.snapshot()


@app.get("/employees")
def employees() -> list[dict[str, Any]]:
    return _get_api().simulation.employees()


@app.get("/departments")
def departments() -> list[dict[str, Any]]:
    return _get_api().simulation.departments()


@app.get("/metrics")
def metrics() -> dict[str, Any]:
    return _get_api().simulation.metrics()


@app.get("/capability-xp")
def capability_xp() -> list[dict[str, Any]]:
    return _get_api().simulation.capability_xp()


@app.get("/projects")
def projects() -> list[dict[str, Any]]:
    return _get_api().simulation.projects()


@app.get("/timeline")
def timeline(
    limit: int | None = None,
    project_id: str | None = None,
    since_sequence: int | None = None,
) -> list[dict[str, Any]]:
    events = _get_api().simulation.timeline(limit=limit, project_id=project_id)
    if since_sequence is not None:
        events = [e for e in events if e.get("sequence", 0) > since_sequence]
    return events


@app.get("/company")
def company_info() -> dict[str, Any]:
    from company_core.config.loader import discover_instance_root

    root = discover_instance_root()
    return {
        "name": "EngineeringOS",
        "instance_root": str(root) if root else None,
        "connected": True,
    }


@app.post("/projects/run")
def run_project(req: RunProjectRequest) -> dict[str, Any]:
    request = DecisionRequest(
        objective=req.objective,
        risk=req.risk,
        capability_hint=req.capability_hint,
        technology_stack=req.technology_stack,
        context=req.context,
    )
    result = _get_api().simulation.run_project(request, project_id=req.project_id)
    return {
        "success": result.success,
        "project_id": req.project_id,
        "decision": result.decision.to_dict() if hasattr(result.decision, "to_dict") else str(result.decision),
        "total_cost": result.total_cost,
        "total_duration_ms": result.total_duration_ms,
    }


# ---------------------------------------------------------------------------
# WebSocket — live event stream
# ---------------------------------------------------------------------------


@app.websocket("/ws/events")
async def ws_events(websocket: WebSocket) -> None:
    await websocket.accept()
    _ws_clients.add(websocket)

    # Send current snapshot on connect so the UI can render immediately.
    snapshot_data = _get_api().simulation.snapshot()
    await websocket.send_text(
        json.dumps({"kind": "snapshot", "data": snapshot_data})
    )

    try:
        while True:
            # Keep connection alive; client may send ping or replay commands later.
            msg = await websocket.receive_text()
            try:
                payload = json.loads(msg)
            except json.JSONDecodeError:
                continue
            if payload.get("type") == "ping":
                await websocket.send_text(json.dumps({"kind": "pong"}))
            elif payload.get("type") == "snapshot":
                snap = _get_api().simulation.snapshot()
                await websocket.send_text(
                    json.dumps({"kind": "snapshot", "data": snap})
                )
    except WebSocketDisconnect:
        pass
    finally:
        _ws_clients.discard(websocket)
