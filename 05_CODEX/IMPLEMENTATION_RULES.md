# Codex Implementation Rules

Last updated: 2026-04-06
Status: active
Purpose: define how implementation tasks should be interpreted and how repository state must be kept synchronized.

## Core rule
Treat this repository as a source-of-truth project system, not as a loose code folder and not as a continuation of chat memory.

## Project operating model

The project runs under a manager-led execution model.

### ChatGPT role
ChatGPT acts as the project manager and decision layer.

### ChatGPT owns
- strongest-next-step selection;
- product and architecture direction;
- scope control;
- task-packet formulation;
- interpretation of Codex results;
- anti-drift control.

### Codex role
Codex acts as the implementation and repository execution layer.

### Codex owns
- creating and updating files;
- executing the active packet;
- committing and pushing changes;
- synchronizing project-state files;
- returning work in the required handoff format.

### Codex does not own
- project strategy;
- independent frontier selection;
- silent product-direction changes;
- silent scope expansion.

## Working cycle

1. ChatGPT defines the strongest next bounded step.
2. ChatGPT creates the task packet.
3. Codex executes the packet in the repository.
4. Codex synchronizes state files.
5. Codex returns a handoff.
6. ChatGPT reviews the result and defines the next step.

## Mandatory reading order for implementation tasks
1. `00_INDEX.md`
2. `01_MASTER/CURRENT_STATE.md`
3. `01_MASTER/DECISIONS.md`
4. `01_MASTER/ROADMAP.md`
5. `01_MASTER/SSOT_MAP.md`
6. `05_CODEX/NEXT_TASK.md`
7. Relevant product/module documents named in `NEXT_TASK.md`

## Task interpretation rules
- Implement only the task described in `05_CODEX/NEXT_TASK.md`.
- Prefer the smallest bounded change that satisfies the task.
- Map work to real user-visible product gains whenever possible.
- Do not silently broaden scope under labels such as cleanup, support work, polish, or hardening.

## Scope-control rules
- Do not introduce heavy engine implementation when the active packet is product-design only.
- Do not duplicate live state in weaker files.
- Do not reopen deferred layers such as mobile, sync, direct publishing, team workflow, or platform-like media management unless explicitly selected.
- Do not replace semantic product control with generic editor abstractions prematurely.

## Codex scope discipline under manager-led execution

Codex must not:
- choose a new product frontier independently;
- create additional implementation lanes without explicit instruction;
- split work into unnecessary micro-slices;
- expand scope under labels such as polish, hardening, support work, or cleanup;
- replace product language with generic engineering abstractions when that reduces project clarity.

If Codex identifies strong follow-up opportunities, they should be returned only as recommendations in the handoff and must not be implemented implicitly.

## Documentation-update rules
A pass is not complete unless repository state is synchronized where required.

### Required repository synchronization after each completed packet
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/CODEX_WORKLOG.md`

### Update when project-level meaning changes
- `01_MASTER/DECISIONS.md`

### Update when navigation or authority changes
- `00_INDEX.md`
- `01_MASTER/SSOT_MAP.md`
