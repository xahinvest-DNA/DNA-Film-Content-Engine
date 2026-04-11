# NEXT TASK

Last updated: 2026-04-11
Status: active
Task ID: A-001
Task type: structural_refactor
Title: Runtime Structural Refactor for Growth

## Goal

Prepare the runtime for product growth by separating UI, domain, persistence, and service responsibilities without changing current behavior.

## Why this is next

The governance reset is complete.

The current runtime already proves a meaningful analysis-to-rough-cut path, but too much responsibility is concentrated in `runtime/app.py` and `runtime/project_slice.py`.

The next strongest move is to lower the cost of the first real builder/output path without opening new behavior prematurely.

## In scope

- create `runtime/ui/`, `runtime/domain/`, `runtime/services/`, and `runtime/persistence/`;
- move responsibilities out of `runtime/app.py` and `runtime/project_slice.py`;
- preserve current runtime behavior and entrypoint behavior;
- update imports and wiring so the application still runs;
- keep existing tests passing;
- add minimal integration smoke coverage for the current flow if needed.

## Out of scope

- new builder or export functionality;
- new UI/UX direction;
- backend/cloud work;
- media playback, rendering, or timeline editing.

## Recommended validation

- run the current test suite;
- verify the app entrypoint still launches;
- verify project create/open, semantic flow, matching prep flow, scene matching flow, and rough cut flow remain intact.

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.

Also include:

- what was moved;
- what behavior was intentionally preserved;
- what remains a candidate for the next refactor pass.
