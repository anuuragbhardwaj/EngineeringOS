# Source Control Platform

Repository management owned by the **Source Control Engineer** employee.

## Philosophy

- Source control is a first-class engineering discipline
- Repository discovered automatically from execution context
- Git abstracted behind provider interfaces
- EM approval required for commit, push, and release

## API

```python
api.source_control.resolve()
api.source_control.status()
api.source_control.generate_commit()
api.source_control.approve("commit")
api.source_control.commit()
api.source_control.release()
```

## CLI

```bash
engineeringos repo status
engineeringos repo validate
engineeringos repo approve commit
engineeringos repo commit
engineeringos repo push
engineeringos repo release
engineeringos repo doctor
```

## Providers

| Provider | Status |
|----------|--------|
| Git | Implemented (default) |
| GitHub | Extension point |
| GitLab | Extension point |
| Azure DevOps | Extension point |
| Bitbucket | Extension point |

## Employee

`source-control-engineer` — registered in `runtime/employee-registry.yaml`
