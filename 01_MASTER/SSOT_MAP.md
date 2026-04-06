# SSOT Map

Last updated: 2026-04-06
Status: active
Purpose: define which document owns each project question so the repository stays resumable and anti-drift.

## Primary project-entry documents

### Project entry and navigation
- Primary SSOT: `00_INDEX.md`
- Scope: main entry point, reading order, key links.
- Notes: navigation only; must not restate live state.

### Current project state
- Primary SSOT: `01_MASTER/CURRENT_STATE.md`
- Scope: what is true now, current frontier, open items, next step.

### Accepted architectural and product decisions
- Primary SSOT: `01_MASTER/DECISIONS.md`
- Scope: fixed decisions, rationale, consequences, boundaries.

### High-level direction and sequencing
- Primary SSOT: `01_MASTER/ROADMAP.md`
- Scope: implementation order and sequence of phases.

### Product boundary
- Primary SSOT: `01_MASTER/PRODUCT_SCOPE.md`
- Secondary SSOT: `01_MASTER/MVP_vs_FULL.md`
- Scope: MVP boundary and later-phase separation.

## Product-design source-of-truth documents

### User flows
- Primary SSOT: `02_PRODUCT/USER_FLOWS.md`
- Scope: user journeys, workflow states, major transitions.

### Screen architecture
- Primary SSOT: `02_PRODUCT/SCREEN_MAP.md`
- Scope: screen hierarchy, navigation, screen responsibilities.

### UX operating principles
- Primary SSOT: `02_PRODUCT/UX_PRINCIPLES.md`
- Scope: product interaction rules, navigation logic, user-control philosophy.

### Content output definitions
- Primary SSOT: `02_PRODUCT/CONTENT_OUTPUT_SPEC.md`
- Scope: supported content outputs and their product definitions.

### Platform-specific packaging rules
- Primary SSOT: `02_PRODUCT/PLATFORM_RULES.md`
- Scope: platform differences for YouTube, Shorts, Reels, Carousel, and later channels.

## Codex execution source-of-truth documents

### Current active task packet
- Primary SSOT: `05_CODEX/NEXT_TASK.md`
- Scope: exactly one current task packet with boundaries and acceptance criteria.

### Codex implementation rules
- Primary SSOT: `05_CODEX/IMPLEMENTATION_RULES.md`
- Scope: how implementation tasks should be interpreted and how state files must be updated.

### Codex handoff format
- Primary SSOT: `05_CODEX/HANDOFF_TEMPLATE.md`
- Scope: mandatory task-result structure.

### Task ledger
- Primary SSOT: `05_CODEX/TASKS.md`
- Scope: bounded registry of completed, active, and upcoming slices.

### Worklog
- Primary SSOT: `05_CODEX/CODEX_WORKLOG.md`
- Scope: what changed, what remains, and what the next recommended slice is.

## Working rule for new chats

A new chat should begin with:
1. `00_INDEX.md`
2. `01_MASTER/CURRENT_STATE.md`
3. `01_MASTER/DECISIONS.md`
4. `01_MASTER/ROADMAP.md`
5. `01_MASTER/SSOT_MAP.md`
6. `05_CODEX/NEXT_TASK.md` if the purpose is implementation
7. The relevant product or module documents for the active slice
