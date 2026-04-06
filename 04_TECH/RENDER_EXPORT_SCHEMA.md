# Render/Export Schema

Last updated: 2026-04-06
Status: active

## Purpose

Define the first stable render/export-facing schema layer for DNA Film Content Engine.

This document extends `04_TECH/DATA_SCHEMA.md` into downstream output-specific record families so approved semantic, scene-reference, and timecode artifacts can become output-ready structures without implying that runtime rendering or export execution already exists.

## Scope

This document covers:
- downstream output-facing record families;
- identity rules for long-form, short-form, carousel, packaging, and export-group records;
- review/readiness representation for downstream outputs;
- boundaries between output records and export-group artifacts.

This document does not cover:
- runtime rendering;
- encoding/transcoding settings;
- render queues;
- background jobs;
- API/backend contracts;
- platform publishing automation.

## Relationship to `DATA_SCHEMA.md` and `PROJECT_FILE_FORMAT.md`

`04_TECH/DATA_SCHEMA.md` already defines the generic record layer, including:
- `Output unit reference record`
- `Packaging / export preparation record`

This document resolves how that generic layer should split into downstream-specific output families.

`04_TECH/PROJECT_FILE_FORMAT.md` defines where downstream records and generated outputs may live inside one local project package.

Important rule:
- this schema layer defines output-facing records and package boundaries;
- it does not define how runtime rendering or export execution is implemented.

## Render/export schema principles

### Continue the approved schema, do not replace it

This document refines the generic output layer from `DATA_SCHEMA.md` rather than creating a competing schema model.

### Output records are still meaning-first artifacts

Downstream records must remain traceable to approved semantic intent and accepted scene/timecode material.

### Ready-for-export is not the same as rendered

A downstream record may be considered export-ready at schema level even when no runtime render has happened yet.

### Package grouping is distinct from individual output identity

Individual output records and package-level export groups must remain separate record families.

## Output record families

## Long-form output record

### Role
Canonical downstream record for one long-form analytical video artifact.

### Derived from
- approved semantic continuity
- accepted scene references
- timecode ranges
- rough cut segments where available

### Required field groups
- `project_id`
- `long_output_id`
- title or working label
- ordered upstream segment references
- ordered semantic block references
- readiness state
- review state

### Record character
- downstream output-facing
- editorially reviewable
- export-facing but not yet runtime-rendered

## Shorts / Reels output unit record

### Role
Canonical downstream record for one short-form output unit.

### Derived from
- selected semantic intent
- accepted scene/timecode evidence
- short-form unitization choices

### Required field groups
- `project_id`
- `short_unit_id`
- source semantic references
- source scene/timecode references
- unit purpose or hook label
- readiness state
- review state

### Record character
- downstream output-facing
- unit-level, not project-level aggregate
- export-facing but not yet runtime-rendered

## Carousel output unit record

### Role
Canonical downstream record for one carousel artifact.

### Derived from
- approved semantic blocks
- condensed semantic sequencing
- optional scene references where they add supporting value

### Required field groups
- `project_id`
- `carousel_unit_id`
- ordered slide/card structure
- upstream semantic references
- optional scene/timecode references
- readiness state
- review state

### Record character
- downstream output-facing
- non-video output family
- export-facing but not yet runtime-rendered

## Packaging bundle record

### Role
Canonical package-level grouping record for titles, hooks, captions, CTA variants, thumbnail text, and related publication support assets.

### Derived from
- one or more downstream output records
- approved semantic intent
- packaging-specific editorial decisions

### Required field groups
- `project_id`
- `packaging_bundle_id`
- linked output record references
- packaging asset references
- completeness marker
- review/approval state

### Record character
- package-level grouping artifact
- editorially reviewable
- not itself a rendered media output

## Export set / export preparation record

### Role
Top-level export-facing grouping record that collects one or more downstream output records and packaging bundles into a release-ready boundary.

### Required field groups
- `project_id`
- `export_set_id`
- included output record references
- included packaging bundle references
- export readiness marker
- approval marker

### Record character
- grouping artifact
- export-facing boundary record
- not a runtime job definition

## Output-unit identity rules

Each downstream output-facing record should preserve:
- project identity;
- output-family-specific id;
- upstream semantic linkage;
- upstream scene/timecode linkage where relevant;
- readiness marker;
- review state.

Preferred conceptual ids:
- `long_output_id`
- `short_unit_id`
- `carousel_unit_id`
- `packaging_bundle_id`
- `export_set_id`

## Long-form vs short-form vs carousel vs packaging distinctions

### Long-form output
- preserves broader semantic continuity across multiple segments;
- is not just a loose set of approved clips.

### Short-form output
- is a self-contained short unit derived from a tighter semantic point;
- is not merely one long-form segment copied into a new slot.

### Carousel output
- is a slide/card structure rather than a time-based video artifact;
- remains grounded in semantic sequencing first.

### Packaging bundle
- groups publication-support assets around outputs;
- is not itself a long-form, short-form, or carousel content record.

## Readiness / review representation for downstream outputs

Downstream output records should support at least:
- `in_progress`
- `ready_for_review`
- `approved`
- `blocked`
- `ready_for_export`

Review markers should make visible:
- whether the output structure is editor-reviewed;
- whether packaging completeness is sufficient;
- whether the export set is complete enough for downstream execution.

## Export-bundle boundaries

### Individual output record
Represents one output artifact family member.

### Packaging bundle
Represents grouped publication-support assets linked to one or more outputs.

### Export set
Represents the top-level export-ready grouping boundary for downstream runtime/export stages.

Important distinction:
- export readiness at schema level means structural completeness;
- it does not imply that a render or export process has already run.

## Non-goals

- no codec settings;
- no renderer internals;
- no ffmpeg-like command design;
- no background job definitions;
- no API contracts;
- no backend/export service design.

## Deferred runtime concerns

- actual rendering workflow;
- media encoding pipeline;
- export queue semantics;
- artifact delivery mechanics;
- publishing connectors;
- execution monitoring and retries.
