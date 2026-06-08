# Careena Pipeline 3 Architecture Contract

## Status

Active working contract for the incremental migration from
`server/careena_pipeline/` to `server/careena_pipeline3/`.

## Purpose

This document fixes the first architectural decisions for the migration so the
new package is not shaped by ad-hoc copies from the legacy structure.

## Core decisions

### 1. Orchestrator naming

- The primary turn orchestrator in `careena_pipeline3` is named
  `DialogueManager`.
- The legacy name `DialogueStateManager` is reserved for state mutation logic
  only and must not be reused as the top-level orchestrator name.

### 2. Target responsibility split

The new application layer is organized around explicit manager roles:

- `DialogueManager`
- `EntryManager`
- `ExtractionManager`
- `CaseStateManager`
- `SafetyManager`
- `ResponseManager`
- `ConfirmationManager`

### 3. Manager of managers

`DialogueManager` owns the per-turn execution order and composes the other
managers. It does not permanently absorb their internal policies.

### 4. Turn contract

Every user message is processed as a turn with three stable artifacts:

- `TurnInput`
- `TurnContext`
- `TurnResult`

The exact fields may evolve, but the contract shape must remain explicit.

### 5. Safety modeling

- Safety is treated as its own architectural concern.
- `careena_pipeline3` will introduce an explicit `SafetyState` as a turn-level
  artifact.
- The current red-flag detector may stay the same during early migration.

### 6. Core preservation rule

The generic LLM infrastructure from `careena_pipeline.core` is migrated with
minimal or no behavioral changes:

- `core/client.py`
- `core/engine.py`
- `core/exceptions.py`

### 7. No package-level legacy mirroring

`careena_pipeline3` must not start by recreating legacy package groups like
`flow/`, `planning/`, and `state/` unchanged. Migration happens by target role,
not by source folder.

### 8. Medical logic admissibility rule

Medical logic from the legacy system is not admissible by default.

The following legacy patterns must be treated as suspicious until explicitly
re-justified:

- symptom or body-part keyword routing
- hardcoded specialty or urgency shortcuts
- one-off emergency escalations for narrow textual markers
- medical fallback heuristics that exist only because an earlier extraction or
  state model was weak
- case-completion rules that fake certainty instead of improving structure

### 9. Structural logic vs. medical decision logic

The migration distinguishes sharply between:

- structural logic:
  - orchestration
  - state synchronization
  - generic merge mechanics
  - transport and logging
- medical decision logic:
  - recommendation policy
  - urgency decisions
  - specialty selection
  - symptom-specific follow-up policy

Structural logic may be migrated earlier when it improves architecture.
Medical decision logic must pass a stronger review gate first.

### 10. Target Model 5 check is mandatory

Before any additional behavior-heavy component is migrated, we must compare it
against `TARGET_MODEL5.md` and answer:

1. Which manager owns this behavior in the target model?
2. Is the behavior truly part of that manager, or was it only compensating for
   another weakness in the legacy system?
3. Would keeping it make the new system clearer, or merely preserve hidden
   coupling?

### 11. Call 2 is a redesign candidate

Call 2 and the surrounding medical extraction behavior are not treated as
stable legacy truth.

Current assumptions:

- the generic extraction engine is reusable
- the current medical extraction behavior is likely to change
- the current medical data modeling is not clean enough to be preserved by
  default

Migration consequence:

- `LLMCaseUpdateExtractor` must not be copied into `careena_pipeline3` as-is
- the future Call-2 contract should be designed around cleaner extraction
  outputs first, and only then mapped into longer-lived state
- temporary compatibility bridges are allowed, but they must stay visibly
  temporary

## Initial package layout

```text
careena_pipeline3/
  application/
    managers/
  core/
  domain/
  infrastructure/
  models/
    common/
    turn/
```

This is an initial structure, not a frozen final tree.

## First implementation rule

Before migrating behavior-heavy legacy code, `careena_pipeline3` must first
have:

- a stable package root
- the preserved generic core
- explicit turn models
- an orchestrator entry point with clear dependencies

## Review rule for every phase

Before a migrated legacy component is accepted into `careena_pipeline3`, we
must answer:

1. Should this behavior exist in the new system at all?
2. Does the current shape match the target role?
3. If not, is the mismatch a temporary migration compromise or a design error?
4. Is this structural migration, or are we about to preserve dubious medical
   decision logic?
