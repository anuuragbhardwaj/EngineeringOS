# Template Guide

Templates are versioned profiles in `packages/company_lifecycle/templates_catalog/catalog.yaml`.

## Profiles

| Profile | Use case |
|---------|----------|
| `prototype` | Minimal scaffold |
| `production` | Standard project with docs |
| `cli` | CLI application |
| `api` | API service |
| `frontend` | Frontend app |
| `backend` | Backend service |
| `fullstack` | Full-stack app |
| `library` | Reusable library |
| `package` | Python package |
| `plugin` | EngineeringOS plugin |
| `agent` | Custom employee agent |

## Usage

```bash
engineeringos project create --yes --name "API" --template api
```

Templates are replaceable and upgradeable without modifying the framework.
