# Current State

Last updated: 2026-04-10
Status: active
Current stage: F-037 rough cut segment removal slice is completed
Active module: manager review and next bounded packet selection
Active frontier: post-F-037 state synchronization
Active question: which one strongest bounded packet should follow now that the runtime can add, reorder, subset-mark, and remove rough-cut segment stubs inside one bounded local-first rough-cut structure without opening playback, trimming, timeline, render/export, backend, or workflow-engine scope

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
- the semantic workspace now supports persisted selected-block editing, project-level review state, persisted ordering, approval-readiness visibility, one approval guardrail, explicit reopened-after-change visibility that survives reload, persisted semantic boundary editing through minimal split/merge controls, deterministic completeness and issue visibility, persisted output-suitability review controls, bounded focus filtering, focused next/previous navigation, adjacent canonical context, focus-span summary, and one explicit matching-prep readiness gate derived from existing semantic-review state;
- Matching Prep now has both sides of the future bridge in minimal form: one approved semantic handoff surface and one persisted film-side input registration surface inside the same local-first lane;
- Matching Prep now also holds one honest manual matching-prep artifact: persisted manual candidate stubs that link one semantic block to one registered film-side input and remain visible across reload and gated/open state transitions;
- the current runtime now proves that later matching work can start from honest local inputs on both sides plus one explicit proposed semantic-to-asset relationship without introducing scene matching automation, ranking, or backend orchestration;
- Matching Prep now also distinguishes manual candidate intent in one bounded way, because each existing manual candidate stub can persist a minimal review status of `tentative`, `selected`, or `rejected` across reload and gated/open state transitions;
- Matching Prep now also exposes one compact status-based focus control so editors can narrow visible candidate stubs to `all`, `tentative`, `selected`, or `rejected` without opening a candidate-management surface or extending persistence;
- Matching Prep now also surfaces selected candidates as the current preferred-for-review subset through one dominant summary and handoff cue, while keeping `selected` explicitly below accepted-reference or final-match semantics;
- Matching Prep now also exposes one compact readiness cue that tells the editor whether a current preferred subset already exists or is not fixed yet, without turning that cue into approval or accepted-reference workflow state;
- Matching Prep now also stores one short editor-supplied preferred rationale on candidate stubs and surfaces that rationale only in the selected-first handoff area, with a bounded fallback when no rationale has been recorded yet;
- Matching Prep now also supports one minimal remove path for the currently selected manual candidate stub, updating local persistence and recalculating selected/readiness/handoff cues without opening a management subsystem;
- Matching Prep now also pins selected candidate stubs to the top of the current visible listing while preserving persisted order on disk and preserving relative order inside each visible subset;
- Matching Prep now also blocks creation of an exact duplicate manual candidate stub for the same semantic block and prep input pair, preserving local candidate integrity without adding a new policy subsystem;
- Matching Prep now also promotes one selected manual candidate stub into one explicit accepted reference for later matching work, keeps that accepted reference singular and reload-stable, and surfaces it as a dominant downstream-facing handoff boundary without turning it into timecoded or final-match output;
- the runtime now also opens one real `Scene Matching` entry surface that receives the current accepted reference as the first honest downstream-facing handoff, stays blocked when no accepted reference exists, remains honestly readable when semantic approval reopens, and keeps explicit pre-automation/pre-timecode wording;
- the runtime now also lets open `Scene Matching` save one singular accepted scene reference stub from the current accepted prep reference, persists that scene-side artifact locally, surfaces it as the dominant downstream handoff inside `Scene Matching`, and keeps it honestly readable across reload and blocked-after-reopen states without opening automatic matching or timecodes;
- the runtime now also lets open `Scene Matching` save one singular timecode range stub from the current accepted scene reference stub, persists that temporal artifact locally, reconciles it against upstream scene-side invalidation, and surfaces it as the dominant current temporal handoff without opening transcript alignment or final timing semantics;
- the timecode range stub now also enforces one bounded manual `HH:MM:SS` format plus one end-not-earlier-than-start sanity rule, making the temporal artifact more trustworthy without turning it into a parsing, alignment, or final-timing subsystem;
- the runtime now also lets the current accepted reference, accepted scene reference stub, and timecode range stub become one ordered persisted `rough_cut_segment_stub` set inside a real `Rough Cut` lane, supports bounded move-up and move-down behavior, and keeps the saved set honestly reconciled against upstream invalidation without opening real cut, render, or workflow scope;
- the `Rough Cut` lane now also distinguishes between all saved rough-cut segment stubs and the current preferred rough-cut subset, persists that subset status locally, and surfaces it as the dominant current editorial handoff without turning the lane into a mini-timeline;
- the `Rough Cut` lane now also supports one bounded removal path for the currently selected rough-cut segment stub, resequences the remaining set honestly, keeps preferred-subset readability coherent, and preserves blocked-but-readable reopen honesty without opening playback or timeline semantics;
- the main MVP operating surface remains fixed as `Semantic Map Workspace`;
- the meaning-first architecture is now explicit across product, domain, schema, project-package, asset, downstream output, and implementation layers;
- the project now uses a manager-led execution model;
- ChatGPT owns strongest-next-step selection;
- Codex owns repository execution and state synchronization;
- manager review depth and next-step efficiency-gate doctrine are now fixed in repository governance documents rather than left to chat memory;
- F-037 is completed and no longer the active runtime frontier;
- the repository is now waiting for ChatGPT to select the next strongest bounded packet.

