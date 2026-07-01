# Workspace Execution Platform

Context-aware execution layer — persistent sessions, active company/workspace/project, intelligent resume.

## Session location

Inside generated companies only:

```
.company/
  session/execution.yaml
  history/execution.jsonl
  recent/
  favorites/
  checkpoints/
```

## CLI

```bash
engineeringos open
engineeringos current
engineeringos status
engineeringos workspace use engineeringos
engineeringos project use memory-system
engineeringos continue
```

## Framework API

```python
api = FrameworkAPI()
api.context.current()
api.context.use_project("my-app")
api.context.status()
```
