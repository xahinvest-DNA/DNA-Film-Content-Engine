# Current State

Last updated: 2026-04-11
Status: active
Product goal: desktop-first content production software
Active stage: Stage C - Production hardening
Active delivery milestone: harden recovery truth and keep SSOT state ownership internally consistent
Active Codex packet: C-002B Output Surface Density and Metadata Hardening

## What is true now

The repository has completed the governance reset from bounded-slice growth to delivery-oriented software execution.

The current runtime now proves a real local-first path through:

- project creation;
- analysis-text intake;
- semantic-map generation and editing;
- matching-prep registration and accepted-reference fixation;
- scene-reference and timecode stub fixation;
- rough-cut segment set assembly and preferred-subset review;
- one real packaging-ready script bundle output artifact saved inside the project package;
- one real Shorts/Reels script artifact saved inside the project package;
- one real long-video script artifact saved inside the project package;
- one real carousel script artifact saved inside the project package.

The current runtime therefore no longer stops at preparation. It now reaches reproducible exportable content artifacts through four honest builder paths.

The runtime boundary hardening pass is now also complete:

- `runtime/app.py` is reduced to a thin entrypoint;
- UI shell and presentation logic now live under `runtime/ui/`;
- builder logic now has an explicit `runtime/builders/` zone;
- `runtime/persistence/project_store.py` now coordinates persistence while domain rules own reopen, reconciliation, and downstream invalidation semantics;
- boundary tests now protect reopen cleanup, reload reproducibility, and builder-entrypoint consistency.
- `01_MASTER/STRATEGIC_WATCHLIST.md` now exists as a separate strategic-observation layer for non-blocking but potentially high-impact concerns.

The first Stage C hardening entry is now also complete:

- `Output Tracks` now reports explicit multi-builder inventory, trust/recovery state, next sensible action, and built artifact paths instead of relying on one dense mixed summary;
- repeated-use trust is stronger across `nothing built`, `partial build set`, `all built`, and `cleared after upstream reopen` states;
- `project.meta/status.json` now records output inventory state (`none_built`, `partially_built`, `all_built`) plus built/missing output families;
- repeated rebuild order, reload, and stale-cleanup scenarios are now more directly test-protected.

The next recovery-truth hardening pass is now also complete:

- `load_project()` now self-heals persisted truth when on-disk output files or `project.meta/status.json` drift away from currently valid downstream state;
- stale output files resurrected on disk no longer survive an open/reload cycle as if current;
- tampered persisted output-inventory status is corrected on load back to the actually valid builder set;
- harder reopen/reload/rebuild scenarios now have stronger test coverage;
- `DECISIONS.md` no longer conflicts with live stage state and now correctly delegates current-stage ownership to `CURRENT_STATE.md` and `DELIVERY_PLAN.md`.

## Main product gap

The main gap has changed again:

- the product now has four honest builders and Stage B breadth is materially real;
- the main remaining gap is no longer output-family coverage, but production hardening;
- recovery confidence and validation depth are now stronger than before C-002A, but they still need more hardening before release-grade trust;
- output-surface scalability and broader release quality remain open.

The software is now a real multi-format content path proof, but it still needs harder release quality.

## Delivery framing

The project is now governed through four levels:

1. product goal: working software for content creation;
2. program stages: Stage A, Stage B, Stage C;
3. one active delivery milestone at a time;
4. one active Codex packet at a time.

The current active milestone belongs to Stage C and is aimed at making the now-broadened multi-builder runtime more durable, recoverable, release-facing, and SSOT-consistent under repeated local use.

## What the next packet must do

`C-002A` is now complete.

Four proven output builders are now real:

- packaging-ready script bundle;
- Shorts/Reels script;
- long-video script;
- carousel script.

All four artifacts now exist as saved markdown plus persisted output records behind the same hardened builder boundary, reload path, stale-cleanup model, clearer multi-builder trust surface, and stronger load-time truth recovery.

The next active packet is `C-002B`, because the strongest next move is to reduce output-surface density risk and thin repeated builder metadata wiring without changing product direction.

What is preserved:

- the first end-to-end usable output path exists;
- short-form, long-form, and carousel output paths now exist beside it;
- the product remains local-first and desktop-first;
- the export center is still intentionally narrow and not yet a full publishing system.
- the strategic watchlist now exists, but it is not a backlog and must not compete with the one active packet rule.
- Output Tracks is now clearer and less misleading in partial-build and cleared-after-reopen scenarios.
- open/reload now also repairs stale on-disk output drift instead of only reconciling it in memory.

## Accepted boundaries right now

- `00_INDEX.md` owns navigation only.
- `CURRENT_STATE.md` owns what is true now.
- `TARGET_STATE.md` owns the definition of finished software.
- `DELIVERY_PLAN.md` owns stage logic and milestone sequencing.
- `RELEASE_CRITERIA.md` owns MVP readiness gates.
- `STRATEGIC_WATCHLIST.md` owns non-blocking but potentially high-impact watch items only.
- `NEXT_TASK.md` owns the one active Codex packet.
- the product remains desktop-first, local-first, and file-based for the current program stage.
- the next implementation work must not drift into backend/cloud, media playback, heavy rendering, or platform publishing automation.

## Open items

- deepen recovery, validation, and release quality now that the first two hardening entries are complete;
- keep the four-builder output surface coherent as Stage C continues;
- use the watchlist to capture high-impact signals without converting everything into immediate packets.

## Next step

Execute `C-002B Output Surface Density and Metadata Hardening`.

## What must not be lost in a new chat

- the project is judged by usable output, not by more intermediate stubs;
- the MVP path is `analysis -> semantic map -> matching -> scene/timecode chain -> rough cut -> output builder -> export package`;
- Stage A has been proven by the first real output path;
- Stage B output breadth is now materially proven through four builders;
- Stage C is now the current program stage;
- the first proven builder is the packaging-ready script bundle;
- the second proven builder is the Shorts/Reels script artifact;
- the third proven builder is the long-video script artifact;
- the fourth proven builder is the carousel script artifact;
- A-002 boundary hardening is complete and Stage B can expand on a cleaner runtime boundary;
- `STRATEGIC_WATCHLIST.md` exists as a strategic observation layer and is not a task backlog;
- `C-001` improved multi-builder trust, inventory visibility, and repeated-use coverage;
- `C-002A` hardened load-time recovery truth and repaired the decisions-layer SSOT conflict;
- `C-002B` is now the one active packet because output-surface density and metadata thinness are the strongest next bounded hardening targets.
