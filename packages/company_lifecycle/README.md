# EngineeringOS Installation & Lifecycle Platform

Operational lifecycle layer for installable EngineeringOS — generates user-owned companies, workspaces, and projects.

## Responsibilities

| Module | Purpose |
|--------|---------|
| `installation/` | Detect installed framework |
| `company/` | Generate companies, session context |
| `workspace/` | Workspace create/list/archive/remove |
| `project/` | Project scaffold/clone/archive |
| `templates/` | Versioned template catalog |
| `validation/` | Doctor, validate, repair |
| `upgrade/` | Upgrade and migration planning |
| `filesystem/boundaries` | Ownership enforcement |

## Philosophy

- Framework is **installed** (`pip install -e .`)
- Companies are **generated** (user-owned assets only)
- Framework source is **never copied** into companies
- Companies reference framework via `framework.install_path`

## CLI

```bash
engineeringos init --yes --name "Acme" --id acme
engineeringos open
engineeringos workspace create team-a
engineeringos project create --yes --name "App" --template production
engineeringos doctor
engineeringos repair
engineeringos upgrade --plan
engineeringos migrate --dry-run
```

## Testing

```bash
pytest tests/company_lifecycle/ -q
```
