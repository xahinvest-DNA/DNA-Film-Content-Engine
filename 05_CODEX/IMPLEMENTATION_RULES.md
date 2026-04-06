# Codex Implementation Rules

Last updated: 2026-04-06
Status: active
Purpose: define how implementation tasks should be interpreted and how repository state must be kept synchronized.

## Core rule
Treat this repository as a source-of-truth project system, not as a loose code folder and not as a continuation of chat memory.

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

## Documentation-update rules
A pass is not complete unless repository state is synchronized where required.

### Always update when the task completes
- `05_CODEX/CODEX_WORKLOG.md`

### Update when the current focus changes
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`

### Update when navigation or authority changes
- `00_INDEX.md`
- `01_MASTER/SSOT_MAP.md`

### Update when project-level meaning changes
- `01_MASTER/DECISIONS.md`
