# Codex Tasks

Last updated: 2026-04-06
Current focus: F-006 first MVP implementation slice

## Working rule
Tasks should be bounded, product-visible, and small enough to preserve continuity without turning the repository into micro-slice overload.

## Active task

### F-006
- Status: active
- Module: first MVP implementation slice
- Goal: implement one bounded implementation-entry packet for a user-visible desktop slice that covers project creation, analysis-text intake, semantic block persistence, and semantic-map inspection without drifting into broad runtime/backend infrastructure.
- Input documents: `00_INDEX.md`, `01_MASTER/CURRENT_STATE.md`, `01_MASTER/DECISIONS.md`, `01_MASTER/ROADMAP.md`, `01_MASTER/SSOT_MAP.md`, `05_CODEX/NEXT_TASK.md`, `02_PRODUCT/MVP_DESKTOP_INTERFACE.md`, `04_TECH/DATA_SCHEMA.md`, `04_TECH/PROJECT_FILE_FORMAT.md`
- Expected result: one minimal executable or testable MVP slice for create project, load analysis text, persist semantic blocks, and inspect the semantic map in a real desktop-facing path without scope explosion.

## Completed tasks

### F-005
- Status: completed
- Module: render/export schema and downstream output-boundary fixation
- Goal: define the first stable downstream render/export schema boundaries and output-module contracts without drifting into runtime backend implementation.
- Outcome: added the render/export-facing schema layer, fixed downstream output record families, fixed long-form / short-form / carousel / packaging module contracts, clarified export-ready grouping boundaries, preserved clear separation between output architecture and runtime render/backend design, and closed `F-005` before opening `F-006` as the active packet.

### F-004
- Status: completed
- Module: data schema and project file format fixation
- Goal: define the first stable data schema and local project file structure that support the approved domain model and MVP interface without drifting into runtime pipeline implementation.
- Outcome: added the stable data schema layer, fixed local project-package boundaries, fixed asset classification and handoff boundaries, clarified canonical versus derived persistence structures, and cleaned `00_INDEX.md` to separate current documents from planning-only map entries.

### F-003
- Status: completed
- Module: domain model and module-boundary fixation
- Goal: define the first domain model and module boundaries that support the approved MVP desktop interface without drifting into engine runtime implementation.
- Outcome: added the domain model, fixed canonical domain entities and relationships, fixed intake / semantic / matching module contracts, clarified source-versus-derived artifact distinctions, and fixed the meaning-first handoff chain from intake to downstream scene-reference preparation.

### F-002
- Status: completed
- Module: MVP desktop interface specification
- Goal: fix the first complete desktop interface package on top of the approved product layer without drifting into engine implementation.
- Outcome: added the MVP desktop interface specification, fixed desktop layout responsibilities, fixed screen and project states, fixed navigation behavior, fixed contextual inspector behavior, and preserved bounded later-phase placeholders around `Semantic Map Workspace`.

### F-001
- Status: completed
- Module: interface-first product framing
- Goal: fix the first usable desktop screen architecture and user workflow for DNA Film Content Engine before deeper engine implementation begins.
- Outcome: product layer added, desktop-first user flow fixed, screen hierarchy fixed, UX principles fixed, output definitions fixed, platform rules fixed, and `Semantic Map Workspace` fixed as the main MVP surface.

### Repository initialization pass - 2026-04-06
- Status: completed
- Module: repository synchronization
- Goal: initialize DNA Film Content Engine as a Project Brain and fix live-state ownership from the start.
- Outcome: repository now has navigation, current state, decisions, roadmap, scope, SSOT map, implementation rules, worklog, and one active packet.
