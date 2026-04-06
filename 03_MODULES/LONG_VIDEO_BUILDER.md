# Long Video Builder

Last updated: 2026-04-06
Status: active

## Module purpose

Define the downstream module boundary that turns approved semantic continuity plus accepted scene/timecode material into one long-form output-facing record.

This module owns long-form output structuring, not runtime rendering.

## Upstream dependencies

Required upstream dependencies:
- approved semantic blocks;
- accepted scene references;
- approved or usable timecode ranges.

Strong supporting upstream artifacts:
- rough cut segments where available;
- project-level review markers;
- packaging relevance notes.

## Required prerequisites

The module becomes meaningfully usable when:
- semantic continuity is approved enough to support a long-form narrative;
- enough scene/timecode evidence exists to support that continuity;
- downstream assembly is not blocked by unresolved core review issues.

## Input contract

The module receives:
- project identity;
- ordered semantic block references;
- accepted scene reference records;
- associated timecode range records;
- rough cut segment references where available;
- review and readiness markers.

## Output contract

The module produces:
- one or more long-form output records;
- ordered long-form structure references;
- readiness and review markers for long-form outputs;
- output-facing handoff suitable for packaging/export grouping.

## Role of rough cut segments, approved scene references, and semantic continuity

### Semantic continuity
Owns the meaning flow of the long-form output.

### Approved scene references and timecodes
Provide the accepted evidence material that supports that flow.

### Rough cut segments
Function as downstream assembly units that help stabilize long-form structure, but the long-form output record is stronger than a raw segment list.

## Review points

Human review is required for:
- long-form continuity quality;
- whether selected scene/timecode material supports the intended meaning;
- whether the output is ready to move into packaging/export grouping.

## Non-goals

- no runtime timeline implementation;
- no render backend;
- no encoding logic;
- no export execution;
- no publishing automation.

## Deferred runtime concerns

- final timeline serialization;
- render scheduling;
- preview generation;
- encoding parameters;
- delivery mechanics.
