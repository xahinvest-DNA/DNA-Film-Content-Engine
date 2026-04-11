# Release Criteria

Last updated: 2026-04-11
Status: active

The MVP is considered ready only when all criteria below are true.

## Functional completeness

- the user can complete the MVP path from analysis input to output artifact inside the product;
- the first builder path is real, not placeholder-only;
- the artifact is produced from existing project data rather than manual external assembly.

## Content-output usefulness

- the resulting artifact is usable as a real content-production output;
- the artifact exposes enough structure to be edited, reviewed, or handed off without rebuilding the logic outside the project.

## Export readiness

- the output is saved in a stable place inside the project package;
- the packaging/export result has a clear contract and predictable file structure;
- the user can reach the saved result from the UI.

## State integrity

- project state persists correctly across save/reload;
- upstream changes reconcile honestly against downstream artifacts;
- invalid or stale output state is not silently presented as current truth.

## Recovery and reload stability

- an existing project can be reopened without breaking the current workflow chain;
- the first builder/output path remains reproducible after reload;
- error states remain bounded and readable.

## Acceptance-proof coverage

- there is at least one acceptance-style scenario from analysis text to output artifact;
- supporting persistence and integration tests cover the first builder path;
- the current runtime path through rough cut remains protected during the transition.
