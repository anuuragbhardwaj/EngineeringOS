# Release — Kernel Hardening

**Version:** Kernel Hardening 1.0  
**Date:** 2026-07-02  
**Branch:** main

---

## Release Contents

- Dependency purity: `company_core` decoupled from `runtime_engine`
- Runtime ownership: `PipelineStateMutator`
- Durable checkpoints: `.company/checkpoints/orchestrator/`
- Event consistency: `AgentInvocationFailed` on orchestrator adapter failure
- MCP health tests

## Upgrade Notes

- **CLI users:** No action required
- **Embedders:** Call `configure_runtime_factory()` before using `ProjectAPI` outside CLI
- **Checkpoints:** First orchestrator checkpoint write creates `.company/checkpoints/` automatically

## Test Gate

142/142 tests pass.

## Release Decision

**Ship** — Final kernel architecture project complete.
