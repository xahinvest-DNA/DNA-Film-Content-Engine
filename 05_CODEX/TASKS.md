# Codex Tasks

Last updated: 2026-04-10
Current focus: manager review and next bounded packet selection after F-024

## Working rule
Tasks should be bounded, product-visible, and small enough to preserve continuity without turning the repository into micro-slice overload.

## Active task

- No new implementation packet is active until ChatGPT selects the next bounded step after reviewing the completed `F-021` handoff.

## Completed tasks

### F-024
- Status: completed
- Module: selected candidate readiness cue slice
- Goal: add one compact selected-readiness cue inside Matching Prep without drifting into accepted-reference pre-state, approval workflow, ranking, timecodes, backend, or workflow execution buildout.
- Outcome: added one explicit readiness-style cue that distinguishes whether a preferred selected subset exists now or is not fixed yet, surfaced that cue in Matching Prep summary and handoff status areas, kept selected semantics limited to manually preferred-for-review only, verified selected-present, selected-absent, reload-coherent, and gated-after-reopen cue behavior through local app-level tests, and kept the packet intentionally narrow.

### F-023
- Status: completed
- Module: selected candidate dominant handoff slice
- Goal: add one minimal selected-first dominant handoff cue inside Matching Prep without drifting into accepted-reference conversion, ranking, final-match semantics, timecodes, backend, or workflow execution buildout.
- Outcome: added one explicit summary cue showing whether selected candidates currently exist, added one selected-first handoff section above the broader candidate listing, kept selected semantics limited to manually preferred-for-review only, verified selected-present, selected-absent, reload-coherent, and gated-after-reopen visibility through local app-level tests, and kept the packet intentionally narrow.

### F-022
- Status: completed
- Module: manual candidate status focus slice
- Goal: add one compact local-first focus/filter control for manual candidate stubs inside Matching Prep without drifting into candidate management, ranking, accepted-reference semantics, timecodes, backend, or workflow execution buildout.
- Outcome: added one compact status focus control with `all`, `tentative`, `selected`, and `rejected` options, filtered the visible candidate subset in Matching Prep summary and handoff surfaces using the existing `review_status` field, kept focus state non-persisted and local to the active UI session, verified reload-coherent filtering and gated-after-reopen visibility through local app-level tests, and kept the packet intentionally narrow.

### F-021
- Status: completed
- Module: manual match candidate review status slice
- Goal: add one minimal local-first review-status control for manual candidate stubs inside Matching Prep without drifting into scene matching automation, ranking, timecode, backend, or downstream execution buildout.
- Outcome: added one persisted `review_status` field directly on manual candidate stubs, defaulted new stubs to `tentative`, exposed one minimal Matching Prep control for switching existing stubs between `tentative`, `selected`, and `rejected`, surfaced compact status visibility in open and gated handoff states, verified reload coherence through local store-level and app-level tests, and kept the packet intentionally narrow.


### F-020
- Status: completed
- Module: first manual match candidate stub slice
- Goal: add one minimal local-first manual semantic-to-asset candidate stub inside Matching Prep without drifting into scene matching automation, ranking, timecode, backend, or downstream execution buildout.
- Outcome: added one persisted manual semantic-to-asset candidate-stub path inside Matching Prep, stored manual candidate stubs locally in the project package, surfaced candidate presence directly in the prep lane across open and gated states, verified creation and reload coherence through local tests, and kept the packet intentionally narrow.

### F-019
- Status: completed
- Module: matching prep asset registration slice
- Goal: add one minimal local-first film-side input registration surface so Matching Prep can hold both an approved semantic handoff and one explicit asset-side entry boundary without drifting into scene matching automation, backend, or downstream execution buildout.
- Outcome: added one persisted film-side prep input registration path inside Matching Prep, stored registered references locally in the project package, surfaced semantic-only versus semantic-plus-asset visibility in the prep lane, kept gated/open semantic logic intact, verified registration and reload coherence through local tests, and kept the packet intentionally narrow.

### F-018
- Status: completed
- Module: first matching prep entry slice
- Goal: open one minimal local-first `Matching Prep` entry surface so an approved semantic map can feed a real downstream-facing handoff slice without drifting into scene matching automation, backend, or downstream execution buildout.
- Outcome: turned `Matching Prep` from a placeholder into a real blocked/open runtime surface, derived blocked/open behavior from existing semantic-review state, exposed one local-first approved semantic handoff view for later matching work, verified blocked, approved, reopened, and reload-coherent behavior through local tests, and kept the packet intentionally narrow.

