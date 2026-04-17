# Decisions

Last updated: 2026-04-17
Status: active

## D-001 Repository operating model

The repository is managed as a source-of-truth project system, not as a loose folder of files.

### Consequences
- `00_INDEX.md` owns navigation only.
- `01_MASTER/CURRENT_STATE.md` owns live current state.
- `05_CODEX/NEXT_TASK.md` owns the one active next packet.
- weaker documents must point to stronger owners instead of duplicating live state.

## D-002 Product starting point

DNA Film Content Engine starts as a desktop-first, local-first product.

### Consequences
- the first executable user-facing surface is local desktop software;
- backend, cloud sync, and publishing automation are deferred;
- a project must remain inspectable on local disk without remote dependency.

## D-003 Product logic

The product is a meaning-first engine, not a generic editor shell.

### Canonical flow
`project -> analysis text -> semantic map -> matching prep -> scene matching -> timecode grounding -> downstream outputs`

### Consequences
- semantic structure is the first real operating core;
- downstream work must attach to semantic truth rather than bypass it;
- each packet should open the next honest handoff rather than invent side infrastructure.

## D-004 Execution model for the MVP frontier

The active MVP work proceeds through one bounded packet at a time inside the active frontier.

### Consequences
- there must be one active packet at a time;
- packets should create real runnable progress, not speculative architecture;
- new packets should extend the last honest vertical slice instead of skipping ahead to broader systems.

## D-005 Runtime choice for the first executable slice

The first executable runtime uses Python with Tkinter as the minimal practical local desktop shell.

### Consequences
- the repo does not wait for a heavier desktop stack before proving the first usable path;
- runtime complexity stays secondary to opening the semantic-first vertical slice;
- UI polish is deferred behind functional bounded execution.

## D-006 Persistence choice for the first executable slice

The first executable slice persists projects as file-based local packages with JSON records.

### Consequences
- the manifest stays light and points to canonical records;
- canonical editable state lives in `records/`;
- source files remain separate from editable records;
- provisional machine-derived artifacts live in `derived/`;
- review/workflow state remains explicit instead of being hidden in UI-only state.
