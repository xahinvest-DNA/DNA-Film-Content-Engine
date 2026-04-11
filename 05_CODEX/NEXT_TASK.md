# NEXT TASK

Last updated: 2026-04-11
Status: active
Task ID: C-002
Task type: production_hardening
Title: Recovery and Validation Hardening Follow-up

## Goal

Deepen recovery and validation trust around the four-builder runtime so repeated local use feels dependable beyond the first Stage C hardening entry.

## Why this is next

`C-001` is complete and the product now has clearer multi-builder inventory, trust summaries, and stronger repeated-use coverage across the existing four outputs.

The strongest next move remains production hardening, but now with a narrower focus: deepen recovery confidence, rebuild/open behavior, and validation honesty rather than broadening the output family set.

## In scope

- deepen recovery confidence around open, reload, rebuild, and stale-cleared project packages;
- strengthen validation honesty around multi-builder repeated use and edge-state transitions;
- make the current four-builder workstation safer to trust without changing product direction;
- keep `runtime/app.py`, `runtime/builders/`, and `runtime/persistence/project_store.py` within the current hardened boundary model.

## Out of scope

- new builder families by default;
- full publishing/export platform work;
- backend/cloud work;
- heavy media rendering;
- platform publishing automation;
- broad visual redesign.

## Recommended validation

- verify one project can survive more demanding open/reload/rebuild cycles without misleading output state;
- expand test protection around recovery behavior, status persistence, and rebuild-after-clear flows;
- confirm the four-builder output surface stays coherent while deeper recovery hardening lands;
- confirm hardening work still does not re-centralize logic in `runtime/app.py` or `runtime/persistence/project_store.py`.

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.

Also include:

- what recovery and validation areas were hardened next and why;
- what risks still remain before release-grade confidence;
- which watchlist items moved and which still remain watching.
