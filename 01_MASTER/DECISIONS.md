# Decisions

Last updated: 2026-04-06
Status: active

## D-001 Repository operating model

The repository is managed as a source-of-truth project system, not as a loose folder of files.

### Consequences
- `00_INDEX.md` owns navigation only.
- `01_MASTER/CURRENT_STATE.md` owns live current state.
- `05_CODEX/NEXT_TASK.md` owns the one active implementation packet.
- Weaker documents must point to stronger owners instead of duplicating live state.

## D-002 Product starting point

DNA Film Content Engine starts as a desktop-first product.

### Consequences
- The first user-facing operating surface is desktop.
- Mobile, cloud sync, team workflows, and publication automation are deferred.

## D-003 Product logic

The product is defined as a meaning-to-media engine rather than as a generic video editor.

### Canonical flow
`analysis text -> semantic blocks -> scene matching -> timecodes -> rough cut -> shorts/reels -> carousel -> packaging/export`

### Consequences
- Semantic structure is primary.
- Raw montage automation is secondary to meaning alignment.
- Interface design must reflect semantic control, not only timeline manipulation.

## D-004 First implementation frontier

The first strong frontier is interface-first product framing.

### Consequences
- The project starts with user flows, screen map, and UX principles.
- Heavy engine implementation is deferred until the user-facing operating model is fixed.

## D-005 Scope-control rule

The project adopts anti-drift discipline from Trader Trainer, but does not inherit its excessive micro-slice granularity.

### Consequences
- Work should move in bounded product slices.
- Task packets should map to real user-visible gains.
- The repository should stay resumable without turning into task-history overload.

## D-006 Manager-led execution model

The project is run through a manager-led execution model.

### Definition
- ChatGPT is the project manager and decision layer.
- Codex is the implementation and repository execution layer.

### Consequences
- strongest-next-step selection belongs to ChatGPT;
- bounded task packets are issued by ChatGPT;
- Codex executes packets and synchronizes the repository;
- Codex must not independently redefine project direction;
- repository state must remain resumable through synchronized state files.

### Why
This model reduces noise, improves decision quality, preserves project coherence, and prevents repository drift caused by mixing strategic and operational roles.
