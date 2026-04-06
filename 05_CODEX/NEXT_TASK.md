# NEXT TASK

Last updated: 2026-04-06
Status: ready
Task ID: F-007
Task type: implementation
Title: Semantic Map Editing and Review Controls

## Goal

Extend the first local-first MVP slice into one bounded editable semantic workspace by adding persisted selected-block editing and one minimal project-level semantic review control without drifting into matching, backend, or downstream execution work.

## Why this is next

The repository now has a proven first implementation slice for project creation, analysis-text intake, semantic block persistence, and semantic-map inspection. The strongest next step is to turn that inspect-only semantic workspace into a minimally editable review surface so the MVP behaves more like a real semantic operating environment without opening broad new lanes.

## In scope

- one bounded follow-up packet on top of the completed F-006 runtime slice
- selected-block editing for title, semantic role, and notes
- persisted updates to semantic block records on local disk
- one minimal project-level semantic review or approval control
- semantic-workspace summary updates required by those edits and review changes
- only the runtime surfaces and persistence touches required to keep the semantic workspace editable and reviewable

## Out of scope

- matching prep implementation
- scene-matching automation
- downstream output generation
- broad navigation expansion
- backend or API design
- generalized editing framework
- packet expansion beyond semantic-map editing and review controls

## Recommended validation

Validate that the resulting packet delivers:

- block edits that can be made in the desktop-facing semantic workspace
- persisted block changes that survive reload
- one visible project-level review or approval state change
- no scope explosion into matching, backend, or downstream-output implementation

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
