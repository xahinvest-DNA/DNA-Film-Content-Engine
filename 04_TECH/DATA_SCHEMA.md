# Data Schema

Last updated: 2026-04-06
Status: active

## Purpose

Define the first stable persistence-facing schema layer for DNA Film Content Engine.

This document translates the approved domain model into canonical record structures that later implementation packets can rely on without committing the project to a database engine, API shape, or runtime pipeline design.

## Scope

This document covers:
- stable record families for core project entities;
- identity rules;
- shared metadata conventions;
- readiness and review representation;
- distinctions between source, editable, derived, and handoff records.

This document does not cover:
- SQL or database-specific design;
- JSON schema syntax;
- API resources;
- job orchestration;
- runtime execution behavior;
- low-level serialization mechanics.

## Relationship to domain model

`04_TECH/DOMAIN_MODEL.md` defines canonical entities and their relationships.

This document defines how those entities should be represented as stable records.

Important rule:
- domain entities are logical truths;
- schema records are persistence-facing structures that represent those truths;
- UI representations are separate and must not be treated as canonical record definitions.

## Schema design principles

### Domain-led, not UI-led

Schema must follow the approved meaning-first domain model rather than mirror screen layout or UI components.

### Stable identity before deep implementation

Every canonical or handoff-relevant record should have a durable identity rule before runtime packets begin.

### Source vs derived must remain explicit

The schema should always preserve whether a record is:
- source;
- normalized;
- derived;
- review-approved;
- output-facing.

### Editorial mutability must remain visible

Schema should distinguish records that remain human-editable from records that are generated or merely referenced.

### Handoff clarity matters more than storage optimization

The primary goal of this layer is continuity between intake, semantic, matching, and later assembly stages.

## Identity rules

### Global rule

Each record that participates in module handoff should have:
- a stable record id;
- a parent project id;
- a record type;
- creation/update metadata;
- readiness or review markers when relevant.

### Preferred identity pattern

The exact serialization may vary later, but the conceptual identity fields should include:
- `project_id`
- `record_id`
- `record_type`
- `created_at`
- `updated_at`

### Human-authored source identity

Source records should preserve:
- origin type;
- source filename or source label when applicable;
- whether the source is canonical or supporting.

### Derived record identity

Derived records should preserve:
- upstream source linkage;
- derivation stage;
- current review state;
- whether the record is provisional or approved.

## Shared metadata conventions

The following metadata groups should be available across core records when relevant:

### Identity metadata
- project id
- record id
- type
- parent linkage

### Provenance metadata
- source origin
- upstream record references
- derivation stage

### Editorial metadata
- editable title or label
- notes
- human comments
- review owner or confirmation marker

### State metadata
- readiness marker
- status marker
- warning count or issue flags
- approval state

## Core record types

## Project record

### Role
Top-level canonical project container.

### Canonical
Yes.

### Required field groups
- project identity
- film title / working title
- working language
- project status
- current readiness summary

### Editable/editorial
Yes.

## Intake package record

### Role
Normalized project intake summary used as the persistence-facing handoff from intake into downstream semantic work.

### Canonical
Yes for intake-state representation.

### Required field groups
- project linkage
- primary analysis source reference
- attached source references
- intake readiness
- intake warnings

## Analysis text source record

### Role
Canonical source record for the primary semantic text.

### Canonical
Yes.

### Required field groups
- source identity
- project linkage
- source classification
- canonical-source marker
- text provenance reference
- readiness/validity marker

## Film asset reference record

### Role
Reference record for film-side assets attached to the project.

### Canonical
Yes as a project attachment reference.

### Required field groups
- asset id
- project linkage
- asset class
- source/origin marker
- file/location reference
- validation state

## Subtitle / transcript reference record

### Role
Reference record for text-support film artifacts.

### Canonical
Yes as attached support-source references.

### Required field groups
- asset id
- project linkage
- subtype marker: subtitle or transcript
- file/location reference
- language marker
- readiness/validity state

## Semantic block record

### Role
Canonical structured semantic working record.

### Canonical
Yes.

### Required field groups
- semantic block id
- project linkage
- source text linkage
- block title
- semantic text span or content body
- order / sequence marker
- semantic role classification
- output suitability markers
- review state

### Handoff role
Primary handoff artifact from semantic structuring into matching and later output assembly.

## Semantic review state record

### Role
Persistence-facing review and approval representation for semantic work.

### Canonical
Yes for workflow control.

### Required field groups
- project or block linkage
- review state
- reviewer confirmation marker
- issue summary
- approved/not approved marker

## Match candidate record

### Role
Proposed semantic-to-scene linkage record.

### Canonical
Yes as a derived pre-approval matching artifact.

### Required field groups
- match candidate id
- project linkage
- semantic block linkage
- candidate scene reference linkage
- provisional timecode linkage when available
- confidence level
- review state

## Accepted scene reference record

### Role
Approved or sufficiently trusted scene-side handoff record.

### Canonical
Yes for downstream scene-side usage.

### Required field groups
- scene reference id
- project linkage
- semantic block linkage
- accepted-source linkage
- accepted timecode reference
- acceptance marker
- notes for downstream use

## Timecode range record

### Role
Persistence-facing result record for temporal scene references.

### Canonical
Yes when accepted for downstream use.

### Required field groups
- timecode id
- project linkage
- source asset linkage
- start marker
- end marker
- validity/review marker

## Rough cut segment record

### Role
Downstream assembly record joining semantic intent with accepted scene material.

### Canonical
Derived downstream record.

### Required field groups
- segment id
- project linkage
- semantic block linkage
- scene reference linkage
- timecode linkage
- sequence marker
- readiness state

## Output unit reference record

### Role
Generic persistence-facing record for later output entities such as short units, carousel units, or long-form output structures.

### Canonical
Yes as a shared output-facing record family.

### Required field groups
- output unit id
- project linkage
- output type
- upstream semantic linkage
- readiness state
- review state

## Packaging / export preparation record

### Role
Later-stage record for packaging completeness and export grouping.

### Canonical
Derived later-phase record.

### Required field groups
- package id
- project linkage
- output linkage
- packaging asset references
- export readiness
- review/approval state

## Readiness / status representation

The schema should support stable readiness markers without overfitting them to UI badges.

### Core readiness vocabulary
- empty
- warning
- in_progress
- ready
- blocked
- placeholder

## Review / approval representation

The schema should preserve human-in-the-loop checkpoints explicitly.

### Review markers should support
- proposed
- under_review
- approved
- rejected
- reopened

## Derived vs source record distinctions

### Source records
- Project record
- Analysis text source record
- Film asset reference record
- Subtitle / transcript reference record

### Normalized / coordination records
- Intake package record
- Semantic review state record

### Derived editorial records
- Semantic block record
- Match candidate record
- Accepted scene reference record
- Timecode range record
- Rough cut segment record

### Output-facing derived records
- Output unit reference record
- Packaging / export preparation record

## Schema non-goals

- no database vendor choice;
- no ORM design;
- no endpoint contracts;
- no binary storage strategy details;
- no runtime event model;
- no queue or worker definitions.

## Deferred items

- whether output unit references should split into separate record families for long-form, shorts, carousel, and packaging in later packets;
- exact normalization rules for nested review history;
- serialization format for large text bodies and media references;
- exact compatibility rules between local project files and later runtime storage layers.
