# Scene Matching

Last updated: 2026-04-06
Status: active

## Module purpose

Define the logical boundary where approved semantic meaning is connected to film-side evidence.

This module does not own runtime matching algorithms. It owns the logical contract between semantic units and usable scene-reference artifacts.

## Relationship to adjacent layers

- upstream semantic output is defined in `03_MODULES/DNA_SEMANTIC_ENGINE.md`;
- relevant entities are defined in `04_TECH/DOMAIN_MODEL.md`;
- this module prepares later downstream cut-building and output-assembly layers without designing them in runtime detail.

## Upstream inputs

Required upstream inputs:
- valid `Project`;
- semantic blocks prepared by the semantic engine;
- project-level readiness showing that semantic work is ready enough for matching.

Optional supporting inputs:
- film assets;
- subtitles;
- transcript;
- semantic notes about required proof, symbolism, emotion, or explanation.

## Required prerequisites

The module becomes meaningfully usable when:
- semantic blocks exist in reviewable or approved form;
- film-side material or references exist at a level sufficient to attempt matching.

The module may remain logically visible before full readiness, but a successful matching pass should not be assumed without both semantic input and some film-side support.

## Matching outputs

The module may produce:
- `Match Candidates`;
- accepted `Scene References`;
- associated `Timecode Ranges`;
- confidence or strength markers;
- review states describing whether a proposed match is usable, weak, ambiguous, or rejected.

## Match confidence / strength levels

The exact scale may evolve later, but the module should support at least these distinctions:

### Strong
- direct and persuasive support for the semantic unit;
- likely usable with minimal editorial correction.

### Plausible
- meaningful support exists, but the connection may still require editorial judgment.

### Weak
- some relation exists, but it is indirect, fragile, or easy to misread.

### Ambiguous
- multiple plausible matches exist or no single choice is clearly preferable.

### Rejected
- candidate is not suitable for downstream use.

## Match candidate vs accepted scene reference

### Match Candidate

Definition:
- proposed semantic-to-scene relationship not yet trusted as final downstream input.

Properties:
- may carry confidence, ambiguity, notes, and tentative timecode information;
- may be revised, compared, or rejected.

### Accepted Scene Reference

Definition:
- scene-side artifact considered usable after enough human confirmation or confidence.

Properties:
- suitable for later cut-building or output derivation;
- may include confirmed `Timecode Range` artifacts;
- serves as the downstream handoff contract.

## Role of human validation

Human validation remains central because meaning-to-scene alignment is editorial, not purely mechanical.

Human review is required for:
- resolving ambiguity between multiple candidates;
- rejecting visually attractive but semantically weak matches;
- confirming whether a candidate is persuasive enough to become a scene reference;
- approving timecode usefulness for downstream assembly.

## What counts as a usable match artifact

A usable downstream artifact should provide:
- a clear connection to one or more semantic blocks;
- a scene-side reference that an editor can understand and reuse;
- enough temporal or structural specificity to support later assembly;
- a review state showing whether it is accepted, provisional, or unresolved.

Usable does not mean fully automated or final-cut ready. It means reliable enough to become downstream input.

## Timecode artifacts as result layer

`Timecode Range` should appear as a result artifact of matching work, not as the module's primary identity.

Meaning:
- matching exists to connect meaning with evidence;
- timecodes serve that connection by making it operationally reusable downstream.

## Downstream handoff

Primary downstream handoff consists of:
- semantic block identity;
- accepted scene reference;
- associated timecode range where available;
- confidence/review markers;
- notes needed for later assembly judgment.

Intended downstream consumers:
- rough-cut building layers;
- short-form derivation layers;
- later packaging or proof-selection workflows.

## Non-goals

- no runtime scene-detection implementation;
- no computer-vision execution design;
- no transcript-alignment algorithm design;
- no render/export behavior;
- no automatic publishing logic;
- no final edit assembly logic;
- no UI implementation for matching screens.

## Deferred execution concerns

The following are intentionally deferred:
- exact matching algorithms;
- use of embeddings, transcripts, subtitles, or multimodal models;
- ranking formulas;
- storage model for candidates and references;
- batch processing and job orchestration;
- caching, retries, and execution observability.
