# NEXT TASK

Last updated: 2026-04-11
Status: active
Task ID: C-001
Task type: production_hardening
Title: Multi-Builder Output Hardening Entry

## Goal

Harden the four-builder runtime so the product becomes more repeatable, recoverable, and trustworthy as local production software.

## Why this is next

`B-003` is complete and the product now has four honest builders: the packaging-ready script bundle, the Shorts/Reels script, the long-video script, and the carousel script.

The strongest next move is no longer another builder by inertia. Stage B breadth now exists, so the main risk has shifted to production hardening: output-surface density, recovery confidence, validation depth, and release-quality trust.

## In scope

- harden the four-builder output surface without redesigning the whole UI;
- improve validation and recovery confidence around reload, stale cleanup, and multi-builder coexistence;
- strengthen local production readiness for repeated use of the existing builder set;
- keep `runtime/app.py`, `runtime/builders/`, and `runtime/persistence/project_store.py` within the current hardened boundary model.

## Out of scope

- new builder families by default;
- full publishing/export platform work;
- backend/cloud work;
- heavy media rendering;
- platform publishing automation;
- broad visual redesign.

## Recommended validation

- verify one project can repeatedly reload and use all four builders without stale or misleading output state;
- expand test protection around multi-builder surface behavior, recovery, and validation honesty;
- confirm the output surface remains coherent with four builders before any future export-center expansion;
- confirm production hardening work does not re-centralize logic in `runtime/app.py` or `runtime/persistence/project_store.py`.

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.

Also include:

- what hardening areas were improved first and why;
- what risks still remain before release-grade confidence;
- which later watchlist items should stay watching rather than become immediate tasks.
