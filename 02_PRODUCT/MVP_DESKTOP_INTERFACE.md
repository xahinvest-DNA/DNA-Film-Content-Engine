# MVP Desktop Interface

Last updated: 2026-04-06
Status: active

## Purpose

Define the first real desktop operating surface for DNA Film Content Engine.

The MVP desktop interface exists to let the user move from project creation and source intake into semantic-map control through one coherent desktop workspace.

## Product statement

- The MVP interface is not a generic timeline editor.
- The MVP interface is a semantic-first workspace.
- The main control surface is `Semantic Map Workspace`.
- `Project Home` and `Source Intake` feed into the semantic workspace.
- Later-phase lanes remain visible when they improve orientation, but they stay bounded and explicitly non-active.

## Main desktop structure

The MVP should read as one desktop application surface with stable navigation and changing work context.

### A. Top header / project bar

Purpose:
- show project name, film title, language, and current project status;
- show current stage label;
- keep the current strongest next action visible without taking over the screen.

Must include:
- project identity;
- project status;
- current screen title;
- current readiness summary;
- one primary next-action control when a clear next step exists.

### B. Left navigation rail

Purpose:
- provide the main product progression;
- preserve orientation across screens;
- keep future lanes visible without implying that they are implemented.

Primary sections:
- Project Home
- Source Intake
- Semantic Map
- Matching Prep
- Output Tracks
- Export Center

Behavior:
- MVP-active screens are selectable directly;
- later-phase screens may remain visible but must render as bounded placeholders;
- availability should reflect project readiness, not generic tab freedom.

### C. Main central workspace

Purpose:
- hold the dominant task surface for the selected screen;
- preserve the feeling that the user is working inside one project flow, not jumping between unrelated tools.

MVP expectation:
- `Project Home` uses the center to show stage overview and next-action guidance;
- `Source Intake` uses the center for source loading and validation;
- `Semantic Map Workspace` uses the center as the primary semantic operating surface.

### D. Right inspector / detail panel

Purpose:
- show object-level detail without forcing the user to leave the main workspace;
- support semantic editing, review, and approval.

MVP expectation:
- most visible and most important inside `Semantic Map Workspace`;
- opens in context for the selected block;
- carries metadata, output suitability, notes, and selected-block actions.

### E. Secondary status / summary area

Purpose:
- make readiness, warnings, and project-level summary visible without turning the interface into a dashboard-heavy control room.

May appear as:
- a lower summary strip in wide layouts;
- a central summary zone on `Project Home`;
- a dedicated summary column section within `Semantic Map Workspace`.

Must surface:
- source completeness;
- semantic-map progress;
- approval state;
- later-phase readiness.

### F. Stage readiness and next-action visibility

The desktop surface must always answer three questions:
- where the project currently stands;
- what is ready and what is blocked;
- what the strongest next meaningful action is.

This visibility should be persistent but restrained. It should orient the user, not dominate the workspace with excessive CTA noise.

## MVP screens inside one desktop surface

## Project Home

Role:
- main entry for a project;
- orientation screen rather than the deepest work surface.

Primary zone:
- project readiness overview.

Secondary zones:
- source status;
- semantic-map status;
- later-phase status cards;
- next-action panel.

User meaning:
- the user lands here after project creation;
- the user understands immediately whether to go to intake, semantic work, or review completion state.

## Source Intake

Role:
- controlled source-loading workspace for text and optional media-side assets.

Primary zone:
- analysis-text intake and validation.

Secondary zones:
- optional asset registration;
- completeness and warning feedback;
- continue action.

User meaning:
- the user attaches the minimum viable source set;
- the user is then routed toward semantic work rather than toward media tooling.

## Semantic Map Workspace

Role:
- main MVP operating surface;
- first truly deep workspace in the product.

Primary zone:
- semantic block map/list/canvas.

Secondary zones:
- selected block inspector;
- project-level summary;
- approval/readiness indicators.

User meaning:
- this is where the raw analysis becomes an approved semantic structure;
- this is the place where the product becomes meaning-first in practice.

## Block Detail / Inspector

Role:
- focused inspection and editing mode for one selected semantic block.

Default presentation:
- contextual panel within `Semantic Map Workspace`, not a separate product lane.

Use:
- opens when a block is selected;
- can expand attention onto one block without discarding the map context;
- supports metadata editing, note taking, and output suitability review.

## Semantic Map Workspace specification

## Purpose

`Semantic Map Workspace` is the center of the MVP because it turns the analysis text into an editor-approved semantic structure.

It is the first screen where the user exercises high-control product work rather than setup actions.

## Main zones

### A. Semantic map area

This is the dominant visual surface.

It may read as:
- an ordered block list;
- a structured map;
- or a scan-friendly canvas that still preserves clear sequence.

It must show:
- block title;
- block text preview;
- block role;
- output suitability;
- status indicators;
- current selection.

### B. Selected-block inspector

This is the main contextual detail surface.

It must show:
- full block text;
- editable title;
- role classification;
- output suitability controls;
- notes for later matching or packaging use;
- current block status.

### C. Project-level summary panel

This panel keeps the user aware of the semantic-map state at project level.

It must show:
- total blocks;
- approval status;
- unresolved warnings;
- source completeness summary;
- whether later matching preparation is structurally available.

### D. Approval and readiness strip

This area communicates whether the map is still under edit or is ready to move forward.

It must make visible:
- `under edit`;
- `issues present`;
- `ready for approval`;
- `approved`.

## Block interaction model

The semantic workspace must support:
- split block;
- merge blocks;
- rename block;
- reorder blocks;
- adjust role;
- adjust output suitability;
- add notes.

These actions should feel like semantic editing operations, not like clip editing or timeline trimming.

## Selection behavior

- only one block should be the primary selection at a time;
- selected state must remain visually obvious;
- changing selection updates the inspector without forcing a route change;
- the user should keep spatial awareness of the full map while working on one block.

## Approval behavior

The workspace must make approval legible and deliberate.

The interface should show:
- whether the map is still incomplete;
- whether warnings remain;
- whether the map is approved at project level.

Approval should not hide editability. An approved map may still be reopened for revision, but the change should be visible as a return from approved to under-edit state.

## Block Detail / Inspector behavior

## Product role

`Block Detail / Inspector` is a contextual detail surface rather than an independent navigation destination in daily MVP use.

It exists to deepen semantic editing without making the user lose the map.

## When it opens

- when the user selects a block in the semantic map;
- when the user creates a new proposed block and needs to refine it;
- when the user reopens an approved block for adjustment.

## What it must show

- full block text;
- editable block title;
- block role;
- output suitability for long video, shorts/reels, carousel, and packaging relevance;
- notes field;
- local warnings if required metadata is weak or incomplete.

## What it must allow

- rename;
- reclassify role;
- update output suitability;
- add or revise notes;
- confirm changes without leaving the workspace.

## Return behavior

- closing the inspector returns focus to the semantic map, not to another screen;
- changing selection moves the inspector context to the newly selected block;
- expanded detail should never make the user lose the main semantic structure entirely.

## Screen priority

### Must be deeply specified for MVP
- Project Home
- Source Intake
- Semantic Map Workspace
- Block Detail / Inspector

### Visible but bounded placeholders
- Matching Prep
- Output Tracks
- Export Center

### Deferred beyond MVP depth
- scene-matching execution surfaces;
- rough-cut building surfaces;
- render/export operations control;
- publishing or distribution consoles;
- broad media-library management surfaces.

## Non-goals

- no timeline-editor-first interface;
- no render/export control room;
- no scene-matching execution UI;
- no full media-management UI;
- no platform publishing console.
