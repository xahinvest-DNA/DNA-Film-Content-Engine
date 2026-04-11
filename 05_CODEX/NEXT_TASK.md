# NEXT TASK

Last updated: 2026-04-11
Status: active
Task ID: B-003
Task type: builder_expansion
Title: Carousel Script Builder Expansion

## Goal

Expand the proven output path by adding the first carousel-oriented builder on top of the current analysis-to-rough-cut chain.

## Why this is next

`B-002` is complete and the product now has three honest builders: the packaging-ready script bundle, the Shorts/Reels script, and the long-video script.

The strongest next move is to broaden Stage B output coverage with the first carousel builder while reusing the same hardened builder boundary and local-first output surface.

## In scope

- choose the first carousel builder contract that can reuse the current rough-cut and multi-builder context;
- define the carousel artifact format and where it lives in the project package;
- expose build and review flow in the current output surface;
- add persistence, integration, and acceptance-style coverage for the new builder path.

## Out of scope

- full export center;
- all remaining builders at once;
- backend/cloud work;
- heavy media rendering;
- platform publishing automation.

## Recommended validation

- verify one project can build a reproducible carousel artifact from the current workflow;
- run persistence, integration, and acceptance-style coverage for the new builder path;
- confirm the existing packaging, Shorts/Reels, and long-video paths remain intact;
- confirm the new builder fits the `runtime/builders/` boundary without pushing business rules back into `runtime/persistence/project_store.py` or `runtime/app.py`.

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.

Also include:

- what carousel contract was chosen and why;
- what new practical output value now exists beyond packaging + Shorts/Reels + long-video;
- which next builder or export step is naturally unlocked.
