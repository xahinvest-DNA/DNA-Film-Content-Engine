# Domain Model

Last updated: 2026-04-06
Status: active

## Purpose

Define the canonical domain language, core entities, and entity relationships for DNA Film Content Engine.

This document fixes the logical model that sits between the approved product/interface layer and the later execution/runtime layer.

## Scope

This document covers:
- canonical domain entities;
- entity roles and relationships;
- lifecycle and transformation logic across the system;
- distinctions between source, derived, editorial, and output-facing artifacts;
- boundary awareness for later technical packets.

This document does not cover:
- UI layout or navigation behavior;
- runtime orchestration;
- database schema;
- API design;
- media-processing implementation;
- execution algorithms.

## Relationship to product documents

The product/interface layer in `02_PRODUCT/*` defines how the user moves through the system and what operating surfaces exist.

This document defines what those surfaces are actually operating on.

Important rule:
- a domain entity is not the same thing as its interface representation.

Example:
- a `Semantic Block` is a canonical domain object;
- a block card, row, or node inside `Semantic Map Workspace` is only a UI representation of that domain object.

## Domain modeling principles

### Meaning first

The system is organized around meaning before media execution.

Canonical sequence:
`analysis text -> semantic units -> scene references -> timecode artifacts -> content units -> packaging/export`

### Human approval remains explicit

The model must preserve human confirmation points rather than pretending that every transformation is self-validating.

### One project, many derived views

The project should remain one semantic source system that later feeds long video, shorts, carousel, and packaging outputs.

### Domain before runtime

Logical entity boundaries should be fixed before execution-layer decisions such as storage, pipelines, or orchestration.

## Core entities

## Project

### Role
Top-level editorial container for one film-centered content effort.

### Entity type
- canonical container
- editorial and coordination entity

### Holds
- source inputs;
- semantic structures;
- review state;
- downstream content artifacts;
- readiness markers.

## Film Source / Film Asset

### Role
Represents film-side material attached to a project.

### Entity type
- source artifact

### Includes
- film file;
- prepared clip set;
- subtitles;
- transcript;
- reference stills;
- attached notes related to film evidence.

### Distinction
`Film Source` is the logical source category.
`Film Asset` is a concrete attached artifact within that category.

## Analysis Text

### Role
Primary meaning-source document for the project.

### Entity type
- source artifact

### Notes
- this is the canonical source for semantic structuring in MVP;
- transcript and subtitles may support later matching, but they do not replace analysis text as the primary semantic source in MVP.

## Semantic Block

### Role
Canonical structured unit derived from analysis text for editorial semantic control.

### Entity type
- derived artifact
- editorial working entity
- module handoff contract

### Notes
- may contain title, text span, role classification, output suitability, notes, and review state;
- is not identical to any particular UI block representation.

## Claim / Insight / Mechanism Unit

### Role
Semantic meaning subtype that clarifies what kind of statement a semantic block contains.

### Entity type
- derived semantic sub-entity or semantic classification layer

### Use
- helps distinguish whether a block expresses an observation, interpretation, causal mechanism, emotional insight, or argument step.

### Boundary
- this is not necessarily a top-level project object exposed everywhere;
- it may function as a typed semantic layer attached to a `Semantic Block`.

## Match Candidate

### Role
Proposed relationship between a semantic unit and film-side evidence.

### Entity type
- derived artifact
- pre-approval matching artifact

### Notes
- may be strong, weak, ambiguous, or rejected;
- is not yet an accepted scene choice.

## Scene Reference

### Role
Human-usable reference to a film moment, scene, or evidence fragment that is considered suitable for semantic support.

### Entity type
- derived and editorially usable artifact
- downstream contract for cut-building layers

### Distinction
- a `Match Candidate` is a proposal;
- a `Scene Reference` is a usable reference after sufficient review or acceptance.

## Timecode Range

### Role
Explicit temporal address for a film-side reference.

### Entity type
- derived technical-facing artifact
- supporting handoff contract

### Notes
- may exist inside a match candidate or accepted scene reference;
- should be treated as a result artifact, not as the primary semantic object.

## Rough Cut Segment

### Role
Downstream assembly unit that combines semantic intent with accepted scene references and time ranges.

### Entity type
- derived output-building artifact

### Boundary
- outside MVP depth for implementation;
- included here because it is a valid downstream consumer of accepted matching artifacts.

## Short / Clip Unit

### Role
Derived output unit for short-form video.

### Entity type
- output-facing artifact

## Carousel Unit

### Role
Derived slide-based output unit built from condensed semantic structure.

### Entity type
- output-facing artifact

## Packaging Asset

### Role
Support asset that packages downstream content for publication.

### Entity type
- output-facing artifact

### Includes
- title;
- hook;
- caption;
- CTA text;
- thumbnail text;
- short description.

## Export Package

