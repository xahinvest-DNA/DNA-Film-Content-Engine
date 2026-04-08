# NEXT TASK

Last updated: 2026-04-08
Status: ready
Task ID: F-017
Task type: implementation
Title: Semantic Review Lane Markers

## Goal

Extend the local-first semantic workspace with one minimal lane-marker cue so the editor can read the currently active semantic review lane more explicitly without opening broader workflow, backend/API, or dashboard scope.

## Why this is next

The repository now has focus modes, step-through navigation, adjacent semantic context, and a compact focus-span summary. The strongest next bounded step is to make the current review lane itself read more intentionally by surfacing one compact lane-marker cue tied to the active focus mode, rather than broadening into matching, planning, or a larger review surface.

## In scope

- one bounded follow-up packet on top of the completed F-016 runtime slice
- one minimal lane-marker cue for the current focus mode inside the semantic workspace
- lightweight language or visual labeling that makes the active review lane more legible without redesigning the workspace
- only the runtime and local-state touches required to keep lane markers coherent after focus changes and empty-state transitions
- local tests covering lane-marker behavior without regressing prior packets

## Out of scope

- matching prep implementation
- scene-matching automation
- downstream output generation
- backend or API design
- generalized workflow queue or review engine
- broad navigation expansion
- packet expansion beyond semantic review lane markers

## Recommended validation

Validate that the resulting packet delivers:

- one clear lane-marker cue inside the desktop-facing semantic workspace
- better readability of which review lane is currently active without dashboard sprawl
- coherent updates after focus changes and empty-state transitions
- no scope explosion into matching, backend, or downstream-output implementation

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
