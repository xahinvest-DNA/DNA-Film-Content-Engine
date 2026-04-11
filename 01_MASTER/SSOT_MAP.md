# SSOT Map

Last updated: 2026-04-11
Status: active
Purpose: keep the repository resumable with a minimal delivery-oriented document contour.

## Mandatory control documents

### Navigation
- Primary SSOT: `00_INDEX.md`
- Scope: reading order and document entry points only.

### Current truth
- Primary SSOT: `01_MASTER/CURRENT_STATE.md`
- Scope: what is true now, active stage, active milestone, active packet, current gap.

### Accepted decisions
- Primary SSOT: `01_MASTER/DECISIONS.md`
- Scope: durable operating rules and strategic decisions only, not live stage-state assertions.

### Strategic watchlist
- Primary SSOT: `01_MASTER/STRATEGIC_WATCHLIST.md`
- Scope: non-blocking but potentially high-impact observations only; not a task backlog.

### Finished-product definition
- Primary SSOT: `01_MASTER/TARGET_STATE.md`
- Scope: what counts as finished usable software.

### Delivery sequencing
- Primary SSOT: `01_MASTER/DELIVERY_PLAN.md`
- Scope: stage logic, milestone movement, entry/exit conditions.

### MVP readiness gates
- Primary SSOT: `01_MASTER/RELEASE_CRITERIA.md`
- Scope: what must be true before the MVP is considered ready.

### Active packet
- Primary SSOT: `05_CODEX/NEXT_TASK.md`
- Scope: exactly one active Codex packet.

### Packet ledger
- Primary SSOT: `05_CODEX/TASKS.md`
- Scope: active, upcoming, and recently completed packets.

### Execution history
- Primary SSOT: `05_CODEX/CODEX_WORKLOG.md`
- Scope: compact implementation history and handoff trail.

## Secondary reference layers

These documents inform delivery but do not own live program control:

- `02_PRODUCT/*` for user flows, screens, UX rules, and output framing;
- `03_MODULES/*` for module contracts and builder boundaries;
- `04_TECH/*` for domain, schema, file-format, and asset rules;
- `01_MASTER/ROADMAP.md` for compact directional orientation only.

## Anti-duplication rule

Use one document for:

- now;
- target;
- path;
- task now.

Do not create additional master documents that restate the same control information with different wording.

## Reading order for new chats

1. `00_INDEX.md`
2. `01_MASTER/CURRENT_STATE.md`
3. `01_MASTER/DECISIONS.md`
4. `01_MASTER/TARGET_STATE.md`
5. `01_MASTER/DELIVERY_PLAN.md`
6. `01_MASTER/RELEASE_CRITERIA.md`
7. `01_MASTER/SSOT_MAP.md`
8. `05_CODEX/NEXT_TASK.md`
9. only the product/module/tech documents needed for the active packet
