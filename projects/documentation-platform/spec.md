# Specification — Documentation Platform

**Date:** 2026-07-01  
**Owner:** Senior Business Analyst

---

## Functional Requirements

### Employee & Roster

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-01 | Documentation Engineer agent exists | `.cursor/agents/documentation-engineer.md` with role, inputs, outputs, capabilities; no embedded writing rules |
| FR-02 | Employee references handbook only for writing | Prompt links `handbook/documentation/` and `handbook/documentation-standards.md` |
| FR-03 | Company handbook lists Documentation Engineer | Phase 8 owner in organization table |

### Handbook

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-04 | Master style guide | `handbook/documentation/documentation-style-guide.md` exists with voice, structure, accuracy rules |
| FR-05 | Specialized style guides | `github-style.md`, `architecture-style.md`, `api-style.md`, `release-notes-style.md` inherit master |
| FR-06 | Documentation standards | `handbook/documentation-standards.md` defines ownership, traceability, phase rules |
| FR-07 | Root index | `handbook/documentation-style-guide.md` points to master guide |

### SDLC Integration

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-08 | Documentation phase in workflow | Phase order 8 Documentation between Review and Release in `workflow.yaml` |
| FR-09 | Gate G8 Documentation | EM approves when `documentation-report.md` passes validation |
| FR-10 | Release requires G8 | `release` phase `entry_criteria` includes documentation gate for production work |
| FR-11 | Gate renumber | Release = G9; Closure = G10 |
| FR-12 | Phase artifact | `documentation-report.md` required in artifacts list |
| FR-13 | Human workflow mirror | `workflow-v1.md` reflects 11-phase pipeline |

### Platform Specifications

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-14 | Platform overview | `docs/documentation/documentation-platform.md` describes system, inputs, outputs |
| FR-15 | Validation spec | `docs/documentation/documentation-validation.md` with checklist |
| FR-16 | Templates | `docs/documentation/documentation-templates.md` with README, CHANGELOG, etc. |
| FR-17 | GitHub guide | `docs/documentation/github-documentation.md` covers repo standards |

### Documentation Engineer Behavior

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-18 | Consume project artifacts | Reads idea through release, pipeline-status, source, config, git history |
| FR-19 | Generate doc set per project type | At minimum README.md; others per templates |
| FR-20 | Never invent information | Missing data → document gap in report; do not fabricate |
| FR-21 | Validate generated docs | Run checklist from documentation-validation.md |
| FR-22 | Traceability matrix | `documentation-report.md` maps each doc section to source artifact |
| FR-23 | Handoff to EM for G8 | Report includes PASS/FAIL verdict |

### MCP

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-24 | Required capability | `documentation-lookup` when documenting frameworks/libraries/APIs |
| FR-25 | Optional capability | `structured-reasoning` for complex doc planning |
| FR-26 | MCP unavailable | Continue; record reduced confidence in report |

### Updates to Existing Artifacts

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-27 | `company-handbook.md` updated | New phase, employee, handbook index |
| FR-28 | `engineering-standards.md` updated | Artifact ownership, gates G8–G10 |
| FR-29 | `definition-of-done.md` updated | Phase 8 DoD; ship-ready includes documentation |
| FR-30 | Code Reviewer handoff | Routes to Documentation Engineer after G7 |
| FR-31 | EM orchestration table | Includes Phase 8 Documentation |
| FR-32 | MCP employee matrix | Documentation Engineer row added |

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | All new markdown must be GitHub-flavored and render correctly |
| NFR-02 | Handbook changes must not duplicate content across agent prompts |
| NFR-03 | Workflow version bumped to 1.1 |
| NFR-04 | Existing employee core responsibilities unchanged |
| NFR-05 | `runtime/interfaces.md` unchanged |

## Edge Cases

| Case | Expected Behavior |
|------|-------------------|
| Design-only project | EM marks Documentation phase **skipped** in pipeline-status with reason |
| No source code (pure docs project) | Generate from artifacts only; skip code-snippet compile checks |
| Missing `release.md` at doc time | Document from `review.md` + git; note release notes as draft |
| Broken links in repo | FAIL validation; fix or document as known issue |
| Library not in Context7 | Use public docs via fallback; note confidence reduction |

## Assumptions

- Projects continue using artifact root pattern from `pipeline-status.md`
- Git history available for CHANGELOG when `.git` exists
- Production work = any project shipping to users or public GitHub

## Dependencies

- Existing workflow.yaml structure
- MCP Platform capability `documentation-lookup`
- Handbook revision policy (EM approval)
