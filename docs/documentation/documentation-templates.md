# Documentation Templates

**Version:** 1.0.0  
**Date:** 2026-07-01

Style authority: [handbook/documentation/](../../handbook/documentation/)

---

## Template Selection

| Project type | Templates to generate |
|--------------|----------------------|
| All (default) | README.md, documentation-report.md |
| Versioned release | + CHANGELOG.md |
| Public API | + API.md |
| Multi-component | + ARCHITECTURE.md |
| Contributor-facing | + CONTRIBUTING.md |
| Deployed service | + INSTALLATION.md or SETUP.md, USAGE.md |
| Release event | + RELEASE_NOTES.md |

---

## README.md Template

```markdown
# [Project Name]

[One-line description from idea.md or requirements.md]

## Overview

[2–4 sentences: problem, solution, audience — from requirements.md]

## Features

- [Must-have from spec.md — FR-* reference in report only]

## Quick Start

\`\`\`bash
# Commands from architecture.md / tasks.md verify
[install command]
[run command]
\`\`\`

## Documentation

| Document | Description |
|----------|-------------|
| [INSTALLATION.md](./INSTALLATION.md) | Full setup |
| [USAGE.md](./USAGE.md) | Usage guide |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System design |
| [API.md](./API.md) | API reference |

## Development

See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

[SPDX or TBD from release.md]
```

---

## ARCHITECTURE.md Template

See [architecture-style.md](../../handbook/documentation/architecture-style.md).

```markdown
# Architecture — [Project Name]

**Version:** [from release or tag]  
**Last updated:** [date]

## Overview

[From project architecture.md — distilled]

## System Context

\`\`\`mermaid
flowchart LR
  [components from architecture.md]
\`\`\`

## Components

| Component | Responsibility | Location |
|-----------|----------------|----------|

## Data Model

[From architecture.md schema section]

## Security

[From architecture.md security section]

## Deployment

[High-level — link INSTALLATION.md]

## References

- Project design: [architecture.md](./projects/.../architecture.md) (internal path if applicable)
```

---

## API.md Template

See [api-style.md](../../handbook/documentation/api-style.md).

```markdown
# API Reference — [Project Name]

**Base URL:** [from architecture.md]  
**Auth:** [scheme]

## Conventions

[Pagination, errors, versioning]

## Endpoints

### `[METHOD] [path]`

[Description]

**Request / Response / Errors** — per api-style.md

## Error Catalog

| Status | Meaning |
|--------|---------|
```

---

## CONTRIBUTING.md Template

```markdown
# Contributing

Thanks for contributing to [Project Name].

## Prerequisites

[From architecture.md tech stack]

## Setup

\`\`\`bash
[commands from tasks.md / architecture.md]
\`\`\`

## Tests

\`\`\`bash
[verify command from tasks.md]
\`\`\`

## Pull Requests

- [Branch convention]
- All tests pass
- Update documentation if behavior changes (Documentation Engineer handles release docs)

## Code of Conduct

[Link or TBD]
```

---

## INSTALLATION.md / SETUP.md Template

```markdown
# Installation

## Requirements

| Requirement | Version |
|-------------|---------|

## Steps

1. [Step — command from architecture.md]

## Verification

\`\`\`bash
[health check or smoke test command]
\`\`\`

## Troubleshooting

| Symptom | Fix |
|---------|-----|
```

---

## USAGE.md Template

```markdown
# Usage

## Basic usage

[Canonical example from spec.md acceptance criteria or source CLI --help]

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|

## Examples

### [Use case from spec.md user story]
```

---

## CHANGELOG.md Template

See [release-notes-style.md](../../handbook/documentation/release-notes-style.md).

---

## RELEASE_NOTES.md Template

```markdown
# Release Notes — [version]

**Date:** [YYYY-MM-DD]

## Summary

[From release.md]

## Highlights

-

## Breaking Changes

[Or "None"]

## Upgrade

[Steps from release.md]

## Known Issues

[From qa-report.md accepted deferrals only]
```

---

## documentation-report.md Template

**Primary gate artifact for Phase 8.**

```markdown
# Documentation Report — [Project Name]

**Date:** YYYY-MM-DD  
**Owner:** Documentation Engineer  
**Verdict:** PASS | FAIL | BLOCKED  
**Confidence:** high | medium | reduced

## Summary

[2–3 sentences: what was generated, overall quality]

## Generated Documents

| File | Purpose | Status |
|------|---------|--------|
| README.md | Landing page | created / updated / skipped |

## Traceability Matrix

| Document | Section | Claim | Source artifact | Source location |
|----------|---------|-------|-----------------|-----------------|
| README.md | Quick Start | `pip install x` | tasks.md | T-03 verify |

## Validation Results

| Check | Result | Notes |
|-------|--------|-------|
| Artifact consistency | pass/fail | |
| Implementation match | pass/fail | |
| Links valid | pass/fail | |
| Commands accurate | pass/fail/unverified | |
| Versions match | pass/fail | |
| Style compliance | pass/fail | |

See [documentation-validation.md](./documentation-validation.md).

## Gaps

| Gap | Reason | Action |
|-----|--------|--------|

## MCP Evidence

| Capability | MCP | Status | Notes |
|------------|-----|--------|-------|
| documentation-lookup | context7 | completed/skipped | |

## Handoff

Ready for EM G8 validation: yes/no
```

---

## docs/ Directory Convention

```
docs/
├── README.md          # Index of extended docs
├── guides/            # Optional deep dives
└── images/            # Screenshots (committed assets only)
```

---

## References

- [documentation-validation.md](./documentation-validation.md)
- [github-documentation.md](./github-documentation.md)
