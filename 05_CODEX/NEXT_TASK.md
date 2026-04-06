# NEXT TASK

Last updated: 2026-04-06
Status: ready
Task ID: F-002
Task type: product-design

## Goal

Create one bounded MVP desktop interface specification packet so DNA Film Content Engine can move from approved product-layer structure to a concrete first desktop operating surface without drifting into engine implementation too early.

## Why this is next

The repository now has user flows, screen map, UX principles, output definitions, and platform rules. The strongest next need is to turn that product layer into a concrete MVP desktop interface package centered on the Semantic Map Workspace.

## What should change

1. Add `02_PRODUCT/MVP_DESKTOP_INTERFACE.md`.
2. Add `02_PRODUCT/SCREEN_STATES.md`.
3. Add `02_PRODUCT/NAVIGATION_BEHAVIOR.md`.
4. Synchronize `CURRENT_STATE.md`, `TASKS.md`, and `CODEX_WORKLOG.md` if the packet is completed.

## What must stay unchanged

* no engine implementation
* no automatic film downloading
* no scene-matching runtime
* no export/render backend
* no mobile/sync/team workflow expansion
* no generic timeline-editor drift

## Recommended validation

Validate that the resulting interface package defines:

* the main MVP desktop layout
* Semantic Map Workspace zones
* object visibility per screen
* screen and workflow states
* navigation rules between stages
* bounded placeholder behavior for later-phase screens

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
