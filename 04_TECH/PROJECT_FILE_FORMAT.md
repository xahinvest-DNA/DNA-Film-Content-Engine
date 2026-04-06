# Project File Format

Last updated: 2026-04-06
Status: active

## Purpose

Define the first stable local project-package boundary for DNA Film Content Engine.

This document describes how one project should be organized on disk so the approved product, domain, and schema layers can be persisted locally without pretending that a full runtime serialization system is already finalized.

## Scope

This document covers:
- local-first project-package assumptions;
- canonical project root structure;
- required versus optional files and folders;
- distinctions between source, metadata, editable records, derived artifacts, and generated outputs;
- compatibility considerations for future packets.

This document does not cover:
- binary container formats;
- database embedding decisions;
- sync architecture;
- cloud storage design;
- runtime watchers or background workers.

## Relationship to data schema

`04_TECH/DATA_SCHEMA.md` defines the persistence-facing record layer.

This document defines how those records and related asset references should be organized inside one local project package.

Important rule:
- the project package is a local boundary;
- it is not a claim that a final serialization/runtime format is fully decided.

## Project package philosophy

One project should behave as one local package that keeps together:
- source materials;
- editable project records;
- derived working artifacts;
- generated outputs;
- package-level metadata.

The package should support meaning-first progression while preserving clear separation between:
- human-authored inputs;
- editable project state;
- machine-derived artifacts;
- output-facing generated results.

## Local-first assumptions

- a project should remain meaningful and inspectable on local disk;
- core project identity and editable state should not depend on a remote service;
- missing later-phase folders should not invalidate an early-stage project;
- the package should allow incremental growth from intake through later downstream stages.

## Canonical project root structure

One valid local project package may be organized as:

- `/project.manifest`
- `/project.meta/`
- `/sources/`
- `/records/`
- `/derived/`
- `/outputs/`
- `/logs/` optional

The exact file extensions may be finalized later, but the structural separation should remain stable.

## Required files

### `project.manifest`

Role:
- top-level project identity and compatibility entry point.

Must include conceptually:
- project id;
- project format version;
- project title or working title;
- primary record entry references;
- basic compatibility marker.

### `project.meta/`

Role:
- package metadata zone for non-content coordination files.

Minimum expectation:
- project status/readiness summary;
- local compatibility markers;
- references to canonical editable records.

### `records/`

Role:
- canonical editable project records zone.

Must be able to hold:
- project record;
- intake package record;
- analysis source record;
- semantic block records;
- review state records;
- later matching and downstream records as they become available.

## Optional files and folders

### `sources/`

Role:
- human-authored or externally acquired source materials.

May contain:
- analysis text files;
- film assets;
- subtitles;
- transcript files;
- notes;
- reference stills.

### `derived/`

Role:
- machine-derived or system-derived working artifacts not treated as primary human-authored sources.

May contain:
- proposed semantic derivatives;
- matching candidate artifacts;
- provisional timecode artifacts;
- later derived assembly intermediates.

### `outputs/`

Role:
- later-phase generated or export-facing content artifacts.

May remain absent or empty in early project stages.

### `logs/`

Role:
- optional local trace or process-support area.

Not required for a valid early-stage project.

## Asset folders, working folders, and generated folders

### Source area
- `/sources/analysis/`
- `/sources/film/`
- `/sources/subtitles/`
- `/sources/transcripts/`
- `/sources/notes/`

### Editable records area
- `/records/project/`
- `/records/intake/`
- `/records/semantic/`
- `/records/review/`
- `/records/matching/`
- `/records/output/`

### Derived working area
- `/derived/semantic/`
- `/derived/matching/`
- `/derived/timecodes/`
- `/derived/assembly/`

### Generated output area
- `/outputs/long/`
- `/outputs/shorts/`
- `/outputs/carousel/`
- `/outputs/packaging/`
- `/outputs/export/`

## Metadata and manifest boundaries

### Manifest boundary

The top-level manifest should remain light and orientation-focused.

It should not duplicate the full project state or become a shadow database.

### Metadata boundary

Package metadata should support:
- compatibility;
- package integrity;
- high-level state discovery.

It should not replace canonical editable records stored in `records/`.

## Valid project conditions

### Minimum valid project

A minimum valid project package should have:
- `project.manifest`
- `project.meta/`
- `records/`
- enough source or record content to identify one project and one primary analysis source.

### Early-stage allowed absences

The following may be absent or incomplete without invalidating an early-stage project:
- film assets;
- subtitles;
- transcripts;
- matching artifacts;
- outputs;
- generated exports.

### Blocking invalidity

A project package becomes structurally invalid when:
- no manifest exists;
- no canonical records area exists;
- no path exists to identify the project and its primary semantic source.

## Versioning / compatibility considerations

The package format should support:
- explicit project format versioning;
- later compatibility migration if record structures evolve;
- bounded optional expansion without invalidating old early-stage projects.

Compatibility should be treated as a manifest- and metadata-level concern first, not as a runtime migration engine decision.

## Non-goals

- no final serialization syntax commitment;
- no cloud sync format;
- no remote collaboration protocol;
- no asset deduplication engine;
- no runtime file watcher behavior;
- no binary media processing design.

## Deferred runtime concerns

- exact extension choices for record and manifest files;
- caching strategy;
- large media reference handling;
- integrity verification routines;
- autosave and recovery mechanics;
- future migration tooling.
