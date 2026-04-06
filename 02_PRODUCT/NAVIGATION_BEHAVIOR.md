# Navigation Behavior

Last updated: 2026-04-06
Status: active

## Purpose

Define how the user moves through the MVP desktop interface.

This document owns navigation logic, availability rules, and contextual movement between screens. It does not replace `SCREEN_MAP.md`, which owns screen hierarchy.

## Primary navigation model

The MVP uses one desktop navigation model with three layers:

- left rail for primary section navigation;
- main workspace routing for the current active screen;
- contextual detail opening for selected semantic objects.

This model should feel like movement through one project progression rather than movement across unrelated app tabs.

## Primary sections

- Project Home
- Source Intake
- Semantic Map
- Matching Prep
- Output Tracks
- Export Center

## Navigation rules

### Directly selectable screens

The following screens should be directly selectable in MVP:
- Project Home
- Source Intake
- Semantic Map

These screens represent the real MVP loop and should remain easy to reach.

### Availability by prerequisite state

Availability must reflect project readiness.

Rules:
- `Source Intake` becomes meaningful once a project exists;
- `Semantic Map` becomes meaningful once the minimum source set exists;
- `Matching Prep` should not behave as active until semantic-map readiness exists;
- `Output Tracks` and `Export Center` remain non-active in MVP depth.

### Visible but not fully active screens

Later-phase screens may remain visible when they improve orientation, but they must not behave like implemented production surfaces.

The interface must show:
- why the screen is not yet active;
- what condition would make it available later;
- that the current MVP does not support full work there.

## Semantic-first navigation principle

Navigation must reinforce product progression:

1. home
2. intake
3. semantic control
4. later preparation
5. outputs
6. export

The user should not experience the product as a creative suite with many unrelated tabs.

The navigation model must keep semantic control as the gravitational center of the MVP.

## Contextual navigation behavior

## Selected block to inspector

Selecting a block inside `Semantic Map Workspace` should open `Block Detail / Inspector` contextually.

Preferred model:
- side panel or split view;
- no full route replacement;
- no forced modal interruption for normal block work.

## Workspace continuity rule

The user should not lose the semantic map while editing one block.

Consequences:
- map remains visible while inspector is open;
- changing selection updates the inspector in place;
- closing the inspector returns focus to the map immediately.

## When separate detail emphasis is acceptable

If the desktop layout becomes constrained, the detail surface may temporarily expand its visual weight, but it should still behave as an extension of the semantic workspace rather than as a detached screen.

## Next-action behavior

## Purpose

The interface should expose the strongest next meaningful action based on current readiness without filling every screen with competing CTA noise.

## Placement

The strongest next action may appear in:
- the top header/project bar;
- the `Project Home` next-action panel;
- the continuation area inside `Source Intake`;
- the approval/readiness area inside `Semantic Map Workspace`.

## Rules

- only one primary next action should dominate at a time;
- secondary actions may exist, but they must not compete with the strongest next step;
- next-action wording should be tied to readiness, not to generic productivity language.

Examples:
- `Load analysis text`
- `Review proposed blocks`
- `Approve semantic map`
- `Matching prep will unlock after map approval`

## Placeholder navigation behavior

Later-phase screens should:
- remain visible when they improve orientation;
- avoid looking active if the product lane is not implemented;
- show bounded placeholder messaging.

Allowed placeholder patterns:
- `Not yet active in MVP`
- `Available after semantic-map approval`
- `Planned for later product phase`

Forbidden placeholder pattern:
- fake controls that imply full operational capability.

## Not-ready-yet behavior

When a user enters a visible but bounded screen, the interface should provide:
- a concise explanation of current status;
- the prerequisite state if one exists;
- the relationship of that lane to the current project flow.

This message should orient the user and then route attention back to the strongest active lane.

## Anti-drift navigation rule

Navigation must support the product logic of the repository and must not drift into generic creative-suite behavior.

Consequences:
- do not promote timeline, render, or publishing metaphors into first-class MVP navigation;
- do not flatten the product into feature tabs without progression logic;
- do not make later-phase surfaces feel equal to the semantic operating surface before the product is ready.
