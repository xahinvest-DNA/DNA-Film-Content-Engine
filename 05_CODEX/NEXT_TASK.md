# NEXT TASK

Last updated: 2026-04-17
Status: active
Task ID: F-006B
Task type: bounded_vertical_slice
Title: Matching Prep Entry After Semantic Map

## Goal

Open the first honest downstream handoff after `F-006A` by letting an approved semantic map feed a minimal matching-prep surface with local persistence and bounded review state.

## Why this is next

`F-006A` completed the first executable desktop slice:

- project creation works;
- local project packages are created in canonical structure;
- analysis text intake works;
- provisional semantic blocks are created and stored;
- Semantic Map inspection/editing works;
- reopen/reload retains local state.

The strongest next move is not wider infrastructure.

The strongest next move is the next real handoff in the product logic: from approved semantic blocks into a minimal matching-prep layer.

## In scope

- use approved semantic blocks as the gate into the next lane;
- save minimal matching-prep asset references in the project package;
- save one bounded accepted/preferred candidate linkage record for later downstream work;
- expose a minimal matching-prep workspace inside the desktop shell;
- keep persistence local-first and record-led.

## Out of scope

- scene matching;
- timecodes;
- rough cut;
- render/export;
- cloud/backend work;
- broad AI orchestration;
- generalized matching automation.

## Recommended validation

- verify approved semantic state is the explicit gate for matching prep;
- verify matching-prep records persist after reopen;
- verify the package still keeps source vs editable vs derived vs review distinctions clean;
- verify the UI still feels like one bounded vertical slice rather than a new subsystem frontier.

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.

Also include:

- what exact matching-prep records were added and where they persist;
- how the semantic approval gate is enforced;
- what remains intentionally deferred after `F-006B`.
