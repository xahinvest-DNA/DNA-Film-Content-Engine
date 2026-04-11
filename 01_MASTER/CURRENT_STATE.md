# Current State

Last updated: 2026-04-11
Status: active
Product goal: desktop-first content production software
Active stage: Stage C - Production hardening
Active delivery milestone: convert stronger runtime trust into release-facing acceptance confidence
Active Codex packet: C-004 Release Criteria and Acceptance Hardening

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

The next output-surface density and metadata hardening pass is now also complete:

- `Output Tracks` now separates aggregate truth, builder-slot overview, current built artifacts, and pending builder slots instead of repeating the same per-builder blocks end to end;
- per-builder slot metadata is now described through a bounded shared UI contract in `runtime/ui/output_slots.py` instead of repeated ad hoc wiring inside the presentation layer;
- none-built, partial-built, all-built, cleared-after-reopen, and recovered-partial states are now easier to scan without weakening recovery truth;
- tests now protect the compact slot overview and pending-slot behavior alongside the existing recovery self-heal scenarios.

The next release-confidence and validation hardening pass is now also complete:

- repeated multi-cycle build/reopen/recover/rebuild flows are now test-protected beyond the earlier one-cycle recovery cases;
- mixed partial rebuild states plus resurrected stale output drift are now validated against UI truth, persisted status payload, and on-disk artifact truth;
- `Output Tracks` next-action and slot-state honesty are now checked after multiple consecutive recovery cycles rather than only after one reset;
- the validation layer now covers a broader set of damaging transitions without widening product scope.

## Main product gap

The main gap has changed again:

- the product now has four honest builders and Stage B breadth is materially real;
- the main remaining gap is no longer output-family coverage, but production hardening;
- recovery confidence, validation depth, and output-surface readability are now stronger than before C-003, but release-grade trust still needs a clearer acceptance and release-confidence layer;
- broader release quality remains open even though repeated-use validation is materially deeper.

The software is now a real multi-format content path proof, but it still needs harder release quality.

## Delivery framing

The project is now governed through four levels:

1. product goal: working software for content creation;
2. program stages: Stage A, Stage B, Stage C;
3. one active delivery milestone at a time;
4. one active Codex packet at a time.

The current active milestone belongs to Stage C and is aimed at turning the now-hardened four-builder runtime into something that is not only honest under repeated use, but also closer to explicit release-facing acceptance confidence.

## What the next packet must do

`C-003` is now complete.

Four proven output builders are now real:

- packaging-ready script bundle;
- Shorts/Reels script;
- long-video script;
- carousel script.

All four artifacts now exist as saved markdown plus persisted output records behind the same hardened builder boundary, reload path, stale-cleanup model, stronger load-time truth recovery, a less dense multi-builder output surface, and broader repeated-use validation coverage.

The next active packet is `C-004`, because the strongest next move is to turn the stronger runtime truth and repeated-use coverage into clearer release-facing acceptance confidence without changing product direction.

What is preserved:

- the first end-to-end usable output path exists;
- short-form, long-form, and carousel output paths now exist beside it;
- the product remains local-first and desktop-first;
- the export center is still intentionally narrow and not yet a full publishing system.
- the strategic watchlist now exists, but it is not a backlog and must not compete with the one active packet rule.
- Output Tracks is now clearer and less misleading in partial-build and cleared-after-reopen scenarios.
- open/reload now also repairs stale on-disk output drift instead of only reconciling it in memory.
- Output Tracks now uses a compact builder-slot overview plus pending-slot separation rather than repeating the same metadata wall for all four builders.
- bounded UI slot metadata now reduces repeated builder wiring without introducing a heavy registry framework.
- multi-cycle recovery and mixed partial-rebuild truth now have broader test protection than the earlier single-recovery cases.

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

- deepen release-facing acceptance confidence now that the first four hardening entries are complete;
- keep the four-builder output surface coherent as Stage C continues without turning UI metadata into a new abstraction sink;
- use the watchlist to capture high-impact signals without converting everything into immediate packets.

## Next step

Execute `C-004 Release Criteria and Acceptance Hardening`.

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
- `C-002B` reduced output-surface density and repeated builder-slot wiring through a bounded shared UI metadata contract;
- `C-003` materially expanded repeated-use validation depth across multi-cycle recovery and mixed partial rebuild states;
- `C-004` is now the one active packet because release-facing acceptance confidence is the strongest next bounded hardening target.
