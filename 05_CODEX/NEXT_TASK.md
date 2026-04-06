# NEXT TASK

Last updated: 2026-04-06
Status: ready
Task ID: F-014
Task type: implementation
Title: Semantic Review Next-Issue Navigation and Focus-Step Controls

## Goal

Extend the local-first semantic workspace with one minimal step-through navigation layer so the editor can move through the currently focused semantic review set without losing context or opening broader workflow, backend/API, or dashboard scope.

## Why this is next

The repository now has bounded semantic review focus controls for issues, review-ready blocks, and suitability lanes. The strongest next bounded step is to let the editor move through those filtered review sets more fluidly inside the existing semantic map, rather than broadening into matching, downstream planning, or a larger workflow surface.

## In scope

- one bounded follow-up packet on top of the completed F-013 runtime slice
- one minimal next/previous navigation control for the currently visible semantic-review set
- lightweight current-position visibility for the focused list where needed for clarity
- only the runtime and local-state touches required to keep focused navigation coherent after edits or focus changes
- local tests covering focused navigation behavior without regressing prior packets

## Out of scope

- matching prep implementation
- scene-matching automation
- downstream output generation
- backend or API design
- generalized workflow queue or review engine
- broad navigation expansion
- packet expansion beyond semantic review next-issue navigation and focus-step controls

## Recommended validation

Validate that the resulting packet delivers:

- one clear next/previous control inside the desktop-facing semantic workspace
- stable movement through issue-focused, review-ready, or suitability-focused block subsets
- visible current-position clarity without dashboard sprawl
- no scope explosion into matching, backend, or downstream-output implementation

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
