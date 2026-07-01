# Installation & Lifecycle Platform

## Installation

```bash
pip install -e .
engineeringos doctor
```

EngineeringOS installs as a Python package. Framework assets remain in the install location.

## Company Generation

```bash
engineeringos init ./my-company --yes --name "My Company" --id my-co
```

Generated assets:
- `company.yaml` — references installed framework
- `workspaces/`
- `docs/`
- `README.md`

Never copied: `packages/`, employees, runtime, orchestrator.

## Workspaces

```bash
engineeringos workspace create default
engineeringos workspace list
engineeringos workspace validate default
```

## Projects

```bash
engineeringos project create --yes --name "App" --template fullstack
engineeringos project list
engineeringos project clone ./existing --name "copy"
```

## Upgrade & Migration

```bash
engineeringos upgrade --plan
engineeringos migrate --dry-run
engineeringos repair
```

User modifications are never overwritten automatically.

## Template Profiles

`prototype`, `production`, `cli`, `api`, `frontend`, `backend`, `fullstack`, `library`, `package`, `plugin`, `agent`

See `packages/company_lifecycle/templates_catalog/catalog.yaml`.
