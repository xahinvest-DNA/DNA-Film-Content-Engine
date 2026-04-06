# NEXT TASK

Last updated: 2026-04-06
Status: ready
Task ID: F-012
Task type: implementation
Title: Semantic Output Suitability Review Controls

## Goal

Extend the local-first semantic workspace with one bounded output-suitability review surface so the editor can adjust how suitable each semantic block looks for downstream long video, shorts/reels, carousel, and packaging use without opening downstream generation scope.

## Why this is next

The repository now has a real editable semantic workspace with project creation, intake, block persistence, selected-block editing, reorder, split/merge, approval clarity, and lightweight completeness / issue visibility. The next strongest bounded step is to expose the already-defined output-suitability field as a minimal review control inside the existing inspector, rather than moving into matching, backend, or downstream automation.

## In scope

- one bounded follow-up packet on top of the completed F-011 runtime slice
- minimal selected-block output-suitability review controls inside the existing inspector
- persisted local updates to the existing output-suitability structure
- lightweight suitability visibility in the semantic list or summary where needed for clarity
- local tests covering suitability edits, reload persistence, and interaction with existing approval-reopen semantics where applicable

## Out of scope

- matching prep implementation
- scene-matching automation
- downstream output generation
- backend or API design
- generalized metadata framework
- broad navigation expansion
- packet expansion beyond semantic output-suitability review controls

## Recommended validation

Validate that the resulting packet delivers:

- one clear selected-block suitability review control in the desktop-facing semantic workspace
- persisted suitability changes that survive reload
- readable suitability visibility without redesigning the workspace into a dashboard
- no scope explosion into matching, backend, or downstream-output implementation

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
