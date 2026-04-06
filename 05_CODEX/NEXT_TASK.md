# NEXT TASK

Last updated: 2026-04-06
Status: ready
Task ID: F-006
Task type: implementation
Packet title: First MVP Implementation Slice

## Goal

Create one bounded implementation packet so DNA Film Content Engine can move from approved architecture to one real desktop-facing MVP slice without drifting into broad runtime infrastructure.

## Why this is next

The repository now has product flows, interface specifications, domain/model boundaries, persistence-facing structures, and downstream output contracts. The strongest next need is to turn that approved architecture into one concrete user-visible slice rather than continue architecture layering indefinitely.

## What should change

1. Define one bounded implementation packet for project creation.
2. Define one bounded implementation packet for analysis-text intake.
3. Define one bounded implementation packet for semantic block persistence and semantic-map inspection.
4. Synchronize `CURRENT_STATE.md`, `TASKS.md`, and `CODEX_WORKLOG.md` if the packet is completed.

## In scope

* one user-visible MVP implementation slice
* project creation
* analysis-text intake
* semantic block persistence
* semantic-map inspection
* local-first implementation boundaries only

## Out of scope

* no broad runtime infrastructure
* no render backend
* no export execution
* no scene-matching runtime implementation
* no API/backend platform design
* no publishing automation

## Recommended validation

Validate that the resulting packet defines and executes:

* one real desktop-facing MVP slice
* continuity from project creation to semantic-map inspection
* alignment with approved product, schema, and project-file boundaries
* bounded implementation without architecture drift

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
