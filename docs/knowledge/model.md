# Knowledge Model

Every `KnowledgeObject` requires:

| Field | Purpose |
|-------|---------|
| `origin` | Where knowledge came from |
| `owner` | Responsible party |
| `scope` | Hierarchy level |
| `confidence` | 0.0–1.0 trust score |
| `knowledge_type` | fact, decision, lesson, etc. |
| `reason` | Why it was captured |
| `source_artifacts` | Traceable files |
| `timestamp` | created_at / updated_at |

Types are extensible via `custom`.
