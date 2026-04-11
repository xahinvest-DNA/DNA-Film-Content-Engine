# NEXT TASK

Last updated: 2026-04-11
Status: active
Task ID: C-002B
Task type: production_hardening
Title: Output Surface Density and Metadata Hardening

## Goal

Reduce output-surface density risk and repeated builder-metadata wiring so the four-builder workstation stays clear and maintainable as Stage C continues.

## Why this is next

`C-002A` is complete and the product now self-heals load-time truth across UI state, persisted status payload, and on-disk output artifacts while the decisions layer is back in SSOT alignment.

The strongest next move is now a bounded UI/metadata hardening pass: `Output Tracks` is still dense under four builders, and builder metadata wiring remains thin and repetitive even though recovery truth is stronger.

## In scope

- make `Output Tracks` easier to scan under four builders without broad redesign;
- reduce repeated per-builder metadata wiring where it directly improves clarity and maintainability;
- keep the current four-builder workstation coherent while preserving current recovery-truth guarantees;
- keep `runtime/app.py`, `runtime/builders/`, and `runtime/persistence/project_store.py` within the current hardened boundary model.

## Out of scope

- new builder families by default;
- full publishing/export platform work;
- backend/cloud work;
- heavy media rendering;
- platform publishing automation;
- broad visual redesign.

## Recommended validation

- verify `Output Tracks` stays coherent and readable across none/partial/all built states;
- reduce repeated builder wiring without breaking current recovery-truth guarantees;
- confirm the four-builder surface remains honest after reload and rebuild transitions;
- confirm hardening work still does not re-centralize logic in `runtime/app.py` or `runtime/persistence/project_store.py`.

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.

Also include:

- what output-surface and metadata areas were hardened next and why;
- what risks still remain before release-grade confidence;
- which watchlist items moved and which still remain watching.
