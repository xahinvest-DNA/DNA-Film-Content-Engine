# NEXT TASK

Last updated: 2026-04-06
Status: ready
Task ID: F-013
Task type: implementation
Title: Semantic Review Filters and Focus Cues

## Goal

Extend the local-first semantic workspace with one minimal filtering and focus-cue layer so the editor can quickly isolate weak, suitability-specific, or review-ready semantic blocks without opening downstream execution, backend/API scope, or a dashboard-heavy workflow surface.

## Why this is next

The repository now has real semantic review controls for editing, ordering, split/merge correction, issue visibility, and output suitability. The strongest next bounded step is to improve editor navigation inside the existing semantic map by adding one minimal way to focus the list on blocks that currently need attention, rather than broadening into matching or downstream planning.

## In scope

- one bounded follow-up packet on top of the completed F-012 runtime slice
- one minimal semantic-map filter or focus control inside the existing workspace
- visibility for blocks with issues, review-readiness, or selected suitability states where it improves focus
- only the runtime and persistence touches required to keep filtering coherent and reload-stable if state is stored
- local tests covering focus/filter behavior without regressing prior packets

## Out of scope

- matching prep implementation
- scene-matching automation
- downstream output generation
- backend or API design
- generalized query/filter engine
- broad navigation expansion
- packet expansion beyond semantic review filters and focus cues

## Recommended validation

Validate that the resulting packet delivers:

- one clear semantic-map focus/filter control in the desktop-facing workspace
- faster isolation of blocks that need attention without dashboard sprawl
- coherence with existing issue visibility, suitability review, and approval signals
- no scope explosion into matching, backend, or downstream-output implementation

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
