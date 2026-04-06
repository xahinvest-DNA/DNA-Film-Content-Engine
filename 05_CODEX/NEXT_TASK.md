# NEXT TASK

Last updated: 2026-04-06
Status: ready
Task ID: F-008
Task type: implementation
Title: Semantic Map Ordering and Approval Readiness

## Goal

Extend the editable semantic workspace with one bounded set of ordering controls and clearer approval-readiness visibility without drifting into matching, backend, or downstream execution work.

## Why this is next

The repository now has a local-first semantic workspace where selected blocks can be edited and project-level semantic review state persists across reload. The strongest next step is to deepen semantic-map control inside that same workspace by allowing bounded ordering changes and making approval readiness more legible before any matching-facing work begins.

## In scope

- one bounded follow-up packet on top of the completed F-007 runtime slice
- one minimal semantic block ordering control inside `Semantic Map Workspace`
- persisted ordering changes on local disk
- clearer approval-readiness visibility derived from the existing semantic map state
- summary and inspector updates required by that ordering and readiness behavior
- only the runtime and persistence touches required to keep the semantic workspace more editor-usable

## Out of scope

- matching prep implementation
- scene-matching automation
- downstream output generation
- backend or API design
- generalized editing framework
- broad navigation expansion
- packet expansion beyond semantic-map ordering and approval-readiness control

## Recommended validation

Validate that the resulting packet delivers:

- one working ordering control for semantic blocks inside the desktop-facing semantic workspace
- persisted order changes that survive reload
- approval-readiness visibility that reflects the current semantic state without opening downstream execution
- no scope explosion into matching, backend, or downstream-output implementation

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
