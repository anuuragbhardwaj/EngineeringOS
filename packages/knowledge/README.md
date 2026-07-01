# Knowledge Platform

EngineeringOS accumulates **engineering knowledge** — not chat history.

## Philosophy

- Knowledge is durable, explainable, and traceable
- Every record has origin, owner, scope, confidence, type, reason, and source artifacts
- Knowledge flows upward only after validation (conversation → employee → project → workspace → company → framework)
- Framework knowledge ships with EngineeringOS and is immutable

## Hierarchy

```
Framework → Company → Workspace → Project → Employee → Conversation
```

Conversation knowledge is temporary. Framework knowledge is immutable.

## API

```python
from company_core.api import FrameworkAPI

api = FrameworkAPI()
api.knowledge.capture(title="...", content="...", origin="em", owner="em", reason="...")
api.knowledge.retrieve(project_id="my-app")
api.knowledge.promote(knowledge_id, target_scope="workspace")
```

## CLI

| Command | Purpose |
|---------|---------|
| `knowledge status` | Platform status |
| `knowledge search` | Search knowledge |
| `knowledge explain` | Traceability and relations |
| `knowledge graph` | Relationship graph |
| `knowledge validate` | Pre-promotion validation |
| `knowledge promote` | EM-controlled promotion |
| `knowledge history` | Promotion audit trail |
| `knowledge stats` | Aggregate statistics |
| `knowledge export` / `import` | Bundle portability |

## Persistence

```
.company/knowledge/
  framework/ company/ workspace/ project/ employee/ conversation/
  relationships/ indexes/ promotions/ versions/
```

## Orchestrator Integration

Before every employee execution, the Orchestrator retrieves relevant knowledge and injects it into prompts via `AssembledContext.knowledge_snippets`.

## Git Operations (extension points)

`GitKnowledgeExtension` prepares commit hints, release notes, and semantic version suggestions — no Git functionality implemented yet.
