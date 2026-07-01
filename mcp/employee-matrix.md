# Employee × MCP Capability Matrix

**Authority:** `mcp/registry.yaml` + `mcp/capabilities.yaml`  
**Version:** 1.1.0  
**Date:** 2026-07-01

## Legend

| Symbol | Meaning |
|--------|---------|
| **R** | Required capability for this role |
| **O** | Optional — use when task benefits |
| **—** | Never used by this role |
| **FB** | Fallback when primary unavailable |

## Employee Capability Summary

| Employee | Required Capabilities | Optional Capabilities |
|----------|----------------------|----------------------|
| Engineering Manager | — | structured-reasoning, documentation-lookup, web-search, repository-hosting, team-notification, incident-management |
| Senior Product Manager | — | web-search, semantic-search, research-synthesis, issue-tracking, documentation-wiki |
| Senior Business Analyst | — | structured-reasoning, web-search, web-scraping, web-fetch, documentation-wiki |
| Senior Software Planner | **structured-reasoning** | documentation-lookup, issue-tracking |
| Senior Software Architect | **documentation-lookup** | structured-reasoning, web-fetch, graph-database, infrastructure-as-code |
| Senior Backend Engineer | **documentation-lookup** | version-control, sql-database, shell-execution, repository-hosting, error-tracking |
| Senior Frontend Engineer | **documentation-lookup** | browser-automation, shell-execution, version-control |
| Senior QA Engineer | — | browser-automation, documentation-lookup, structured-reasoning, llm-evaluation, static-analysis |
| Senior Code Reviewer | — | documentation-lookup, diff-inspection, static-analysis, secret-scanning |
| Documentation Engineer | **documentation-lookup** | structured-reasoning |

---

## Full Matrix

| MCP / Capability | EM | PM | BA | Planner | Architect | Backend | Frontend | QA | Reviewer | DocEng |
|------------------|:--:|:--:|:--:|:-------:|:---------:|:-------:|:--------:|:--:|:--------:|:------:|
| **structured-reasoning** | O | — | O | **R** | O | — | — | O | — | O |
| **documentation-lookup** | O | — | — | O | **R** | **R** | **R** | O | O | **R** |
| **web-search** | O | O | O | — | — | — | — | — | — |
| **web-scraping** | — | — | O | — | — | — | — | — | — |
| **web-fetch** | — | — | O | — | O | — | — | — | — |
| **issue-tracking** | — | O | — | O | — | — | — | — | — |
| **version-control** | O | — | — | — | — | O | O | — | O |
| **repository-hosting** | O | — | — | — | — | O | — | — | O |
| **diff-inspection** | — | — | — | — | — | O | — | — | O |
| **browser-automation** | — | — | — | — | — | — | O | O | — |
| **shell-execution** | — | — | — | — | — | O | O | O | — |
| **sql-database** | — | — | — | — | O | O | — | — | — |
| **graph-database** | — | — | — | — | O | O | — | — | — |
| **llm-evaluation** | — | — | — | — | — | — | — | O | — |
| **static-analysis** | — | — | — | — | — | — | — | O | O |
| **secret-scanning** | — | — | — | — | — | — | — | — | O |
| **team-notification** | O | — | — | — | — | — | — | — | — |
| **error-tracking** | O | — | — | — | — | O | — | O | — |
| filesystem | — | — | — | — | — | O | O | O | — |
| sequential-thinking | O | — | O | **R** | O | — | — | O | — |
| context7 | O | — | — | O | **R** | **R** | **R** | O | O |
| git | O | — | — | — | — | O | O | — | O |
| github | O | — | — | — | — | O | — | — | O |
| playwright | — | — | — | — | — | — | O | O | — |
| tavily / exa / firecrawl | O | O | O | — | — | — | — | — | — |
| sqlite / postgresql / mysql / neo4j | — | — | — | — | O | O | — | — | — |
| docker / aws / k8s / terraform | — | — | — | — | O | O | — | — | — |
| slack / notion / jira / linear | O | O | O | O | — | — | — | — | — |
| promptfoo / deepeval / ragas | — | — | — | — | — | — | — | O | — |
| semgrep / gitguardian | — | — | — | — | — | — | — | O | O |
| sentry / grafana / prometheus | O | — | — | — | — | O | — | O | — |

---

## Evidence Requirements by Employee

| Employee | Phase | Required Evidence |
|----------|-------|-------------------|
| Planner | Planning (G3) | `structured-reasoning` completion footer in `tasks.md` |
| Architect | Architecture (G4) | `documentation-lookup` references in `architecture.md` |
| Backend / Frontend | Implementation (G5) | Context7 library IDs for non-obvious APIs (on request) |
| QA | Testing (G6) | `browser-automation` evidence if E2E via Playwright |
| Documentation Engineer | Documentation (G8) | `documentation-lookup` when library/API claims; or reduced confidence documented |
| All others | — | None mandatory unless EM requests |

---

## Fallback Assignments

| Employee | Primary Unavailable | Fallback Action |
|----------|--------------------|-----------------|
| Planner | structured-reasoning | **STOP** — cannot pass G3 |
| Architect | documentation-lookup | web-fetch for public docs; document limitation |
| Backend/Frontend | documentation-lookup | STOP for framework APIs; use training data only with EM risk acceptance |
| QA | browser-automation | Shell-based tests; document gap in qa-report.md |
| Documentation Engineer | documentation-lookup | Continue with reduced confidence in documentation-report.md |
| EM | any optional | Proceed without MCP; log in pipeline-status.md |

See [selection-policy.md](./selection-policy.md) for full rules.
