# Project Intake

Last updated: 2026-04-06
Status: active

## Module purpose

Define the boundary where a new DNA Film Content Engine project receives its source materials and turns them into a normalized intake state that downstream semantic work can use.

This module owns entry into the system. It does not own semantic transformation, scene matching, or execution-layer processing.

## Relationship to adjacent layers

- Product/interface behavior for intake is described in `02_PRODUCT/USER_FLOWS.md`, `02_PRODUCT/SCREEN_MAP.md`, and `02_PRODUCT/MVP_DESKTOP_INTERFACE.md`.
- Domain entities used by intake are defined in `04_TECH/DOMAIN_MODEL.md`.

This document defines the logical contract between product-facing intake behavior and downstream semantic processing.

## Accepted inputs

## Required MVP input
- `Analysis Text`

## Optional MVP inputs
- film file;
- prepared film asset set;
- subtitles;
- transcript;
- notes;
- reference stills or related editorial attachments;
- film title and project metadata.

## Input categories

### Text analysis
Primary semantic source for MVP.

### Film asset
Any attached media artifact related to the film that may support later matching or downstream validation.

### Subtitles
Time-linked dialogue/support artifact that may help later scene matching or film evidence review.

### Transcript
Textual film-side support artifact distinct from the analysis text.

### Metadata
Project-level identifying information such as film title, language, and intended output emphasis.

## Required vs optional inputs

### Required for meaningful MVP work
- a created `Project`;
- one primary `Analysis Text`.

### Optional but useful
- film-side materials;
- subtitles;
- transcript;
- notes;
- additional metadata that improves later orientation.

### Not required for semantic-map work
- complete film ingest;
- subtitles;
- transcript;
- downstream publishing metadata;
- rendering assets.

## Intake normalization logic

The intake module should normalize incoming project material into a stable project-ready source package.

## Normalization responsibilities
- identify the artifact category of each input;
- distinguish semantic source from film-side support inputs;
- mark one primary `Analysis Text` for MVP use;
- attach optional film-side materials without pretending they are semantically equivalent to the analysis source;
- record missing optional inputs without falsely blocking semantic work;
- produce a project-level intake readiness view.

## Normalized intake output

The output of intake is not a rendered asset set or runtime job.

It is a normalized project source state containing:
- project identity;
- primary analysis text;
- categorized optional film-side inputs;
- source completeness markers;
- intake readiness status;
- warnings for missing but non-blocking support materials.

## Readiness implications

### Ready for semantic work
The project is ready for downstream semantic work when:
- the project exists;
- the analysis text is present and accepted as the primary semantic source.

### Warning state
The project may remain usable for semantic work while warning that:
- film-side assets are absent;
- subtitles are absent;
- transcript is absent;
- metadata is partial.

### Blocked state
The project is blocked for meaningful downstream semantic work when:
- no analysis text is present;
- the source text is unusable or not recognized as analysis input;
- the project container does not exist.

### Downstream effect
- lack of analysis text blocks the semantic engine;
- lack of film-side material may not block semantic structuring but may weaken or delay later scene matching.

## What the module produces for downstream use

The intake module hands downstream consumers:
- a valid `Project`;
- the primary `Analysis Text`;
- normalized source classifications for optional attached materials;
- intake warnings and readiness markers;
- enough project identity to preserve continuity across later stages.

## Downstream consumers

Primary downstream consumer:
- `DNA_SEMANTIC_ENGINE`

Secondary later consumer:
- `SCENE_MATCHING`

## Non-goals

- no semantic interpretation of analysis meaning beyond identifying the primary text source;
- no scene matching;
- no automatic film downloading;
- no transcript alignment logic;
- no media pipeline execution;
- no export preparation;
- no database or API design.

## Edge cases / invalid states

### Multiple candidate text inputs

Problem:
- the project may contain more than one text artifact.

Required handling:
- intake must distinguish the primary analysis text from transcript or notes;
- if ambiguity remains, the system should require explicit human clarification rather than silently guessing.

### Film asset present without analysis text

Meaning:
- project has media-side material but lacks the semantic source required for MVP meaning-first work.

State:
- warning or blocked for semantic progression.

### Analysis text present but malformed or incomplete

Meaning:
- the project may technically contain text but not enough usable semantic source material.

State:
- blocked or warning depending on severity;
- human clarification remains required.

### Transcript mistaken for analysis text

Meaning:
- film-side transcript is present, but the system should not silently elevate it to the primary semantic source.

State:
- invalid or ambiguous until clarified.

### Optional support materials missing

Meaning:
- semantic work can proceed, but later matching confidence may be reduced.

State:
- warning, not block, unless a later module explicitly depends on those inputs.
