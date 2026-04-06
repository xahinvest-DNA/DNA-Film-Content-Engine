# NEXT TASK

Last updated: 2026-04-06
Status: ready
Task ID: F-004
Task type: product-architecture

## Goal

Create one bounded data schema and project file format packet so DNA Film Content Engine can move from approved domain/module boundaries to stable persistence-ready structures without drifting into runtime pipeline implementation too early.

## Why this is next

The repository now has product flows, MVP interface specifications, the core domain model, and module boundaries for intake, semantic structuring, and scene matching. The strongest next need is to define the stable data structures and local project-file boundaries that these approved layers depend on.

## What should change

1. Add `04_TECH/DATA_SCHEMA.md`.
2. Add `04_TECH/PROJECT_FILE_FORMAT.md`.
3. Add `04_TECH/ASSET_PIPELINE.md`.
4. Synchronize `CURRENT_STATE.md`, `TASKS.md`, and `CODEX_WORKLOG.md` if the packet is completed.

## What must stay unchanged

* no runtime pipeline implementation
* no automatic film downloading
* no render/export backend
* no scene-matching execution logic
* no API or job orchestration design
* no generic editor drift

## Recommended validation

Validate that the resulting packet defines:

* stable structures for core project entities and readiness markers
* local project-file organization boundaries
* asset classification and handoff boundaries without runtime fiction
* clear continuity from domain/model layer into later technical implementation packets

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
