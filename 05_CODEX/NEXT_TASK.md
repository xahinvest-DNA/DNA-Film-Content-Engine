# NEXT TASK

Last updated: 2026-04-10
Status: ready
Task ID: F-021
Task type: implementation
Title: Manual Match Candidate Review Status Slice

## Goal

Add one minimal local-first review-status control for manual match candidate stubs inside Matching Prep so the project can distinguish candidate stubs that are still tentative from those explicitly selected or rejected for later matching work without implementing ranking, automation, timecode logic, backend/API work, or a broader workflow engine.

## Why this is next

The repository now has both sides of the future matching bridge plus one honest manual candidate-stub artifact in local-first form. That means raw candidate presence is no longer the strongest gap.

The strongest next bounded gain is to let Matching Prep express explicit editorial intent about those manual candidates, because that proves the lane can hold not only candidate existence but also one minimal review decision without pretending that automated scene matching already exists.

## In scope

- one bounded follow-up packet on top of completed `F-020`
- one minimal review-status control for manual candidate stubs inside Matching Prep
- one narrow persisted status on each manual candidate stub in the local project package
- compact Matching Prep visibility for tentative versus selected or rejected candidate state
- only the smallest runtime and local-storage changes required to make that review state executable or testable
- local tests covering review-state update, reload persistence, and blocked/open coherence

## Out of scope

- scene matching automation
- ranking or candidate generation
- timecode logic
- backend or API design
- workflow queues or planning dashboards
- downstream output generation
- generalized matching subsystem buildout
- packet expansion beyond the first bounded candidate-review-status slice

## Recommended validation

Validate that the resulting packet delivers:

- one clear local-first review-status path for manual candidate stubs inside Matching Prep
- one persisted candidate-review state that survives reload
- coherent visibility between candidate-stub presence and selected or rejected intent
- no scope explosion into scene matching, backend, or downstream-output implementation

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
