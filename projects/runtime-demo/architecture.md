# Architecture — Runtime Demo

## Overview
E2E runtime test

Platform: cross-platform. Stack: Python.

## API Contracts

### IRuntime
- `init_project`, `advance`, `validate`, `status` per runtime/interfaces.md

### FrameworkAPI
- CLI delegates to ProjectAPI → IRuntime

## Data Model

### PipelineState
- schema_version, current_phase_id, gate_history, artifact_index

## Security
- No secrets in state or event payloads
- Manifest-driven path resolution only

## Task Coverage
- T-001: Runtime facade in `packages/runtime_engine`
- T-002: JsonStateStore at `.runtime/state.json`
- T-003: Technology documented above

---
<!-- mcp-evidence: documentation-lookup -->
MCP Evidence: documentation-lookup — contracts sourced from runtime/interfaces.md (Runtime records only).
