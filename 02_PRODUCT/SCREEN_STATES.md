# Screen States

Last updated: 2026-04-06
Status: active

## Purpose

Define the project-level and screen-level states needed to make MVP interface behavior legible and consistent.

This document owns state vocabulary and state transitions for the MVP desktop interface package. It does not own layout decisions.

## State vocabulary

### Empty

Meaning:
- required information or structure does not exist yet.

Use when:
- no project is selected;
- no source text is loaded;
- no semantic blocks exist.

### Warning

Meaning:
- work may continue, but the interface should surface a meaningful gap, inconsistency, or weakness.

Use when:
- optional assets are missing;
- semantic roles are incomplete;
- approval is possible but not recommended yet.

### In progress

Meaning:
- the user is actively building or editing a structure that is not yet considered approved or ready.

### Ready

Meaning:
- the current stage has met its MVP conditions and can feed the next stage.

### Blocked

Meaning:
- the next stage cannot proceed because a required prerequisite is absent.

### Placeholder / not yet active

Meaning:
- the surface is visible for orientation, but the product lane is not yet implemented in MVP depth.

## Project-level states

### No project

Meaning:
- no project has been created or opened.

Primary implication:
- `Project Home` cannot show project-specific progress yet.

### Draft project

Meaning:
- project exists, but the minimum source set is not yet complete.

Primary implication:
- the strongest next step is source intake.

### Sources partially loaded

Meaning:
- some source inputs exist, but the project is not yet fully ready for semantic work.

Primary implication:
- the interface should show what is present, what is optional, and what still blocks semantic block proposal.

### Semantic map in progress

Meaning:
- semantic blocks exist or are proposed, but the map remains under active editing or review.

Primary implication:
- `Semantic Map Workspace` becomes the primary operating surface.

### Semantic map ready

Meaning:
- semantic structure is approved at MVP level and can feed later matching preparation.

Primary implication:
- `Matching Prep` may become available as a bounded next-stage surface.

### Matching prep not ready

Meaning:
- the project does not yet satisfy the conditions for later matching preparation.

Primary implication:
- `Matching Prep` remains visible but either blocked or placeholder-only.

### Output tracks not ready

Meaning:
- output-specific views are not yet an active MVP lane.

Primary implication:
- `Output Tracks` remains orientation-only or placeholder-only.

### Export not ready

Meaning:
- final delivery behavior is outside current MVP depth.

Primary implication:
- `Export Center` remains placeholder-only.

## Screen-level states

## Project Home

### Newly created

Meaning:
- project exists, but no meaningful source work has happened yet.

UI expectation:
- emphasize identity, project status, and route to `Source Intake`.

### Source missing

Meaning:
- required analysis text is not present.

UI expectation:
- show a clear missing-source warning and one dominant next action.

### Semantic work pending

Meaning:
- source minimum exists, but semantic blocks are not yet approved.

UI expectation:
- show semantic-map readiness as the current active lane.

### Semantic map ready

Meaning:
- semantic map is approved.

UI expectation:
- show readiness summary and bounded access to the next lane.

### Next action available

Meaning:
- one strongest action can be suggested without ambiguity.

UI expectation:
- show one primary next-action control, not multiple competing CTA patterns.

## Source Intake

### No text loaded

Meaning:
- required analysis text is absent.

### Text loaded

Meaning:
- analysis text is present and recognized as the core semantic source.

### Optional assets missing

Meaning:
- media-side assets, transcript, subtitles, or notes are missing, but semantic work may still continue.

### Ready to continue

Meaning:
- the minimum viable source set for semantic work exists.

UI expectation:
- the interface may offer transition into semantic block proposal or semantic workspace entry.

## Semantic Map Workspace

### No blocks yet

Meaning:
- source text exists, but block structure is not yet proposed or created.

### Proposed blocks available

Meaning:
- the system has provided an initial semantic structure for review.

### Map under edit

Meaning:
- the semantic structure is being changed through split, merge, rename, reorder, reclassification, or note edits.

### Block selected

Meaning:
- one block is the current focus object and drives the inspector content.

### Map approved

Meaning:
- the project-level semantic map is approved for the MVP stage.

### Unresolved issues present

Meaning:
- warnings or incomplete fields remain visible even if some progress is strong.

UI expectation:
- approval should stay legible but cautious.

## Block Detail / Inspector

### Closed

Meaning:
- no block is selected or the detail panel is intentionally hidden.

### Opened with selected block

Meaning:
- the inspector is bound to one currently selected block.

### Editing block metadata

Meaning:
- title, role, suitability, or notes are being adjusted.

### Saving changes

Meaning:
- the interface is applying the current edit operation.

### Changes applied

Meaning:
- the selected block and semantic map reflect the saved changes.

## State transitions

### Project creation path

`no project -> draft project -> Project Home newly created -> Source Intake`

### Source preparation path

`no text loaded -> text loaded -> ready to continue -> proposed blocks available`

### Semantic structuring path

`proposed blocks available -> map under edit -> block selected -> changes applied -> map approved`

### Approval-to-next-stage path

`map approved -> semantic map ready -> matching prep available as bounded next-state surface`

### Reopen-after-approval path

`map approved -> block selected -> editing block metadata -> map under edit`

## Placeholder states for later-phase screens

## Matching Prep

Default MVP state:
- visible;
- placeholder or blocked until semantic-map readiness exists;
- never represented as a fully working scene-matching surface.

Allowed message pattern:
- `available after semantic map approval`
- `not yet active in MVP`

## Output Tracks

Default MVP state:
- visible for orientation;
- not presented as a fully working branching editor;
- may show shared-source logic and readiness summary only.

Allowed message pattern:
- `prepared later-phase view`
- `not yet active in MVP`

## Export Center

Default MVP state:
- visible only as a bounded later-phase endpoint;
- not presented as an operational delivery console.

Allowed message pattern:
- `delivery surface planned after later stages`
- `not yet active in MVP`
