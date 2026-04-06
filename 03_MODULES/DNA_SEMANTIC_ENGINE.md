# DNA Semantic Engine

Last updated: 2026-04-06
Status: active

## Module purpose

Define the logical transformation layer that turns analysis text into structured semantic units for editor-facing control and later scene matching.

This module is the meaning-first core of DNA Film Content Engine.

## Relationship to adjacent layers

- upstream intake behavior is defined in `03_MODULES/PROJECT_INTAKE.md`;
- downstream matching boundaries are defined in `03_MODULES/SCENE_MATCHING.md`;
- interface behavior for semantic control is defined in `02_PRODUCT/MVP_DESKTOP_INTERFACE.md` and related product docs;
- entity definitions live in `04_TECH/DOMAIN_MODEL.md`.

## Upstream dependencies

Required upstream inputs:
- valid `Project`;
- primary `Analysis Text`.

Optional supporting context:
- project metadata;
- notes attached during intake;
- optional film-side context that may help later handoff labeling, but not replace semantic interpretation.

## Downstream consumers

Primary downstream consumers:
- `Semantic Map Workspace` as the editorial control surface;
- `SCENE_MATCHING` as the next logical module.

Later downstream consumers:
- rough-cut building layers;
- shorts/reels derivation;
- carousel derivation;
- packaging derivation.

## Semantic engine responsibilities

- interpret the analysis text as meaning-bearing source material;
- propose and maintain structured `Semantic Blocks`;
- attach semantic subtype logic such as claim, insight, or mechanism where useful;
- preserve ambiguity markers when interpretation is uncertain;
- expose review points for human confirmation;
- produce a canonical semantic output that downstream modules can rely on.

## Input contract

The semantic engine receives:
- one valid `Project`;
- one primary `Analysis Text`;
- intake readiness state;
- optional supporting metadata and notes.

The semantic engine should assume:
- analysis text is the canonical semantic source;
- optional film-side assets do not replace semantic interpretation;
- human review remains available and necessary.

## Output contract

The semantic engine produces:
- a structured set of `Semantic Blocks`;
- semantic subtype or classification information where available;
- local ambiguity or confidence markers;
- project-level semantic readiness state;
- reviewable semantic-map artifacts suitable for editor confirmation;
- canonical downstream handoff data for `SCENE_MATCHING`.

The canonical downstream output is not a UI canvas.

It is an approved or reviewable semantic structure that downstream modules can interpret without depending on a specific screen representation.

## Transformation logic at conceptual level

### Step 1 - Read the analysis as a meaning structure

The module treats the analysis text as an argument or interpretation flow, not as raw text to be displayed unchanged.

### Step 2 - Derive semantic units

The module proposes one or more `Semantic Blocks` that represent coherent meaning units.

### Step 3 - Clarify semantic role

Where useful, the module attaches typed semantic understanding such as:
- claim;
- insight;
- mechanism;
- emotional point;
- explanatory point;
- transition function.

### Step 4 - Prepare editorial control

The semantic structure is presented as something the human can split, merge, rename, reorder, classify, and approve.

### Step 5 - Prepare downstream matching handoff

Approved or reviewable semantic units are handed forward with enough structure for matching preparation without requiring the downstream module to re-parse the original analysis text from scratch.

## Supported semantic unit types

The module may use the following semantic categories when they improve clarity:
- claim;
- insight;
- mechanism;
- emotional beat;
- explanatory beat;
- transition or connective unit;
- packaging-relevant point.

These categories should remain product-specific and meaning-first rather than generic NLP labels.

## Confidence / ambiguity handling

The semantic engine must preserve uncertainty explicitly.

### Acceptable ambiguity cases
- unclear boundary between two semantic blocks;
- uncertain semantic subtype;
- one block that may support more than one output orientation;
- weak or indirect downstream visual evidence expectation.

### Required behavior
- ambiguity should be marked, not hidden;
- uncertain structures should remain reviewable;
- the editor must be able to confirm, refine, or reject the proposed semantic interpretation.

## Human review points

Human review is required at least at these points:
- confirmation of the proposed semantic block structure;
- correction of titles, order, or scope;
- correction of semantic roles where the proposal is weak;
- project-level semantic approval before later matching work is treated as ready.

## Downstream handoff to scene matching

`SCENE_MATCHING` should receive a canonical semantic handoff containing:
- project identity;
- approved or reviewable semantic blocks;
- semantic subtype or role information;
- notes relevant to future visual proof needs;
- confidence or ambiguity markers where unresolved interpretation still matters.

## Non-goals

- no UI implementation;
- no prompt engineering specification;
- no LLM orchestration design;
- no runtime job design;
- no direct scene lookup execution logic;
- no timecode extraction implementation;
- no rough-cut building;
- no publishing or export behavior.

## Deferred runtime concerns

The following are intentionally deferred:
- exact proposal-generation mechanism;
- model/provider choice;
- persistence of revision history;
- autosave behavior;
- batch processing mechanics;
- latency and cost optimization;
- execution-level observability and retries.