### F-017R
- Status: completed
- Module: semantic review to matching prep readiness gate
- Goal: add one compact readiness gate that tells the editor whether the semantic map is structurally ready to feed later matching prep and, if not, why not.
- Outcome: added a compact matching-prep readiness cue derived from existing intake, semantic completeness, review-state, approval, and reopen signals; surfaced blocked, conditionally plausible, and ready states in the current workspace; verified coherent gate behavior across approval, reopen-after-change, reorder, split, and merge paths; and replaced the weaker lane-marker step by explicit efficiency-gate reasoning.

### F-016
- Status: completed
- Module: semantic review focus-span summary
- Goal: extend the semantic workspace with one minimal summary cue so editors can read the shape of the current focused review subset without drifting into matching, backend, or downstream execution.
- Outcome: added a compact focus-span summary cue derived from the visible subset, surfaced count and canonical sequence span, kept the cue coherent after focus changes and structure edits, added local validation for full-range, filtered, singleton, and empty states, and kept the packet intentionally narrow.

### F-015
- Status: completed
- Module: semantic review adjacent context peek
- Goal: extend the semantic workspace with one minimal adjacent-context cue so editors can see the immediate previous and next semantic neighbors around the selected block without drifting into matching, backend, or downstream execution.
- Outcome: added a compact adjacent-context cue inside the inspector, derived previous and next semantic neighbors from canonical sequence order, kept the cue coherent under focus modes and focused navigation, recomputed adjacent context after reorder and split changes, added local validation for context behavior, and kept the packet intentionally narrow.

### G-001
- Status: completed
- Module: manager review depth and efficiency-gate fixation
- Goal: fix in the strongest governance documents that ChatGPT must review Codex handoffs as management inputs and apply an efficiency gate before choosing the next packet.
- Outcome: strengthened the manager-led doctrine in `DECISIONS.md` and `IMPLEMENTATION_RULES.md`, fixed explicit two-level handoff review, fixed the efficiency-gate and anti-inertia rules for strongest-next-step selection, synchronized live state without changing the active runtime frontier, and kept the packet documentation-only.

### F-014
- Status: completed
- Module: semantic review next-issue navigation and focus-step controls
- Goal: extend the semantic workspace with one minimal step-through control so editors can move through the currently focused semantic review subset without broadening navigation scope.
- Outcome: added bounded previous/next controls tied to the visible focused subset, added a compact current-position cue, kept navigation stable at subset boundaries and after focus changes, added local validation, and preserved the narrow local-first workspace boundary.

### F-013
- Status: completed
- Module: semantic review filters and focus cues
- Goal: extend the semantic workspace with one minimal filter or focus cue so editors can isolate blocks that need attention without drifting into matching, backend, or downstream execution.
- Outcome: added one bounded focus control with issue, review-ready, and suitability-lane modes; filtered the semantic list without introducing a dashboard surface; kept selection behavior coherent when focus changes; added concise empty-state cues; added local validation for focus behavior; and kept the packet intentionally narrow.

### F-012
- Status: completed
- Module: semantic output suitability review controls
- Goal: extend the semantic workspace with one minimal selected-block output-suitability review surface without drifting into matching, backend, or downstream execution.
- Outcome: exposed the existing output-suitability field as four bounded inspector controls, persisted local suitability edits on semantic blocks, surfaced lightweight suitability summaries in the semantic list and inspector, kept approved-map reopen behavior coherent after suitability edits, added reload-stable validation coverage, and kept the packet intentionally narrow.

### F-011
- Status: completed
- Module: semantic completeness cues and issue visibility
- Goal: extend the semantic workspace with lightweight completeness cues and clearer issue visibility without drifting into matching, backend, or downstream execution.
- Outcome: added deterministic warning-flag derivation for semantic blocks, surfaced project-level semantic completeness cues, exposed lightweight issue visibility in the semantic list and selected-block inspector, updated local summaries and approval-readiness legibility, added reload-stable validation coverage, and kept the packet intentionally narrow.

### F-010
- Status: completed
- Module: semantic block boundary editing and structural review completion
- Goal: extend the semantic workspace with one minimal split action and one minimal merge-with-adjacent action so editors can correct semantic block boundaries directly without drifting into matching, backend, or downstream execution.
- Outcome: added one minimal split-block control and one minimal merge-with-adjacent control inside the existing semantic workspace inspector, persisted structural semantic-block updates on disk, kept sequence ordering stable after split and merge, made approved semantic maps reopen explicitly after structural edits, added reload-persistence coverage through local tests, and kept the packet intentionally narrow.

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
