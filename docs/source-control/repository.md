# Repository Guide

Repositories are discovered automatically:

```
Company → Workspace → Project → Repository
```

No manual paths required. The resolver walks from the active project root to find `.git`.

Validation checks: git initialized, remote configured, conflicts, detached HEAD, ownership, .gitignore.
