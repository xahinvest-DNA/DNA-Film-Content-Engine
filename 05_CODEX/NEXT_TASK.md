# NEXT TASK

Last updated: 2026-04-08
Status: ready
Task ID: F-019
Task type: implementation
Title: Matching Prep Asset Registration Slice

## Goal

Add one minimal local-first film-side input registration slice so Matching Prep can hold both an approved semantic handoff and one explicit asset-side entry boundary without implementing scene matching automation, backend/API work, or a broader workflow lane.

## Why this is next

The repository now has a real blocked/open Matching Prep entry surface driven by approved semantic state. That proves the semantic side of the next lane can open honestly.

The strongest next bounded gain is not candidate generation yet. It is to give Matching Prep one equally narrow film-side input boundary, because later scene matching logically requires both approved semantic input and some film-side material or reference presence.

## In scope

- one bounded follow-up packet on top of completed `F-018`
- one minimal local-first asset or film-side input registration surface inside the current runtime
- one narrow persisted representation of registered film-side inputs or references
- one compact Matching Prep visibility update showing whether semantic handoff only or semantic-plus-asset registration is present
- only the smallest runtime and local-storage changes required to make that asset registration slice executable or testable
- local tests covering registration, reload persistence, and blocked/open coherence

## Out of scope

- scene matching automation
- candidate generation or ranking
- timecode logic
- backend or API design
- workflow queues or planning dashboards
- downstream output generation
- generalized asset management subsystem buildout
- packet expansion beyond the first bounded asset registration slice

## Recommended validation

Validate that the resulting packet delivers:

- one clear local-first film-side registration path inside the current Matching Prep lane
- one persisted asset-side entry boundary that survives reload
- coherent visibility between semantic-only readiness and semantic-plus-asset registration readiness
- no scope explosion into scene matching, backend, or downstream-output implementation

## Required handoff format

Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
