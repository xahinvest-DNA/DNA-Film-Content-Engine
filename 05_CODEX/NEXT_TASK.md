# NEXT TASK

Last updated: 2026-04-06
Status: ready
Task ID: F-010
Task type: implementation
Title: Semantic Completeness Cues and Issue Visibility

## Goal

Extend the semantic workspace with lightweight completeness cues and clearer issue visibility without drifting into matching, backend, or downstream execution work.

## Why this is next

The repository now has clearer approval guardrails and explicit reopened-after-change visibility inside the local-first semantic workspace. The strongest next step is to make the semantic map more self-explanatory by surfacing lightweight completeness cues and issue visibility before any broader workflow or matching-facing work begins.

## In scope

- one bounded follow-up packet on top of the completed F-009 runtime slice
- lightweight completeness cues for semantic blocks or project-level semantic state
- clearer visibility for small semantic issues that affect approval confidence
- summary and inspector updates required to keep those cues readable
- only the runtime and persistence touches required to improve semantic review clarity

## Out of scope

- matching prep implementation
- scene-matching automation
- downstream output generation
- backend or API design
- generalized validation engine
- broad navigation expansion
- packet expansion beyond semantic completeness cues and issue visibility

## Recommended validation

Validate that the resulting packet delivers:

- visible completeness or issue cues inside the desktop-facing semantic workspace
- persisted visibility that survives reload where required by the new cues
- clearer understanding of why the semantic map is complete or still weak
- no scope explosion into matching, backend, or downstream-output implementation

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
