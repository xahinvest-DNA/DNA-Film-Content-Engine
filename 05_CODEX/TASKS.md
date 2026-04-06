# Codex Tasks

Last updated: 2026-04-06
Current focus: F-010 semantic completeness cues and issue visibility

## Working rule
Tasks should be bounded, product-visible, and small enough to preserve continuity without turning the repository into micro-slice overload.

## Active task

### F-010
- Status: active
- Module: semantic completeness cues and issue visibility
- Goal: extend the semantic workspace with lightweight completeness cues and clearer issue visibility without drifting into matching, backend, or downstream execution.
- Input documents: `00_INDEX.md`, `01_MASTER/CURRENT_STATE.md`, `01_MASTER/DECISIONS.md`, `01_MASTER/ROADMAP.md`, `01_MASTER/SSOT_MAP.md`, `05_CODEX/NEXT_TASK.md`, `02_PRODUCT/MVP_DESKTOP_INTERFACE.md`, `02_PRODUCT/NAVIGATION_BEHAVIOR.md`, `03_MODULES/DNA_SEMANTIC_ENGINE.md`
- Expected result: one minimal semantic workspace update where completeness cues and issue visibility are clearer without scope explosion.

## Completed tasks

### F-009
- Status: completed
- Module: semantic approval guardrails and reopen clarity
- Goal: extend the semantic workspace with clearer approval-transition guardrails and explicit reopen visibility without drifting into matching, backend, or downstream execution.
- Outcome: added one approval guardrail that blocks unclear approval transitions, persisted readable blocked-approval reasons, made reopen-after-change explicit after approved semantic edits or reorder actions, surfaced those signals in the workspace, added reload-persistence coverage through local tests, and kept the packet intentionally narrow.

### F-008
- Status: completed
- Module: semantic map ordering and approval readiness
- Goal: extend the editable semantic workspace with one bounded ordering control and clearer approval-readiness visibility without drifting into matching, backend, or downstream execution.
- Outcome: added a minimal move-up / move-down ordering control, persisted semantic block order updates on disk, kept reordered sequence values stable across reload, derived a clearer approval-readiness indicator from existing semantic state, updated workspace summaries with that visibility, added local validation for reorder persistence, and kept the packet intentionally narrow.

### F-007
- Status: completed
- Module: semantic map editing and review controls
- Goal: extend the completed local-first MVP slice with persisted selected-block editing and one minimal project-level semantic review control without drifting into matching, backend, or downstream execution.
- Outcome: extended the existing inspector into an editable semantic detail surface, persisted selected-block title/role/notes updates on disk, added a local semantic review state record, exposed project-level semantic review controls in the desktop-facing workspace, added reload-persistence coverage through local tests, and kept the packet intentionally narrow.

### F-006
- Status: completed
- Module: first MVP implementation slice
- Goal: implement one bounded implementation-entry packet for a user-visible desktop slice that covers project creation, analysis-text intake, semantic block persistence, and semantic-map inspection without drifting into broad runtime/backend infrastructure.
- Outcome: added a local-first runtime package, created a minimal `tkinter` desktop-facing app shell, created a file-based project package flow for project creation and analysis-text intake, persisted derived semantic blocks to disk, exposed semantic map and selected-block inspection, added local tests, and kept the slice intentionally narrow.

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