## Accepted boundaries right now

- The repository is run as a single system of documents.
- `00_INDEX.md` owns navigation only.
- Live project state is owned by this file.
- The active implementation packet is owned by `05_CODEX/NEXT_TASK.md`.
- The project starts desktop-first.
- MVP is centered on project creation, source intake, semantic blocks, semantic-map review, the first matching-prep entry boundary, the first film-side registration boundary, the first manual candidate-stub boundary, the first manual candidate review-status boundary, the first manual candidate status-focus boundary, the first selected-dominant handoff boundary, the first selected-readiness cue boundary, the first selected-candidate rationale boundary, the first manual candidate removal boundary, the first selected-pin-to-top visibility boundary, the first manual candidate duplicate-guard boundary, the first accepted-reference boundary, the first scene-matching-facing entry boundary, the first accepted scene reference stub boundary, the first timecode range stub boundary, and the approved semantic-first desktop operating surface.
- manager-led execution model is fixed.
- ChatGPT must review Codex handoffs at completion level and management level before selecting the next packet.
- strongest-next-step selection must pass an efficiency gate rather than follow previous recommendations by inertia alone.
- architecture layers through downstream output-boundary fixation are completed before broad runtime expansion.
- the current runtime proof remains local-first, file-based, and intentionally narrow.
- The next implementation lane must not drift into automatic film downloading, full render automation, platform publishing, or speculative AI quality scoring.

## Open items

- preserve the new timecode range stub boundary as a bounded temporal artifact slice rather than letting it drift into transcript alignment, automatic timing extraction, ranking, or workflow-engine semantics;
- preserve the new rough-cut segment removal boundary as bounded structural control inside the existing ordered rough-cut set rather than letting it drift into timeline editing, playback, render, or export semantics;
- keep the new `HH:MM:SS` manual-format and ordering guard narrow rather than letting it grow into smart parsing, normalization, or frame-accurate validation policy;
- choose one strongest next bounded packet now that the runtime can cross from accepted prep reference into scene-side and temporal downstream artifacts inside `Scene Matching`;
- keep later scene-matching work explicitly outside automatic matching, transcript alignment, confidence engines, timecodes beyond this stub, backend, dashboard, and workflow-engine scope until a stronger packet justifies opening them.

## Next step

ChatGPT should review the completed `F-037 Rough Cut Segment Removal Slice` handoff and select one strongest next bounded packet.

## What must not be lost in a new chat

- The project is not just a video editor; it is a meaning-to-media engine.
- The correct logic is `analysis text -> semantic blocks -> scene matching -> timecodes -> rough cut -> shorts/carousel/package`.
- manager-led execution model is fixed.
- MVP main surface is `Semantic Map Workspace`.
- product, domain, schema, project-file, asset, and downstream output-boundary layers are fixed.
- F-037 is completed with one bounded removal path on the ordered `rough_cut_segment_stub` set, so the runtime now completes the first minimal rough-cut structural control loop by allowing add, reorder, subset-mark, and remove while still staying provisional, local-first, pre-render, and outside workflow-engine semantics.
- ChatGPT must read Codex handoffs as management signals about capability gained, capability unlocked, unresolved gap, and packet-size efficiency before choosing what comes next.
- the next strong active runtime step must be re-selected from current repository capability rather than assumed by inertia from the just-completed matching-prep status slice.
