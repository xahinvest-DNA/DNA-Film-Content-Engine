# NEXT TASK

Last updated: 2026-04-11
Status: active
Task ID: P-001
Task type: vertical_slice
Title: First Usable Content Output Vertical Slice

## Goal

Build the first end-to-end vertical slice that produces a real content output artifact rather than only intermediate workflow records.

## Why this is next

The governance reset is complete and `A-001` has already reduced the structural concentration in the runtime.

The current runtime now reaches rough-cut preparation through a better-separated codebase, but it still does not produce a real output artifact.

The strongest next move is to prove the product's value with the first honest builder/output path.

## In scope

- choose the first MVP builder with the strongest value-to-effort ratio;
- define the output contract and storage location in the project package;
- build the artifact from existing semantic/matching/scene/timecode/rough-cut records;
- expose a UI path to trigger and inspect the result;
- add persistence, integration, and acceptance-style coverage for the new path.

## Out of scope

- full export center;
- all builders at once;
- backend/cloud work;
- heavy media rendering;
- platform publishing automation.

## Recommended validation

- verify one project can move from analysis text to a real saved output artifact;
- run persistence, integration, and acceptance-style coverage for the new builder path;
- confirm the existing analysis-to-rough-cut flow still remains intact.

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.

Also include:

- which builder was chosen and why;
- what practical output value now exists;
- which next builder or export step is naturally unlocked.
