# NEXT TASK

Last updated: 2026-04-06
Status: ready
Task ID: F-003
Task type: product-architecture

## Goal

Create one bounded domain model and module-boundary packet so DNA Film Content Engine can move from approved MVP interface structure to stable product entities and system boundaries without drifting into engine runtime implementation too early.

## Why this is next

The repository now has user flows, screen map, UX principles, output definitions, platform rules, and a concrete MVP desktop interface package. The strongest next need is to define the product entities and module boundaries that the approved interface will operate on.

## What should change

1. Add `04_TECH/DOMAIN_MODEL.md`.
2. Add `03_MODULES/PROJECT_INTAKE.md`.
3. Add `03_MODULES/DNA_SEMANTIC_ENGINE.md`.
4. Add `03_MODULES/SCENE_MATCHING.md`.
5. Synchronize `CURRENT_STATE.md`, `TASKS.md`, and `CODEX_WORKLOG.md` if the packet is completed.

## What must stay unchanged

* no engine runtime implementation
* no automatic film downloading
* no render/export backend
* no scene-matching execution logic
* no mobile/sync/team workflow expansion
* no generic editor drift

## Recommended validation

Validate that the resulting packet defines:

* the core product entities used by the MVP interface
* clear ownership boundaries between intake, semantic, and matching-preparation modules
* stable terminology across product and tech layers
* prepared support for later phases without pretending runtime execution already exists

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
