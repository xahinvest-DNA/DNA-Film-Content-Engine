# NEXT TASK

Last updated: 2026-04-11
Status: active
Task ID: C-004
Task type: production_hardening
Title: Release Criteria and Acceptance Hardening

## Goal

Turn the now-broader runtime trust and repeated-use validation into clearer release-facing acceptance confidence, so Stage C stops being only “harder to break” and becomes “closer to explicit release readiness.”

## Why this is next

`C-003` is complete and the product now has broader repeated-use validation across multi-cycle recover/rebuild scenarios on top of the surface and recovery hardening from `C-001`, `C-002A`, and `C-002B`.

The strongest next move is now a bounded release-facing hardening pass: the runtime is clearer and more test-protected than before, but acceptance confidence and release-facing evidence still lag behind the four-builder workstation breadth.

## In scope

- convert stronger runtime truth into clearer acceptance-style and release-facing validation evidence;
- tighten the most important gaps between current hardening progress and `RELEASE_CRITERIA.md`;
- preserve the current boundary model while improving release confidence rather than breadth;
- keep the one-active-packet rule and avoid turning the watchlist into a backlog.

## Out of scope

- new builder families by default;
- full publishing/export platform work;
- backend/cloud work;
- heavy media rendering;
- platform publishing automation;
- broad visual redesign.

## Recommended validation

- verify the four-builder runtime remains coherent against the release criteria under acceptance-style validation, not only unit-level or narrow boundary scenarios;
- strengthen tests where release-facing confidence is still implied rather than explicitly proven;
- confirm the clearer `Output Tracks` surface still stays honest while broader acceptance evidence is added;
- confirm hardening work still does not re-centralize logic in `runtime/app.py` or `runtime/persistence/project_store.py`.

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.

Also include:

- what release-criteria and acceptance-confidence areas were hardened next and why;
- what risks still remain before release-grade confidence;
- which watchlist items moved and which still remain watching.
