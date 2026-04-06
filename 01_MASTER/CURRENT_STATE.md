# Current State

Last updated: 2026-04-06
Status: active
Current stage: F-013 semantic review filters and focus cues are completed
Active module: F-014 semantic review next-issue navigation and focus-step controls
Active frontier: F-014 Semantic Review Next-Issue Navigation and Focus-Step Controls
Active question: how to let editors step through the currently focused semantic review set with minimal next/previous controls so issue-driven review moves faster without turning the workspace into a workflow engine or dashboard

## Where the project is now

The repository is initialized and synchronized as a source-of-truth project system.

At this point:

- the repository is initialized as a Project Brain rather than as an unstructured empty code folder;
- the project is defined as a desktop-first Communication DNA content engine centered on film analysis to multi-format content production;
- interface-first product framing is completed through `USER_FLOWS.md`, `SCREEN_MAP.md`, `UX_PRINCIPLES.md`, `CONTENT_OUTPUT_SPEC.md`, and `PLATFORM_RULES.md`;
- MVP desktop interface specification is completed through `MVP_DESKTOP_INTERFACE.md`, `SCREEN_STATES.md`, and `NAVIGATION_BEHAVIOR.md`;
- domain model and module-boundary fixation are completed through `DOMAIN_MODEL.md`, `PROJECT_INTAKE.md`, `DNA_SEMANTIC_ENGINE.md`, and `SCENE_MATCHING.md`;
- data schema, project file format, and asset-pipeline boundaries are completed through `DATA_SCHEMA.md`, `PROJECT_FILE_FORMAT.md`, and `ASSET_PIPELINE.md`;
- render/export-facing schema and downstream output boundaries are completed through `RENDER_EXPORT_SCHEMA.md`, `LONG_VIDEO_BUILDER.md`, `SHORTS_REELS_BUILDER.md`, `CAROUSEL_BUILDER.md`, and `PACKAGING_ENGINE.md`;
- the first bounded MVP implementation slice is real through a local-first runtime that can create a project, accept analysis text, derive semantic blocks, persist them on disk, and inspect them in a desktop-facing semantic workspace;
- the semantic workspace now supports persisted selected-block editing, project-level review state, persisted ordering, approval-readiness visibility, one approval guardrail, explicit reopened-after-change visibility that survives reload, persisted semantic boundary editing through minimal split/merge controls, deterministic completeness / issue visibility across the project and selected-block inspector, and persisted output-suitability review controls for long video, shorts/reels, carousel, and packaging;
- the main MVP operating surface remains fixed as `Semantic Map Workspace`;
- the meaning-first architecture is now explicit across product, domain, schema, project-package, asset, downstream output, and implementation layers;
- the project now uses a manager-led execution model;
- ChatGPT owns strongest-next-step selection;
- Codex owns repository execution and state synchronization;
- F-013 is completed and no longer the active frontier;
- the current active frontier is now `F-014 Semantic Review Next-Issue Navigation and Focus-Step Controls`.

## Accepted boundaries right now

- The repository is run as a single system of documents.
- `00_INDEX.md` owns navigation only.
- Live project state is owned by this file.
- The active implementation packet is owned by `05_CODEX/NEXT_TASK.md`.
- The project starts desktop-first.
- MVP is centered on project creation, source intake, semantic blocks, semantic-map review, and the approved semantic-first desktop operating surface.
- manager-led execution model is fixed.
- architecture layers through downstream output-boundary fixation are completed before broad runtime expansion.
- the current runtime proof remains local-first, file-based, and intentionally narrow.
- The next implementation lane must not drift into automatic film downloading, full render automation, platform publishing, or speculative AI quality scoring.

## Open items

- add one minimal next/previous navigation control for the current focused semantic review set inside Semantic Map Workspace;
- keep movement through issue-focused, review-ready, or suitability-focused subsets stable and legible;
- improve review flow without introducing a workflow queue, dashboard surface, or broader navigation subsystem.

## Next step

Open and execute one bounded packet for `F-014 Semantic Review Next-Issue Navigation and Focus-Step Controls`.

## What must not be lost in a new chat

- The project is not just a video editor; it is a meaning-to-media engine.
- The correct logic is `analysis text -> semantic blocks -> scene matching -> timecodes -> rough cut -> shorts/carousel/package`.
- manager-led execution model is fixed.
- MVP main surface is `Semantic Map Workspace`.
- product, domain, schema, project-file, asset, and downstream output-boundary layers are fixed.
- F-013 is completed with one bounded focus control, filtered semantic-list visibility for issues/review-ready/suitability modes, coherent selection behavior, and concise empty-state cues in the local-first workspace.
- the next strong step is `F-014 Semantic Review Next-Issue Navigation and Focus-Step Controls`, not broad runtime/backend depth.
