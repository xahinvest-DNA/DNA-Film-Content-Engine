# NEXT TASK

Last updated: 2026-04-06
Status: ready
Task ID: F-001
Task type: product-design

## Goal
Create one bounded interface-first product packet so the repository fixes the first usable desktop screen architecture and user workflow for DNA Film Content Engine before deeper engine implementation begins.

## Why this is next
The repository is newly initialized. The strongest current need is not engine depth but product clarity: the project needs user flows, screen hierarchy, navigation logic, and screen responsibilities so later technical work attaches to a stable user-facing operating model.

## What should change
1. Add `02_PRODUCT/USER_FLOWS.md`.
2. Add `02_PRODUCT/SCREEN_MAP.md`.
3. Add `02_PRODUCT/UX_PRINCIPLES.md`.
4. Add `02_PRODUCT/CONTENT_OUTPUT_SPEC.md`.
5. Add `02_PRODUCT/PLATFORM_RULES.md`.
6. Synchronize `CURRENT_STATE.md`, `TASKS.md`, and `CODEX_WORKLOG.md` if the packet is completed.

## What must stay unchanged
- no rendering-engine implementation
- no automatic film downloading
- no social-platform publishing layer
- no mobile/sync/team workflow expansion
- no speculative AI-quality scoring subsystem

## Recommended validation
Validate that the resulting product layer defines:
- a coherent desktop-first user flow,
- a clear screen hierarchy,
- responsibilities for each screen,
- output definitions that match the intended product loop.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
