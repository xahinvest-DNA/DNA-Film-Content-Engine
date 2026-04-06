# Roadmap

Last updated: 2026-04-06
Status: active

## Direction of travel

The project should move from product framing to bounded implementation in this order:

1. interface-first product framing;
2. project intake and screen architecture;
3. semantic-map workflow;
4. scene-matching workflow;
5. rough-cut builder;
6. shorts/reels builder;
7. carousel and packaging;
8. export center;
9. later-phase personalization, film library, and reuse systems.

## Phase 1 - Product framing

Goal: fix the user-facing operating model before engine-heavy implementation.

Outputs:
- `02_PRODUCT/USER_FLOWS.md`
- `02_PRODUCT/SCREEN_MAP.md`
- `02_PRODUCT/UX_PRINCIPLES.md`
- `01_MASTER/PRODUCT_SCOPE.md`
- `01_MASTER/MVP_vs_FULL.md`

## Phase 2 - Interface skeleton

Goal: define the first desktop workspace and navigation system.

Outputs:
- MVP desktop screen hierarchy
- screen responsibilities
- object visibility per screen
- transitions between states

## Phase 3 - Domain and module fixation

Goal: define domain entities and source-of-truth module boundaries.

Outputs:
- domain model
- data schema
- intake / semantic / matching / cut-building module boundaries

## Phase 4 - First implementation slices

Goal: implement one usable user-visible vertical slice rather than disconnected helpers.

Suggested first slice:
- create project
- load analysis text
- define semantic blocks
- inspect proposed screen-ready semantic map

## Deferred areas

- automatic film downloading
- cloud sync
- social-media publishing automation
- team workflows
- advanced recommendation or viral-scoring layers
- full render farm or heavy media infrastructure
