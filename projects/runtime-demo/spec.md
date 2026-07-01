# Specification — Runtime Demo

## Functional Requirements

### FR-001 Pipeline Execution
The system SHALL execute the planning pipeline from idea through architecture.

**Acceptance Criteria:**
- GIVEN a new project WHEN `engineeringos project create` runs THEN planning artifacts are generated.

### FR-002 State Persistence
The system SHALL persist runtime state for resume and recovery.

**Acceptance Criteria:**
- GIVEN an interrupted pipeline WHEN resume is invoked THEN execution continues from last phase.

## Non-Functional Requirements

### NFR-001 Technology
Preferred stack: Python

### NFR-002 Editor Independence
Runtime SHALL NOT depend on Cursor, VS Code, or Claude Code.

## Edge Cases
- Missing predecessor artifacts block advancement
- Corrupted state triggers recovery error
- Invalid phase transitions are rejected

## Context
E2E runtime test
