# DNA Film Content Engine

DNA Film Content Engine is a desktop-first content production system that turns film analysis into usable content outputs.

This repository is managed as a source-of-truth project system, not just as a code folder.

## Start here

1. `00_INDEX.md`
2. `01_MASTER/CURRENT_STATE.md`
3. `01_MASTER/DECISIONS.md`
4. `01_MASTER/TARGET_STATE.md`
5. `01_MASTER/DELIVERY_PLAN.md`
6. `01_MASTER/RELEASE_CRITERIA.md`
7. `01_MASTER/SSOT_MAP.md`
8. `05_CODEX/NEXT_TASK.md` when the purpose is implementation

## Product aim

Build a desktop-first workstation where a user can move through:

`analysis text -> semantic map -> matching -> scene/timecode chain -> rough cut -> output builder -> export package`

The project is considered successful only when that path produces a usable content artifact.

## Current runtime proof

The existing runtime already covers the path from project creation through rough-cut preparation in a local-first desktop prototype.

The current active packet is `A-001 Runtime Structural Refactor for Growth`, which prepares the codebase for the first real builder/output vertical slice.

### Run the desktop prototype

```bash
python -m runtime
```

### Run the local validation tests

```bash
python -m unittest tests/test_mvp_slice.py -v
```