### Role
Grouped delivery artifact for later export behavior.

### Entity type
- output-facing aggregate artifact

## Readiness / Status Marker

### Role
Project-level or entity-level marker that communicates whether work is empty, in progress, ready, blocked, approved, or placeholder-only.

### Entity type
- coordination and workflow entity

### Notes
- used across product and domain layers;
- should not be confused with visual badges or UI states, though UI may represent it.

## Review / Human Confirmation Point

### Role
Explicit checkpoint where an editor validates or rejects a proposed transformation.

### Entity type
- editorial control entity
- trust and boundary contract

### Examples
- semantic map approval;
- match candidate acceptance;
- downstream cut readiness review.

## Entity roles by system function

### Source artifacts
- Project
- Film Source / Film Asset
- Analysis Text

### Derived semantic artifacts
- Semantic Block
- Claim / Insight / Mechanism Unit

### Matching artifacts
- Match Candidate
- Scene Reference
- Timecode Range

### Downstream assembly artifacts
- Rough Cut Segment

### Output-facing artifacts
- Short / Clip Unit
- Carousel Unit
- Packaging Asset
- Export Package

### Workflow and control artifacts
- Readiness / Status Marker
- Review / Human Confirmation Point

## Entity relationships

### Project relationships
- a `Project` contains one primary `Analysis Text` for MVP;
- a `Project` may contain zero or more `Film Assets`;
- a `Project` contains zero or more `Semantic Blocks`;
- a `Project` owns readiness markers and review states;
- a `Project` may later contain multiple downstream output artifacts.

### Analysis-to-semantics relationship
- `Analysis Text` is segmented or transformed into `Semantic Blocks`;
- a `Semantic Block` may carry one or more semantic subtypes such as claim, insight, or mechanism.

### Semantics-to-matching relationship
- a `Semantic Block` may produce zero or more `Match Candidates`;
- each `Match Candidate` may point to one or more `Scene References`;
- a `Scene Reference` may include or depend on one or more `Timecode Ranges`.

### Matching-to-downstream relationship
- accepted `Scene References` and associated `Timecode Ranges` can feed `Rough Cut Segments`;
- selected semantic units may also feed `Short / Clip Units`, `Carousel Units`, and `Packaging Assets`.

### Review relationship
- `Review / Human Confirmation Point` may be attached to semantic approval, match acceptance, or later cut approval;
- a readiness marker may change as a result of that confirmation.

## Lifecycle / transformation chain

### Stage 1 - Intake
- `Project` is created;
- `Analysis Text` becomes the minimum viable semantic source;
- optional `Film Assets` may be attached.

### Stage 2 - Semantic structuring
- `Analysis Text` is transformed into `Semantic Blocks`;
- semantic subtype information such as claim, insight, or mechanism may be attached;
- review points validate whether semantic structure is usable.

### Stage 3 - Scene matching
- `Semantic Blocks` become inputs to matching work;
- the system or editor derives `Match Candidates`;
- accepted candidates become `Scene References` with usable `Timecode Ranges`.

### Stage 4 - Downstream assembly
- accepted references feed `Rough Cut Segments` and later output units;
- semantic structure may also feed short, carousel, and packaging derivatives.

### Stage 5 - Delivery aggregation
- output-facing artifacts may be grouped into an `Export Package`.

## Canonical naming

Use these names as preferred canonical terms:
- `Project`
- `Film Asset`
- `Analysis Text`
- `Semantic Block`
- `Claim / Insight / Mechanism Unit`
- `Match Candidate`
- `Scene Reference`
- `Timecode Range`
- `Rough Cut Segment`
- `Short / Clip Unit`
- `Carousel Unit`
- `Packaging Asset`
- `Export Package`
- `Readiness Marker`
- `Human Confirmation Point`

Avoid generic substitutes when they reduce clarity:
- do not collapse `Semantic Block` into generic `content block`;
- do not collapse `Scene Reference` into generic `media item`;
- do not use UI labels as canonical domain truth.

## In-scope vs out-of-scope entities

### In scope for this packet
- entities needed to support intake, semantic structuring, matching preparation, and downstream architectural continuity;
- entity relationships and handoff contracts;
- approval and readiness concepts.

### Out of scope for this packet
- persistence schema;
- API resources;
- queue jobs;
- GPU/media-processing workers;
- social publication entities;
- recommendation or virality scoring entities;
- cloud collaboration entities.

## Open questions / deferred topics

- whether `Claim / Insight / Mechanism Unit` should remain a subtype layer on `Semantic Block` or become a more explicit secondary entity family in later packets;
- how far `Scene Reference` should separate scene identity from shot-level evidence in later matching packets;
- what exact downstream entity set should be fixed for rough-cut building versus output-specific derivation;
- how readiness markers should map into later technical data schema without overfitting the product layer.
