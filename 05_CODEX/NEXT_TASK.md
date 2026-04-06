# NEXT TASK

Last updated: 2026-04-06
Status: ready
Task ID: F-009
Task type: implementation
Title: Semantic Approval Guardrails and Reopen Clarity

## Goal

Extend the semantic workspace with clearer approval-transition guardrails and explicit reopen visibility without drifting into matching, backend, or downstream execution work.

## Why this is next

The repository now has persisted semantic block ordering and clearer approval-readiness visibility inside the local-first semantic workspace. The strongest next step is to make approval transitions safer and more legible so the user can see when the semantic map is approved, why it is not yet approved, and when later edits reopen it, without building a larger workflow system.

## In scope

- one bounded follow-up packet on top of the completed F-008 runtime slice
- clearer approval and reopen messaging inside `Semantic Map Workspace`
- one narrow guardrail that prevents unclear approval transitions
- persisted visibility for reopened-after-change semantic state
- summary and inspector updates required to keep those approval signals readable
- only the runtime and persistence touches required to improve semantic approval trust

## Out of scope

- matching prep implementation
- scene-matching automation
- downstream output generation
- backend or API design
- generalized workflow engine
- broad navigation expansion
- packet expansion beyond semantic approval guardrails and reopen clarity

## Recommended validation

Validate that the resulting packet delivers:

- one clear approval-transition guardrail inside the desktop-facing semantic workspace
- visible reopened or under-edit state after semantic changes affect an approved map
- persisted approval-transition visibility that survives reload
- no scope explosion into matching, backend, or downstream-output implementation

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
