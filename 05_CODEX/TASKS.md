# Codex Tasks

Last updated: 2026-04-11
Current focus: Stage B delivery milestone - output expansion beyond the first proven builder

## Working rule

There must be exactly one active packet at a time, and that packet must move the active delivery milestone rather than locally polishing the current surface.

## Active task

### B-001
- Status: active
- Title: First Shorts/Reels Builder Expansion
- Goal: turn the proven analysis-to-rough-cut chain into a first shorts/reels-oriented builder path using the now-established output-builder surface and persistence pattern.

## Recently completed

### P-001
- Status: completed
- Title: First Usable Content Output Vertical Slice
- Outcome: chose the packaging-ready script bundle as the first honest builder, added persisted output-record plus markdown artifact storage, exposed build/view flow in `Output Tracks`, and added persistence, integration, and UI acceptance coverage from analysis text to saved artifact.

### A-001
- Status: completed
- Title: Runtime Structural Refactor for Growth
- Outcome: introduced `runtime/ui`, `runtime/domain`, and `runtime/persistence`, turned `runtime/project_slice.py` into a thin compatibility facade over the persistence store, moved layout/navigation construction into `runtime/ui/layout.py`, kept the current runtime behavior intact, and added an integration smoke test covering analysis-to-rough-cut flow.

### M-001
- Status: completed
- Title: Project Governance Reset for Delivery
- Outcome: moved the repository from bounded-slice management to delivery-oriented program control, added `TARGET_STATE.md`, `DELIVERY_PLAN.md`, and `RELEASE_CRITERIA.md`, reduced the master control contour, closed the post-`F-040` waiting state, and opened `A-001` as the active next packet.

### F-040
- Status: completed
- Title: Rough Cut Focus Summary Cue Slice
- Outcome: the runtime now surfaces active rough-cut focus mode plus visible, saved-total, and preferred-total counts inside the `Rough Cut` lane.

## Earlier completed foundation

- `G-001` fixed manager review depth and efficiency-gate governance.
- `F-006` implemented the first local runtime slice.
- `F-007` through `F-040` extended that runtime from semantic editing through matching prep, scene/timecode stubs, and rough-cut assembly.
- `F-001` through `F-005` fixed the product, module, schema, and downstream-output document foundation.
