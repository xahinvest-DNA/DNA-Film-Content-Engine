# NEXT TASK

Last updated: 2026-04-08
Status: ready
Task ID: F-018
Task type: implementation
Title: First Matching Prep Entry Slice

## Goal

Open the first minimal local-first `Matching Prep` entry surface so an approved semantic map can feed one real downstream-facing handoff slice without implementing scene matching automation, backend/API work, or a broader planning workflow.

## Why this is next

The repository now has a bounded semantic workspace with explicit review state, approval guardrails, reopen-after-change clarity, completeness and issue visibility, suitability review, focused navigation, adjacent context, focus-span summary, and a compact readiness gate that says whether the current semantic map is structurally ready for later matching prep.

That means the strongest next bounded gain is no longer another semantic review micro-cue. The next stronger step is to prove that this approved semantic state can open one real entry surface for the later lane, while still staying local-first and intentionally narrow.

## In scope

- one bounded follow-up packet on top of completed `F-017R`
- one minimal `Matching Prep` entry surface inside the current desktop-facing runtime
- one local-first handoff view derived from the approved semantic map only
- one narrow blocked-vs-open transition between semantic approval state and matching-prep entry
- only the smallest local data/runtime changes required to make that entry slice executable or testable
- local tests covering approved-entry behavior, blocked behavior, and reload coherence where applicable

## Out of scope

- scene matching automation
- shot or asset matching logic
- backend or API design
- workflow queues or planning dashboards
- downstream output generation
- generalized matching-prep subsystem buildout
- packet expansion beyond the first bounded matching-prep entry slice

## Recommended validation

Validate that the resulting packet delivers:

- one clear local-first `Matching Prep` entry path tied to the current semantic project state
- blocked behavior while the semantic map is not yet structurally ready
- open behavior once the semantic map is approved and matching-prep-ready
- one narrow downstream-facing handoff surface without matching automation or backend expansion
- no scope explosion into scene matching, backend, or downstream-output implementation

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
