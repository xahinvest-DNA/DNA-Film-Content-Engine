# Content Output Specification

Last updated: 2026-04-06
Status: active

## Purpose

Define the product-level output entities supported by DNA Film Content Engine.

## O-001 Long-form analytical video

### Definition
A structured long-form video built from the analysis through semantic sequencing and later visual alignment.

### Product role
Primary deep-format output.

### Minimum product fields
- title
- block sequence
- target duration
- status
- packaging readiness

## O-002 Shorts / Reels

### Definition
Short-form vertical videos derived from one or more semantic blocks and later paired with visual proof or support scenes.

### Product role
Attention, entry, and amplification units.

### Minimum product fields
- hook
- core point
- source block link
- target duration band
- platform suitability

## O-003 Carousel

### Definition
A slide-based content unit built from condensed semantic blocks for Instagram-style reading flow.

### Product role
Static or swipeable analytical summary format.

### Minimum product fields
- slide sequence
- title slide
- body slides
- closing slide
- status

## O-004 Packaging set

### Definition
Support assets that package content for publication.

### Includes
- titles
- hooks
- captions
- CTA variants
- thumbnail text
- short descriptions

### Product role
Convert content outputs into publishable units.

## O-005 Project content pack

### Definition
A grouped project-level output view that collects all outputs derived from one source analysis.

### Includes
- long-form analytical video
- shorts / reels set
- carousel set
- packaging set

### Product role
The highest-level output entity for one project.

## MVP output rule

The MVP should define these outputs as first-class product entities even if later implementation of rendering and export remains partial.
