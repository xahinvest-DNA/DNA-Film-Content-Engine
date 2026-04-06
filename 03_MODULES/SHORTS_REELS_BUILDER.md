# Shorts / Reels Builder

Last updated: 2026-04-06
Status: active

## Module purpose

Define the downstream module boundary that turns approved semantic intent plus accepted scene/timecode evidence into short-form output units.

This module owns short-form unitization logic at conceptual level, not runtime publishing or render execution.

## Upstream dependencies

Required upstream dependencies:
- approved semantic blocks or approved semantic subsets;
- accepted scene references;
- usable timecode ranges.

Optional supporting inputs:
- rough cut segment references;
- packaging notes;
- project-level output priorities.

## Input contract

The module receives:
- project identity;
- upstream semantic references;
- upstream scene/timecode references;
- review and readiness markers;
- optional cues for emphasis or hook orientation.

## Output contract

The module produces:
- one or more shorts/reels output unit records;
- unit-level readiness and review markers;
- output-facing records suitable for later packaging/export grouping.

## Unitization logic at conceptual level

A short/reel unit is one bounded downstream artifact built around one sharp semantic point or one tightly coherent cluster of points.

The unit should preserve:
- semantic clarity;
- enough approved evidence material to support the point;
- independence as a short-form artifact.

## Distinction between short unit and long-form segment

A long-form segment remains part of broader narrative continuity.

A short/reel unit must stand as its own output-facing artifact and therefore cannot be treated as merely a detached long-form segment.

## Platform-agnostic boundary logic

This module defines short-form output boundaries in a platform-agnostic way.

It may later feed YouTube Shorts, Instagram Reels, or similar channels, but it does not own channel-specific publishing behavior.

## Review points

Human review is required for:
- whether the unit is coherent as a short-form artifact;
- whether the semantic point is sufficiently sharp;
- whether supporting scene/timecode material is persuasive enough;
- whether the unit is ready for packaging/export grouping.

## Non-goals

- no platform publishing spec;
- no channel connector logic;
- no runtime render backend;
- no encoding/transcoding behavior;
- no distribution automation.

## Deferred runtime concerns

- final vertical-video execution details;
- export templates;
- channel-specific formatting rules in runtime form;
- render scheduling and delivery.
