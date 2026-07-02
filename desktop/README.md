# EngineeringOS Desktop

FireRed-inspired visualization layer for the autonomous EngineeringOS runtime.

**The Desktop renders. The runtime decides.**

## Architecture

```
Desktop (Electron + React + PixiJS)
        ↓ WebSocket / HTTP
Desktop Bridge (FastAPI)
        ↓ in-process
SimulationAPI → CompanyDashboard → Runtime
```

No business logic lives in the Desktop. Every pixel corresponds to a real runtime event.

## Phase 1 (this release)

- Electron desktop shell
- FastAPI WebSocket bridge
- Event client with live subscription
- Engineering office (PixiJS)
- Employee sprites with state-driven visuals
- Top HUD (company health, energy, knowledge, time)
- Right sidebar (project, decision, employees, departments, capability XP)
- Bottom live timeline
- Bottom navigation

## Quick Start

### 1. Install Python bridge dependencies

From the `engineeringos` repo root:

```bash
pip install -e ".[desktop]"
```

### 2. Start the bridge (from `engineeringos` root)

```bash
python -m desktop.bridge.run --port 9477
```

### 3. Install and run the Desktop app

```bash
cd desktop/app
npm install
npm run dev
```

For Electron window:

```bash
npm run electron:dev
```

### 4. Trigger a project (optional)

With the bridge running:

```bash
curl -X POST http://127.0.0.1:9477/projects/run \
  -H "Content-Type: application/json" \
  -d '{"objective": "Build an OCR document processing platform", "risk": 0.3, "project_id": "demo-1"}'
```

Watch the office come alive from real runtime events.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /snapshot` | Full company state |
| `GET /employees` | Employee snapshots |
| `GET /departments` | Department utilization |
| `GET /metrics` | Company metrics |
| `GET /timeline` | Event history |
| `WS /ws/events` | Live event stream + initial snapshot |
| `POST /projects/run` | Run a project through Intelligence Core |

## Rules

- Never fake progress
- Never invent employee state
- Never duplicate runtime logic
- If the runtime stops, the office stops

## Roadmap

- **Phase 2**: Animations, Knowledge Library, Capability XP effects, Metrics view, Timeline replay
- **Phase 3**: Multiple rooms, camera zoom, notifications, Project flow visualization
