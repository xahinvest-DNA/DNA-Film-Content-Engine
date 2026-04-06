# Asset Pipeline

Last updated: 2026-04-06
Status: active

## Purpose

Define asset classification, asset states, and module handoff boundaries for DNA Film Content Engine without designing the runtime media pipeline.

This document exists to clarify what assets the system works with, where responsibility changes between modules, and how asset state affects downstream readiness.

## Scope

This document covers:
- asset categories;
- source vs normalized vs derived distinctions;
- asset lifecycle states;
- module handoff boundaries;
- readiness and validation implications;
- human review checkpoints.

This document does not cover:
- transcoding;
- indexing;
- shot detection;
- frame extraction;
- model execution;
- batch processing;
- render/export runtime behavior.

## Asset categories

### Analysis source assets
- primary analysis text;
- attached editorial notes that support semantic interpretation.

### Film-side source assets
- film file;
- prepared clip set;
- reference stills.

### Text-support film assets
- subtitles;
- transcripts.

### Canonical record assets
- project records;
- intake records;
- semantic records;
- review records;
- matching records.

### Derived working assets
- semantic derivation artifacts;
- match candidate artifacts;
- provisional timecode artifacts;
- later assembly intermediates.

### Output-facing assets
- rough-cut outputs;
- short-form outputs;
- carousel outputs;
- packaging artifacts;
- export bundles.

## Source vs normalized vs derived asset distinctions

### Source assets

Definition:
- human-authored or externally acquired inputs attached to the project.

### Normalized assets

Definition:
- project-attached materials that have been classified, registered, and made stable for downstream module use.

### Derived assets

Definition:
- artifacts produced from source or normalized assets during semantic, matching, or later downstream work.

### Review-approved assets

Definition:
- records or artifacts that have passed an explicit human confirmation point and are trusted enough for downstream use.

## Asset lifecycle states

The conceptual asset states should include:
- attached
- classified
- normalized
- in_review
- approved
- rejected
- missing
- optional_missing
- blocking_missing

## Module handoff boundaries

## Intake boundary

`PROJECT_INTAKE` owns:
- receiving source assets;
- classifying them;
- marking the primary analysis text;
- creating normalized intake references;
- exposing readiness warnings.

## Semantic boundary

`DNA_SEMANTIC_ENGINE` consumes:
- normalized project intake state;
- primary analysis text;
- supporting notes and metadata.

`DNA_SEMANTIC_ENGINE` produces:
- semantic block records;
- semantic review markers;
- ambiguity markers relevant to downstream use.

## Scene matching boundary

`SCENE_MATCHING` consumes:
- approved or reviewable semantic records;
- available film-side source references;
- subtitles/transcripts when present;
- project readiness markers.

`SCENE_MATCHING` produces:
- match candidates;
- accepted scene references;
- timecode-facing result artifacts;
- confidence and review markers.

## Validation and readiness implications

### Analysis text missing
- blocks semantic work;
- therefore blocks all meaning-first downstream stages.

### Film asset missing
- does not necessarily block semantic work;
- may block or weaken meaningful scene matching.

### Subtitles/transcript missing
- usually warning rather than immediate block;
- may reduce matching quality or review speed.

### Semantic approval missing
- blocks strong downstream matching handoff.

### Accepted scene reference missing
- downstream cut-building or proof-based output assembly cannot proceed confidently.

## Human review checkpoints

Human review remains required at these asset-relevant boundaries:
- confirmation that the primary analysis source is correctly identified;
- approval of semantic block structure;
- acceptance or rejection of match candidates;
- approval that a scene reference and timecode are usable downstream;
- later confirmation that output-facing assets are ready for export grouping.

## Non-goals

- no transcoding rules;
- no file hashing strategy;
- no scene-detection pipeline;
- no multimodal execution design;
- no render queue;
- no export backend;
- no publication automation logic.

## Deferred execution concerns

- asset indexing mechanics;
- media proxy generation;
- large-file storage behavior;
- checksum/integrity enforcement;
- processing jobs and retries;
- performance optimization;
- distributed execution concerns.
