# Current State

Last updated: 2026-04-11
Status: active
Product goal: desktop-first content production software
Active stage: Stage C - Production hardening
Active delivery milestone: harden the four-builder runtime into repeatable local production software
Active Codex packet: C-001 Multi-Builder Output Hardening Entry

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

## Main product gap

The main gap has changed again:

- the product now has four honest builders and Stage B breadth is materially real;
- the main remaining gap is no longer output-family coverage, but production hardening;
- recovery confidence, validation depth, output-surface scalability, and release quality still need a deliberate Stage C pass.

The software is now a real multi-format content path proof, but it still needs harder release quality.

## Delivery framing

The project is now governed through four levels:

1. product goal: working software for content creation;
2. program stages: Stage A, Stage B, Stage C;
3. one active delivery milestone at a time;
4. one active Codex packet at a time.

The current active milestone belongs to Stage C and is aimed at making the now-broadened multi-builder runtime more durable, recoverable, and release-facing.

## What the next packet must do

`B-003` is now complete.

Four proven output builders are now real:

- packaging-ready script bundle;
- Shorts/Reels script;
- long-video script;
- carousel script.

All four artifacts now exist as saved markdown plus persisted output records behind the same hardened builder boundary, reload path, and stale-cleanup model.

The next active packet is `C-001`, because the strongest next move is to harden recovery, validation, and multi-builder usability rather than continue format expansion by inertia.

What is preserved:

- the first end-to-end usable output path exists;
- short-form, long-form, and carousel output paths now exist beside it;
- the product remains local-first and desktop-first;
- the export center is still intentionally narrow and not yet a full publishing system.
- the strategic watchlist now exists, but it is not a backlog and must not compete with the one active packet rule.

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

- harden recovery, validation, and release quality now that Stage B breadth exists;
- keep the four-builder output surface coherent as production hardening begins;
- use the watchlist to capture high-impact signals without converting everything into immediate packets.

## Next step

Execute `C-001 Multi-Builder Output Hardening Entry`.

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
- `C-001` is now the one active packet because production hardening is the strongest next move after Stage B breadth is proven.
