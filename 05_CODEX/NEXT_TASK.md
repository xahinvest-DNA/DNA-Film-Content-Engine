# NEXT TASK

Last updated: 2026-04-08
Status: ready
Task ID: F-015
Task type: implementation
Title: Semantic Review Adjacent Context Peek

## Goal

Extend the local-first semantic workspace with one minimal adjacent-context cue so the editor can see the immediate previous and next semantic neighbors around the selected block without opening broader workflow, backend/API, or dashboard scope.

## Why this is next

The repository now has bounded focus controls plus previous/next movement through the current focused review set. The strongest next bounded step is to make that movement more intelligible by surfacing nearby semantic context around the selected block inside the existing review surface, rather than broadening into matching, downstream planning, or a larger workflow layer.

## In scope

- one bounded follow-up packet on top of the completed F-014 runtime slice
- one minimal adjacent-context cue for the currently selected semantic block
- lightweight previous/next block visibility where it improves focused review clarity
- only the runtime and local-state touches required to keep adjacent context coherent after navigation, edits, or focus changes
- local tests covering adjacent-context behavior without regressing prior packets

## Out of scope

- matching prep implementation
- scene-matching automation
- downstream output generation
- backend or API design
- generalized workflow queue or review engine
- broad navigation expansion
- packet expansion beyond semantic review adjacent context peek

## Recommended validation

Validate that the resulting packet delivers:

- one clear adjacent-context cue inside the desktop-facing semantic workspace or inspector
- better readability of semantic transitions while moving through focused review subsets
- coherent behavior after focus changes, edits, and boundary cases
- no scope explosion into matching, backend, or downstream-output implementation

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
