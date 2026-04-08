# NEXT TASK

Last updated: 2026-04-08
Status: ready
Task ID: F-020
Task type: implementation
Title: First Manual Match Candidate Stub Slice

## Goal

Add one minimal local-first manual match-candidate stub slice inside Matching Prep so the project can hold one explicit semantic-to-asset candidate relationship without implementing scene matching automation, ranking, timecode logic, backend/API work, or a broader workflow engine.

## Why this is next

The repository now has both sides of the future matching bridge in real local-first form: approved semantic handoff and persisted film-side input registration. That means separate inputs are no longer the strongest gap.

The strongest next bounded gain is to create one honest manual candidate stub between those two sides, because that proves the next lane can hold an explicit matching-prep artifact without pretending that automated scene matching already exists.

## In scope

- one bounded follow-up packet on top of completed `F-019`
- one minimal manual semantic-to-asset candidate stub inside Matching Prep
- one narrow persisted representation of that stub in the local project package
- compact Matching Prep visibility for candidate-stub presence
- only the smallest runtime and local-storage changes required to make that candidate stub executable or testable
- local tests covering creation, reload persistence, and blocked/open coherence

## Out of scope

- scene matching automation
- ranking or candidate generation
- timecode logic
- backend or API design
- workflow queues or planning dashboards
- downstream output generation
- generalized matching subsystem buildout
- packet expansion beyond the first bounded manual candidate stub slice

## Recommended validation

Validate that the resulting packet delivers:

- one clear local-first manual candidate-stub path inside Matching Prep
- one persisted semantic-to-asset candidate artifact that survives reload
- coherent visibility between input presence and first candidate-stub presence
- no scope explosion into scene matching, backend, or downstream-output implementation

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
