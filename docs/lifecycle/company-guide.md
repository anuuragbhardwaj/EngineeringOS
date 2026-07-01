# Company Guide

## Create a company

```bash
engineeringos init ./my-company --yes \
  --name "My Company" \
  --id my-co \
  --editor cursor \
  --ai-provider cursor \
  --git --github
```

## What is generated

| Asset | Owner |
|-------|-------|
| `company.yaml` | Company |
| `workspaces/` | Company |
| `docs/` | Company |
| `README.md` | Company |

Framework packages, employees, runtime, and orchestrator remain in the **installed** EngineeringOS location.

## Open and validate

```bash
cd my-company
engineeringos open
engineeringos doctor
engineeringos validate
engineeringos repair
```

## Upgrade

```bash
engineeringos upgrade --plan
engineeringos upgrade
engineeringos migrate --dry-run
```

User modifications are never overwritten automatically.
