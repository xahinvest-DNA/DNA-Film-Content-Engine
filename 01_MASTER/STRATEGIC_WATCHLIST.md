# Strategic Watchlist

Last updated: 2026-04-11
Status: active
Purpose: keep track of non-blocking but potentially high-impact signals without turning them into the active task queue.

## Operating rule

This file is not a backlog.

Use it only for observations that:

- are not blocking the current packet;
- do not yet require immediate intervention;
- may later have a large effect on architecture, UX, delivery speed, or release readiness.

Promote an item into a real packet only when its trigger is reached.

---

## W-001

Title: Output Tracks UI density growth

Area: ui

What is observed now:
- `Output Tracks` now carries Packaging, Shorts/Reels, Long Video, and Carousel through a clearer overview/detail split, and C-001/C-002A/C-002B together improved trust wording, recovery honesty, and slot readability for current states.

Why it is not a blocker yet:
- all four builders still fit in one readable local-first surface and the current interactions remain understandable after the density hardening pass.

Why it may become high-impact later:
- more builder rows, summaries, and previews can quickly turn the output surface into a dense wall of controls that slows build-review work.

Suggested trigger:
- the next builder or export-facing action makes the current surface harder to scan in one pass.

Suggested future response:
- UX pass

Status:
- watching

## W-002

Title: Builder metadata layer remains thin

Area: output_layer

What is observed now:
- `runtime/builders/` has a clean extension zone, and `runtime/ui/output_slots.py` now removes the worst repeated per-builder surface wiring, but builder metadata still lives as thin repeated fields rather than a stronger cross-layer contract.

Why it is not a blocker yet:
- four builders still remain understandable without a heavier registry layer, and the UI now has a bounded shared slot pattern instead of fully manual wiring.

Why it may become high-impact later:
- adding more builders or export actions may still increase naming drift, duplicated summaries, and inconsistent cross-layer metadata even after the UI-side compaction.

Suggested trigger:
- the next builder requires duplicated metadata mapping in multiple modules.

Suggested future response:
- architectural consolidation

Status:
- watching

## W-003

Title: Presentation layer growth

Area: ui

What is observed now:
- `runtime/ui/presentation.py` still owns a broad set of summary, preview, gate, and surface-formatting responsibilities.

Why it is not a blocker yet:
- the current builder and workflow surface set is still maintainable inside one presentation module.

Why it may become high-impact later:
- continued growth can turn the presentation layer into the next hidden monolith and slow safe UI changes.

Suggested trigger:
- a new output or UX pass requires touching many unrelated presentation helpers at once.

Suggested future response:
- refactor

Status:
- watching

## W-004

Title: ProjectSliceStore coordinator weight

Area: persistence

What is observed now:
- `ProjectSliceStore` is much cleaner than before A-002, but it still coordinates a large amount of write/load/build orchestration.

Why it is not a blocker yet:
- persistence behavior remains honest and test-covered, and the store no longer owns most of the business rules.

Why it may become high-impact later:
- more builders, recovery rules, and validation paths could make the coordinator too heavy to change confidently.

Suggested trigger:
- a new packet requires store edits across unrelated responsibilities in the same pass.

Suggested future response:
- architectural consolidation

Status:
- watching

## W-005

Title: Stage B output identity coherence

Area: product_identity

What is observed now:
- the product now emits four artifact families, each with a different editorial shape.

Why it is not a blocker yet:
- Packaging, Shorts/Reels, Long Video, and Carousel are still semantically distinct and test-covered for output identity.

Why it may become high-impact later:
- further builder expansion can blur the meaning of each output family and reduce product clarity.

Suggested trigger:
- a new builder starts to look like a renamed variation of an existing artifact rather than a distinct handoff type.

Suggested future response:
- product decision

Status:
- watching

## W-006

Title: Release-quality gap remains large

Area: release_readiness

What is observed now:
- Stage B breadth is now strong, and C-001/C-002A/C-002B/C-003 improved output trust, repeated-use coverage, load-time recovery honesty, output-surface maintainability, and multi-cycle validation depth, but release polish and acceptance confidence still lag behind output breadth.

Why it is not a blocker yet:
- the current focus was builder expansion, not production hardening.

Why it may become high-impact later:
- without a deliberate Stage C pass, the product may look richer than it is operationally durable.

Suggested trigger:
- output breadth stops being the main differentiator and the next risk becomes reliability, recovery, or trust.

Suggested future response:
- release hardening

Status:
- elevated
