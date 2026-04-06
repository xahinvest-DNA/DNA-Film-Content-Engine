# DNA Film Content Engine

A project system for building a Communication DNA-based content engine that turns a film analysis text into synchronized video and multi-platform content outputs.

This repository is managed as a source-of-truth project system, not just as a code folder.

## Start here

1. `00_INDEX.md`
2. `01_MASTER/CURRENT_STATE.md`
3. `01_MASTER/DECISIONS.md`
4. `01_MASTER/ROADMAP.md`
5. `01_MASTER/SSOT_MAP.md`
6. `05_CODEX/NEXT_TASK.md` when the purpose is implementation

## Core aim

Build a desktop-first product that accepts:
- a text analysis of a film,
- the film or prepared film assets,
- optional subtitles/transcript,

and produces:
- long-form analytical video,
- shorts / reels,
- carousel-ready slide content,
- packaging assets such as titles, captions, and thumbnails.

## F-006 local MVP slice

The repository now includes one bounded local-first MVP implementation slice:
- create a project package on disk;
- load analysis text;
- derive and persist semantic blocks;
- inspect the semantic map and selected block in a minimal desktop-facing prototype.

### Run the desktop prototype

```bash
python -m runtime
```

### Run the local validation tests

```bash
python -m unittest tests/test_mvp_slice.py -v
```
