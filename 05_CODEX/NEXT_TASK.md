# NEXT TASK

Last updated: 2026-04-08
Status: ready
Task ID: F-016
Task type: implementation
Title: Semantic Review Focus-Span Summary

## Goal

Extend the local-first semantic workspace with one minimal focus-span summary so the editor can see a compact summary of the currently active review subset without opening broader workflow, backend/API, or dashboard scope.

## Why this is next

The repository now has bounded focus modes, step-through navigation within the current focused subset, and adjacent semantic context around the selected block. The strongest next bounded step is to make the active review slice itself easier to read by surfacing one small span-level cue about the current focused set, rather than broadening into matching, planning, or a larger review surface.

## In scope

- one bounded follow-up packet on top of the completed F-015 runtime slice
- one minimal summary cue for the current focused semantic-review subset
- lightweight visibility such as subset size, visible sequence span, or equivalent compact range information where it improves review orientation
- only the runtime and local-state touches required to keep the summary coherent after focus changes, navigation, or structural edits
- local tests covering focus-span summary behavior without regressing prior packets

## Out of scope

- matching prep implementation
- scene-matching automation
- downstream output generation
- backend or API design
- generalized workflow queue or review engine
- broad navigation expansion
- packet expansion beyond semantic review focus-span summary

## Recommended validation

Validate that the resulting packet delivers:

- one clear focus-span summary cue inside the desktop-facing semantic workspace
- better readability of the active focused review slice without dashboard sprawl
- coherent updates after focus changes, navigation, and structural edits
- no scope explosion into matching, backend, or downstream-output implementation

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
