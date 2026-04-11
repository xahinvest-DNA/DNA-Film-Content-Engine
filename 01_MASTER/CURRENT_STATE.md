# Current State

Last updated: 2026-04-11
Status: active
Product goal: desktop-first content production software
Active stage: Stage B - Builder outputs
Active delivery milestone: expand the output layer beyond the first two proven builders
Active Codex packet: B-002 Long Video Script Builder Expansion

## What is true now

The repository has completed the governance reset from bounded-slice growth to delivery-oriented software execution.

The current runtime now proves a real local-first path through:

- project creation;
- analysis-text intake;
- semantic-map generation and editing;
- matching-prep registration and accepted-reference fixation;
- scene-reference and timecode stub fixation;
- rough-cut segment set assembly and preferred-subset review;
- one real packaging-ready script bundle output artifact saved inside the project package.
- one real Shorts/Reels script artifact saved inside the project package.

The current runtime therefore no longer stops at preparation. It now reaches reproducible exportable content artifacts through two honest builder paths.

The runtime boundary hardening pass is now also complete:

- `runtime/app.py` is reduced to a thin entrypoint;
- UI shell and presentation logic now live under `runtime/ui/`;
- builder logic now has an explicit `runtime/builders/` zone;
- `runtime/persistence/project_store.py` now coordinates persistence while domain rules own reopen, reconciliation, and downstream invalidation semantics;
- boundary tests now protect reopen cleanup, reload reproducibility, and builder-entrypoint consistency.

## Main product gap

The main gap has changed again:

- the product now has two honest builders, but output breadth is still incomplete;
- long-video and further builder families are still missing;
- production hardening is still missing.

The software is now a real content-creation path proof, but it still needs more builders and harder release quality.

## Delivery framing

The project is now governed through four levels:

1. product goal: working software for content creation;
2. program stages: Stage A, Stage B, Stage C;
3. one active delivery milestone at a time;
4. one active Codex packet at a time.

The current active milestone belongs to Stage B and is aimed at expanding output coverage beyond the now-proven packaging and short-form builder pair.

## What the next packet must do

`B-001` is now complete.

Two proven output builders are now real:

- builder chosen: packaging-ready script bundle;
- artifact type: saved markdown + persisted output record;
- output surface: `Output Tracks`;
- second builder added: Shorts/Reels script;
- second artifact type: saved markdown + persisted output record;
- acceptance proof: analysis text to both saved artifacts is now test-covered.

The next active packet is `B-002`, because the strongest next move is to add the first long-video-oriented builder on top of the same hardened output layer.

What A-002 changed before that move:

- Stage B no longer has to expand builders on top of a hidden persistence-heavy core;
- stale downstream chain state is now honestly cleared when upstream approval is reopened;
- builder invocation now has a clearer extension contour for the next output family.

What is preserved:

- the first end-to-end usable output path exists;
- the second output path now exists beside it;
- the product remains local-first and desktop-first;
- the export center is still intentionally narrow and not yet a full publishing system.

## Accepted boundaries right now

- `00_INDEX.md` owns navigation only.
- `CURRENT_STATE.md` owns what is true now.
- `TARGET_STATE.md` owns the definition of finished software.
- `DELIVERY_PLAN.md` owns stage logic and milestone sequencing.
- `RELEASE_CRITERIA.md` owns MVP readiness gates.
- `NEXT_TASK.md` owns the one active Codex packet.
- the product remains desktop-first, local-first, and file-based for the current program stage.
- the next implementation work must not drift into backend/cloud, media playback, heavy rendering, or platform publishing automation.

## Open items

- implement the next builder after packaging + Shorts/Reels;
- expand the product toward long-video and then further Stage B outputs;
- harden recovery, validation, and release quality later in Stage C.

## Next step

Execute `B-002 Long Video Script Builder Expansion`.

## What must not be lost in a new chat

- the project is judged by usable output, not by more intermediate stubs;
- the MVP path is `analysis -> semantic map -> matching -> scene/timecode chain -> rough cut -> output builder -> export package`;
- Stage A has been proven by the first real output path;
- Stage B is now the current program stage;
- the first proven builder is the packaging-ready script bundle;
- the second proven builder is the Shorts/Reels script artifact;
- A-002 boundary hardening is complete and Stage B can expand on a cleaner runtime boundary;
- `B-002` is now the one active packet because long-video expansion is the strongest next move.
