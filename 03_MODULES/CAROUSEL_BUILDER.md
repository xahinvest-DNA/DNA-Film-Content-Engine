# Carousel Builder

Last updated: 2026-04-06
Status: active

## Module purpose

Define the downstream module boundary that turns approved semantic structure into carousel output units.

This module owns slide/card-level output logic at conceptual level, not runtime graphic generation or publishing automation.

## Upstream inputs

Required upstream inputs:
- approved semantic blocks;
- semantic ordering and review markers.

Optional supporting inputs:
- accepted scene references;
- timecode ranges where they help support slide content;
- packaging notes.

## Input contract

The module receives:
- project identity;
- approved semantic references;
- optional supporting scene/timecode references;
- review and readiness markers.

## Output contract

The module produces:
- one or more carousel output unit records;
- ordered card/slide structures;
- readiness and review markers;
- output-facing records suitable for packaging/export grouping.

## Card/slide-level output logic at conceptual level

A carousel unit is one bounded sequence of cards/slides that expresses a semantic progression in non-video form.

Minimum structure should preserve:
- opening frame or title logic;
- ordered body-card progression;
- closing or takeaway structure.

## Relation to semantic blocks

Carousel output remains primarily semantic-first.

Semantic blocks provide the main source structure, sequencing logic, and editorial meaning boundary for each carousel unit.

## Relation to scene/timecode artifacts where relevant

Scene/timecode artifacts may support carousel output, but they are secondary.

They do not redefine carousel as a video artifact and should be used only where they strengthen downstream structure.

## Review points

Human review is required for:
- semantic clarity across the card sequence;
- whether the slide progression is coherent;
- whether the carousel unit is complete enough for packaging/export grouping.

## Non-goals

- no visual template engine;
- no slide renderer implementation;
- no publishing automation;
- no platform connector behavior;
- no runtime graphics generation.

## Deferred runtime concerns

- final slide layout rendering;
- image/text composition execution;
- asset template systems;
- export scheduling and packaging delivery.
