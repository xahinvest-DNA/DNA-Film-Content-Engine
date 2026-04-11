# Decisions

Last updated: 2026-04-11
Status: active

## D-001 Repository operating model

The repository is managed as a source-of-truth project system, not as a loose folder of files.

### Consequences
- `00_INDEX.md` owns navigation only.
- `01_MASTER/CURRENT_STATE.md` owns live current state.
- `05_CODEX/NEXT_TASK.md` owns the one active implementation packet.
- weaker documents must point to stronger owners instead of duplicating live state.

## D-002 Product starting point

DNA Film Content Engine starts as a desktop-first product.

### Consequences
- the first user-facing operating surface is desktop;
- mobile, cloud sync, team workflows, and publication automation are deferred.

## D-003 Product logic

The product is a meaning-to-media engine, not a generic video editor.

### Canonical flow
`analysis text -> semantic map -> matching -> scene/timecode chain -> rough cut -> output builder -> export package`

### Consequences
- semantic structure is primary;
- rough cut is not the final unit of value;
- the product is judged by usable content outputs.

## D-004 Delivery program rule

The project is governed as a delivery program rather than as an open-ended chain of bounded local slices.

### Consequences
- the repository must always have one active stage;
- the repository must always have one active delivery milestone;
- Codex must always have one active packet that moves that milestone.

## D-005 Scope-control rule

The project keeps anti-drift discipline, but not at the cost of turning progress into endless micro-slice management.

### Consequences
- packets must map to real delivery progress;
- local improvements are justified only if they unlock the next product step;
- the control layer should stay compact.

## D-006 Manager-led execution model

The project is run through a manager-led execution model.

### Definition
- ChatGPT is the project manager and decision layer.
- Codex is the implementation and repository execution layer.

### Consequences
- strongest-next-step selection belongs to ChatGPT;
- Codex executes packets and synchronizes the repository;
- Codex must not independently redefine project direction.

## D-007 Manager review depth and efficiency gate

ChatGPT must review Codex handoffs as project-management inputs, not only as completion confirmations.

### Operating consequence
- strongest-next-step selection must pass an efficiency gate that checks value gained, strategic relevance, and whether the next step should change scale;
- the next packet must not be chosen by inertia from the previous local recommendation.

## D-008 First runtime boundary

The current runtime boundary remains local-first, file-based, and desktop-first.

### Consequences
- project state persists as a real local project package on disk;
- backend, cloud, heavy rendering, and platform publishing remain deferred until the first usable output path exists.

## D-009 Current stage logic

The repository is currently in `Stage A - Usable end-to-end engine`.

### Consequences
- the main gap is the absence of a real builder and export-ready artifact;
- structural refactoring is justified only because it reduces the cost of that first output path;
- success is defined by one usable end-to-end content workflow.
