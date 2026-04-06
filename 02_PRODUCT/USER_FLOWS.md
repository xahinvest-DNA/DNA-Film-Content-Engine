# User Flows

Last updated: 2026-04-06
Status: active

## Purpose

Define the core desktop-first user journeys for DNA Film Content Engine so the interface can be designed around real operator flows rather than abstract feature lists.

## Primary user

The primary user is an editor-analyst working with Communication DNA style film analysis who wants to transform one analysis into multiple content outputs with high control and strong automation support.

## Core operating principle

The product should move the user through meaning-first states:

1. create project;
2. load source materials;
3. structure analysis into semantic blocks;
4. review and refine the semantic map;
5. prepare scene-matching work;
6. build output variants;
7. package and export content.

## Flow A - Create project

### Goal
Start a new content project around one film.

### User actions
- create a new project;
- enter project name;
- define film title;
- select working language;
- choose intended output focus: long video, shorts, carousel, or full pack.

### System responsibilities
- create the project container;
- show project status as `draft`;
- route the user into source loading.

### Completion state
Project exists and is ready for source ingest.

## Flow B - Load source materials

### Goal
Attach the core inputs needed to start work.

### User actions
- paste or upload analysis text;
- optionally attach film file, subtitles, transcript, notes, or reference assets.

### System responsibilities
- validate text presence;
- register asset types;
- mark missing but optional inputs clearly;
- route the user into analysis structuring even if film assets are not yet attached.

### Completion state
The project contains the minimum viable source set for semantic work.

## Flow C - Build semantic map

### Goal
Turn the raw analysis into structured semantic blocks.

### User actions
- review the raw text split;
- merge, split, rename, or reorder blocks;
- assign block roles where needed;
- flag strong candidate blocks for long video, short video, or carousel.

### System responsibilities
- propose initial semantic blocks;
- show each block with title, text, role, and output suitability;
- preserve edit history at the project level.

### Completion state
A project-level semantic map exists and is editor-approved.

## Flow D - Review semantic map as the main operating surface

### Goal
Use the semantic map as the main control surface before scene work.

### User actions
- inspect the full map;
- check whether the analysis has gaps, overload, repetition, or weak transitions;
- select which blocks belong to which output tracks.

### System responsibilities
- show the semantic map in a scannable desktop layout;
- expose block importance, output suitability, and current status;
- show what is ready and what is missing.

### Completion state
The user can move from semantic control into scene-matching preparation with confidence.

## Flow E - Prepare scene matching

### Goal
Prepare the project for later text-to-scene alignment.

### User actions
- confirm which blocks require visual proof scenes;
- classify which blocks are explanatory, emotional, symbolic, or packaging-only.

### System responsibilities
- expose matching readiness per block;
- mark which blocks need film assets;
- show whether the project can proceed to matching or still lacks required media inputs.

### Completion state
The project is structurally ready for scene matching.

## Flow F - Build output tracks

### Goal
Turn one semantic project into multiple output-oriented tracks.

### Output tracks
- Long Video Track
- Shorts / Reels Track
- Carousel Track
- Packaging Track

### User actions
- select a track;
- inspect which semantic blocks feed that track;
- disable or duplicate blocks where needed;
- adjust order and emphasis.

### System responsibilities
- preserve one shared semantic source with track-specific views;
- avoid duplicating the project into separate disconnected workflows.

### Completion state
The user can see how one analysis becomes several content forms.

## Flow G - Package and export

### Goal
Collect final deliverables and metadata for publishing use.

### User actions
- review outputs;
- approve packaging units;
- export project assets.

### System responsibilities
- show output readiness;
- group exports by platform and asset type;
- preserve project history.

### Completion state
The project has exportable content assets.

## Flow priority for MVP

The MVP must strongly support Flows A through D.

Flows E through G may be represented as prepared future-facing product states, but should not force heavy engine implementation into the first desktop cycle.
