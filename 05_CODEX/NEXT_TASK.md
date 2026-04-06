# NEXT TASK

Last updated: 2026-04-06
Status: ready
Task ID: F-005
Task type: product-architecture

## Goal

Create one bounded render/export schema and downstream output-boundary packet so DNA Film Content Engine can move from approved schema/project-file structures to stable downstream output contracts without drifting into runtime backend implementation too early.

## Why this is next

The repository now has product flows, MVP interface specifications, the core domain model, module boundaries, stable data structures, local project-file boundaries, and asset classifications. The strongest next need is to define how downstream output-oriented structures should be represented and handed off before any implementation packet begins.

## What should change

1. Add `04_TECH/RENDER_EXPORT_SCHEMA.md`.
2. Add `03_MODULES/LONG_VIDEO_BUILDER.md`.
3. Add `03_MODULES/SHORTS_REELS_BUILDER.md`.
4. Add `03_MODULES/CAROUSEL_BUILDER.md`.
5. Add `03_MODULES/PACKAGING_ENGINE.md`.
6. Synchronize `CURRENT_STATE.md`, `TASKS.md`, and `CODEX_WORKLOG.md` if the packet is completed.

## What must stay unchanged

* no runtime backend implementation
* no automatic film downloading
* no render queue or job orchestration design
* no scene-matching execution logic
* no API design
* no generic editor drift

## Recommended validation

Validate that the resulting packet defines:

* downstream render/export-facing record and package boundaries
* module contracts for long-form, shorts, carousel, and packaging output layers
* continuity from approved timecode/scene-reference artifacts into output-ready structures
* clear separation between schema-level architecture and runtime/backend implementation

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
