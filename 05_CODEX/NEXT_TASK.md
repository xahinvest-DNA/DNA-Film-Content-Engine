# NEXT TASK

Last updated: 2026-04-06
Status: ready
Task ID: F-006
Task type: implementation
Title: First MVP Implementation Slice

## Goal

Create one bounded implementation packet so DNA Film Content Engine can move from approved architecture into one minimal executable desktop slice without drifting into broad runtime infrastructure.

## Why this is next

The repository now has approved product, domain, schema, file, asset, and downstream output boundaries. The strongest next need is to prove that architecture through one narrow implementation slice rather than continue documentation layering or expand into the full stack at once.

## What should change

1. Implement one bounded path for project creation.
2. Implement one bounded path for analysis-text intake.
3. Implement one bounded path for semantic block persistence.
4. Implement one bounded path for semantic-map inspection.
5. Synchronize `CURRENT_STATE.md`, `TASKS.md`, and `CODEX_WORKLOG.md` if the packet is completed.

## In scope

* first minimal implementation slice
* one narrow vertical path only
* only the runtime surfaces and contracts required for that slice
* minimal executable path through the approved architecture

## Out of scope

* full backend
* full render pipeline
* full scene-matching automation
* platform publishing automation
* broad UI implementation across all screens
* generalized production system

## Recommended validation

Validate that the resulting packet delivers:

* concrete files created or updated
* one executable or testable minimal slice
* state synchronized after completion
* no scope explosion beyond the bounded slice

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
