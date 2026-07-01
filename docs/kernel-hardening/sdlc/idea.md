# Idea — Kernel Hardening

## Problem

EngineeringOS constitutional architecture is complete, but three implementation gaps remain:

1. `company_core` imports `runtime_engine` directly
2. Orchestrator mutates `PipelineState` without Runtime-owned APIs
3. Orchestrator checkpoints are ephemeral

## Opportunity

Final kernel hardening before transitioning from framework development to building real software with EngineeringOS.

## Decision

**Proceed** — implementation hardening only. No redesign, no new platforms.
