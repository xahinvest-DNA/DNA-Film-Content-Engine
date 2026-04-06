# Screen Map

Last updated: 2026-04-06
Status: active

## Purpose

Define the first desktop-first screen hierarchy and responsibilities for DNA Film Content Engine.

## Screen hierarchy

### S-01 Project Home
Main entry for one project.

#### Responsibilities
- show project identity;
- show project status;
- show readiness by stage;
- route into the next meaningful screen.

#### Main zones
- project header;
- source status;
- semantic map readiness;
- output-track readiness;
- next action panel.

### S-02 Source Intake
Screen for loading and inspecting source materials.

#### Responsibilities
- analysis-text input;
- source asset registration;
- asset completeness visibility;
- preparation for semantic processing.

#### Main zones
- analysis text panel;
- attached assets panel;
- validation panel;
- continue action area.

### S-03 Semantic Map Workspace
The main MVP operating surface.

#### Responsibilities
- show semantic blocks;
- allow split / merge / rename / reorder;
- show role and output suitability;
- support editor approval of the map.

#### Main zones
- block list or canvas;
- selected block detail;
- semantic properties panel;
- project-level summary panel.

### S-04 Block Detail / Inspector
Focused inspection and editing of a selected semantic block.

#### Responsibilities
- show full block text;
- edit block title;
- edit role classification;
- mark output suitability;
- store notes for future matching.

#### Main zones
- full text;
- metadata fields;
- output checkboxes/toggles;
- notes panel.

### S-05 Matching Preparation
Prepared state for the next product lane.

#### Responsibilities
- indicate which blocks are ready for scene matching;
- classify matching expectations;
- expose missing film-side prerequisites.

#### Main zones
- block readiness table;
- missing asset warnings;
- matching-type indicators.

### S-06 Output Tracks Overview
Prepared state that shows how the project branches into content outputs.

#### Responsibilities
- long video view;
- shorts / reels view;
- carousel view;
- packaging view.

#### Main zones
- track cards;
- block-to-track summary;
- readiness by output type.

### S-07 Export Center
Prepared later-phase delivery screen.

#### Responsibilities
- group output assets;
- show packaging completeness;
- export files and project artifacts.

## Navigation model

### Primary left navigation
- Project Home
- Source Intake
- Semantic Map
- Matching Prep
- Output Tracks
- Export Center

### Rule
Unavailable later-phase screens should still be visible if they help orientation, but they must show bounded `not ready yet` states rather than pretending to be implemented.

## MVP screen priority

### Must exist in MVP
- S-01 Project Home
- S-02 Source Intake
- S-03 Semantic Map Workspace
- S-04 Block Detail / Inspector

### May exist as bounded non-implemented placeholders
- S-05 Matching Preparation
- S-06 Output Tracks Overview
- S-07 Export Center

## Main desktop relationship

The MVP should not behave like a generic timeline editor. The main desktop surface is the Semantic Map Workspace, with Project Home and Source Intake as feeders into it.
