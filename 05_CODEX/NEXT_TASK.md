# NEXT TASK

Last updated: 2026-04-11
Status: active
Task ID: C-003
Task type: production_hardening
Title: Release Confidence and Validation Hardening

## Goal

Push the four-builder workstation from clearer trust and recovery behavior toward broader release-confidence by strengthening validation depth, repeated local-use confidence, and final trust semantics.

## Why this is next

`C-002B` is complete and the product now has a less dense `Output Tracks` surface plus thinner per-builder metadata wiring on top of the recovery-truth guarantees from `C-001` and `C-002A`.

The strongest next move is now a bounded release-confidence hardening pass: the runtime is clearer and more honest than before, but validation depth, repeated-use confidence, and release-facing trust still lag behind builder breadth.

## In scope

- strengthen validation around repeated open/reload/rebuild/invalidation cycles across the four-builder runtime;
- harden release-facing trust semantics where the current workstation can still feel less than release-grade under repeated local use;
- preserve the current boundary model while improving confidence rather than breadth;
- keep the one-active-packet rule and avoid turning the watchlist into a backlog.

## Out of scope

- new builder families by default;
- full publishing/export platform work;
- backend/cloud work;
- heavy media rendering;
- platform publishing automation;
- broad visual redesign.

## Recommended validation

- verify the four-builder runtime remains coherent across repeated build, reopen, reload, clear, and rebuild cycles;
- strengthen tests where release-facing trust still depends on a narrow set of scenarios;
- confirm the clearer `Output Tracks` surface still stays honest after harder repeated-use transitions;
- confirm hardening work still does not re-centralize logic in `runtime/app.py` or `runtime/persistence/project_store.py`.

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.

Also include:

- what release-confidence areas were hardened next and why;
- what risks still remain before release-grade confidence;
- which watchlist items moved and which still remain watching.
