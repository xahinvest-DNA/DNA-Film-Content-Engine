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

### MVP desktop interface specification
- Primary SSOT: `02_PRODUCT/MVP_DESKTOP_INTERFACE.md`
- Scope: main desktop layout, role of interface areas, semantic workspace behavior, and MVP/non-MVP boundaries.

### Screen states
- Primary SSOT: `02_PRODUCT/SCREEN_STATES.md`
- Scope: project states, screen states, readiness vocabulary, and major state transitions.

### Navigation behavior
- Primary SSOT: `02_PRODUCT/NAVIGATION_BEHAVIOR.md`
- Scope: navigation rules, availability logic, contextual inspector behavior, next-action visibility, and placeholder behavior.

## Domain and logical architecture source-of-truth documents

### Domain model
- Primary SSOT: `04_TECH/DOMAIN_MODEL.md`
- Scope: canonical domain entities, entity relationships, lifecycle logic, and source/derived/output distinctions.

### Project intake module
- Primary SSOT: `03_MODULES/PROJECT_INTAKE.md`
- Scope: accepted inputs, normalization rules, readiness implications, and intake handoff contract.

### DNA semantic engine module
- Primary SSOT: `03_MODULES/DNA_SEMANTIC_ENGINE.md`
- Scope: semantic transformation responsibilities, semantic output contract, ambiguity handling, and review boundaries.

### Scene matching module
- Primary SSOT: `03_MODULES/SCENE_MATCHING.md`
- Scope: matching prerequisites, output artifacts, confidence levels, human validation role, and downstream handoff.

## Persistence and file-boundary source-of-truth documents

### Data schema
- Primary SSOT: `04_TECH/DATA_SCHEMA.md`
- Scope: stable record structures, identity rules, readiness markers, and persistence-facing distinctions.

### Project file format
- Primary SSOT: `04_TECH/PROJECT_FILE_FORMAT.md`
- Scope: local project-package structure, required/optional files, storage zones, and compatibility boundaries.

### Asset pipeline boundaries
- Primary SSOT: `04_TECH/ASSET_PIPELINE.md`
- Scope: asset classes, asset states, module handoff boundaries, and readiness implications without runtime execution design.

## Codex execution source-of-truth documents

### Current active task packet
- Primary SSOT: `05_CODEX/NEXT_TASK.md`
- Scope: exactly one current task packet with boundaries and acceptance criteria.

### Codex implementation rules
- Primary SSOT: `05_CODEX/IMPLEMENTATION_RULES.md`
- Scope: execution rules, manager-led operating model, and required state synchronization behavior.

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
7. The relevant product, module, or tech documents for the active slice
