# Current State

Last updated: 2026-04-17
Status: active
Product goal: desktop-first, local-first semantic-first MVP for film content production
Active frontier: F-006 First MVP Implementation Slice
Latest completed Codex packet: F-006A Minimal local-first desktop vertical slice for project creation, analysis intake, and semantic map inspection
Active next packet: F-006B Matching Prep Entry After Semantic Map

## What is true now

The repository now has the first honest executable desktop vertical slice inside frontier `F-006`.

The runtime is intentionally minimal and bounded:

- the desktop runtime is a local Tkinter shell;
- projects are saved as local project packages under `runtime_projects/`;
- the package follows the canonical local-first separation of `project.manifest`, `project.meta/`, `sources/`, `records/`, and `derived/`;
- the manifest stays light and points to canonical records instead of duplicating the full state model.

The runnable user path that now exists is:

1. create a project;
2. create a valid local package on disk;
3. paste or load primary analysis text;
4. save canonical project, intake, and analysis-source records;
5. generate provisional semantic blocks with a bounded deterministic bootstrap;
6. open the Semantic Map Workspace;
7. inspect a block in the inspector;
8. edit `title`, `role`, `output suitability`, and `notes`;
9. save changes locally;
10. close and reopen the project without losing data.

The persistence boundary is now explicit:

- source data lives in `sources/analysis/` plus the canonical analysis source record in `records/intake/analysis_source.json`;
- editable semantic records live in `records/semantic/semantic_blocks.json`;
- review state lives in `records/review/semantic_review.json`;
- the provisional bootstrap artifact lives in `derived/semantic/provisional_bootstrap.json`;
- project-level status visibility lives in `project.meta/status.json`.

The semantic bootstrap is intentionally narrow:

- it splits the analysis text by blank-line groups;
- it is heading-sensitive when the first line behaves like a heading;
- it creates real inspectable block records without opening any LLM orchestration frontier.

The desktop surface is also intentionally narrow:

- `Project Home` handles create/open and project status visibility;
- `Source Intake` handles text paste/file load plus source save;
- `Semantic Map Workspace` handles ordered block inspection, selection, editing, and local save.

Verification now exists for the real F-006A path:

- package creation and canonical folder/file placement;
- source intake and provisional block bootstrap;
- block editing and review-state persistence after reload;
- UI-path create/intake/edit/reopen behavior.

## Main product gap

The main gap is no longer "whether the first runtime exists at all."

The main gap is now the next honest downstream handoff:

- semantic map approval exists only as a minimal persisted state;
- no matching-prep entry surface exists yet;
- no scene matching, timecodes, rough cut, render/export, or broader AI orchestration exists in the active runtime;
- the UI is functional but intentionally plain.

## Delivery framing right now

The repository is currently governed by:

1. one active frontier;
2. one active bounded packet inside that frontier;
3. source-of-truth state docs that must describe only what is literally true in the repo.

`F-006A` is complete.

The strongest next move is `F-006B`, which should open the first minimal downstream handoff from approved semantic blocks into matching prep without widening into scene pipelines, timecodes, or export work.

## Accepted boundaries right now

- the product remains desktop-first and local-first;
- the runtime remains file-based and package-based;
- the current slice stops at semantic map inspection and editing;
- matching prep, scene matching, timecodes, output building, render/export, cloud sync, and broad AI orchestration remain out of scope;
- `CURRENT_STATE.md` owns live truth, `NEXT_TASK.md` owns the one active next packet, and `TASKS.md` records packet history.

## Open items

- add the first honest downstream handoff after semantic approval;
- keep the project package canonical as new record families are added;
- preserve boundedness and avoid turning the minimal runtime into premature infrastructure.

## Next step

Execute `F-006B Matching Prep Entry After Semantic Map`.

## What must not be lost in a new chat

- `F-006A` is now complete and runnable;
- the live runtime is intentionally a small Tkinter desktop shell;
- the first honest product path is `create project -> load analysis -> bootstrap semantic blocks -> inspect/edit semantic map -> save -> reopen`;
- semantic blocks are deterministic provisional records, not LLM-derived artifacts;
- canonical editable state lives in `records/`, source data remains separate, and provisional bootstrap output lives in `derived/`;
- the strongest next step is downstream handoff from semantic approval into matching prep, not cloud/backend/render/export work.
