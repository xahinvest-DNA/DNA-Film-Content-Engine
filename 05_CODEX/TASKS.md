# Codex Tasks

Last updated: 2026-04-11
Current focus: Stage C delivery milestone - keep the four-builder local production runtime trustworthy enough for repeated use and stronger release-facing validation

## Working rule

There must be exactly one active packet at a time, and that packet must move the active delivery milestone rather than locally polishing the current surface.

## Active task

### C-003
- Status: active
- Title: Release Confidence and Validation Hardening
- Goal: deepen repeated-use trust and validation depth now that recovery truth and output-surface density have already been hardened.

## Recently completed

### C-002B
- Status: completed
- Title: Output Surface Density and Metadata Hardening
- Outcome: reduced `Output Tracks` density by separating overview, built-artifact detail, and pending-slot guidance; introduced a bounded shared UI slot-metadata contract in `runtime/ui/output_slots.py`; preserved recovery guarantees; and added tests for compact four-builder state readability.

### C-002A
- Status: completed
- Title: Recovery Truth Hardening and SSOT Decision-State Alignment
- Outcome: made `load_project()` self-heal stale output files and tampered status payloads back to currently valid truth, added harder recovery-edge tests, and removed the stale live-stage conflict from `DECISIONS.md`.

### C-001
- Status: completed
- Title: Multi-Builder Output Hardening Entry
- Outcome: made `Output Tracks` clearer about built vs missing vs cleared output state, added explicit multi-builder inventory/trust/path summaries, strengthened repeated-use and stale-cleanup tests, and added output inventory state to `project.meta/status.json`.

### B-003
- Status: completed
- Title: Carousel Script Builder Expansion and Strategic Watchlist Initialization
- Outcome: added a fourth real builder in `runtime/builders`, persisted a carousel markdown artifact plus output record, integrated the new builder into `Output Tracks`, preserved coexistence with packaging + Shorts/Reels + long-video, created `01_MASTER/STRATEGIC_WATCHLIST.md`, and opened the first Stage C hardening packet.

### B-002
- Status: completed
- Title: Long Video Script Builder Expansion
- Outcome: added a third real builder in `runtime/builders`, persisted a long-video markdown artifact plus output record, integrated the new builder into `Output Tracks`, preserved coexistence with packaging + Shorts/Reels, and added reload/invalidation/UI coverage for the long-form path.

### B-001
- Status: completed
- Title: First Shorts/Reels Builder Expansion
- Outcome: added a second real builder in `runtime/builders`, persisted a Shorts/Reels markdown artifact plus output record, integrated the new builder into `Output Tracks`, preserved packaging-builder compatibility, and added coexistence/reload/invalidation coverage across both builders.

### A-002
- Status: completed
- Title: Runtime Boundary Hardening Before Builder Expansion Debt Grows
- Outcome: moved UI shell/presentation work under `runtime/ui`, formalized `runtime/builders` as the builder zone, pushed runtime rules into domain modules, reduced `runtime/app.py` to an entrypoint, made `runtime/persistence/project_store.py` persistence-led rather than rule-led, and added boundary tests for reopen cleanup, reload reproducibility, and builder-entrypoint consistency.

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
