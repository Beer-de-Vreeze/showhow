---
version: alpha
name: Showhow - Frame (video / frame layer)
description: >
  Warm paper ground, ink line drawings, one teal accent. A drawn-by-hand explainer look that stays calm under narration.
unit: the frame - 1920x1080 primary; 9:16 and 1:1 documented
principle: atoms are sacred, composition is free, numbers come from the script

colors:
  paper: "#F3ECDD"
  ink: "#23201B"
  muted: "#5B5547"
  teal: "#0F6E6A"
  line: "#23201B"

typography:
  title:   { fontFamily: "EB Garamond", px: 96, weight: 700, lineHeight: 1.04, tracking: "-0.02em" }
  label:   { fontFamily: "Inter", px: 34, weight: 400, color: "ink" }
  caption: { fontFamily: "Inter", px: 32, weight: 400, color: "muted" }
  figure:  { fontFamily: "Inter", px: 28, weight: 700, tabular: true }

spacing:
  pad: "6cqw"
  gap: "3cqw"

components:
  line-drawing:
    stroke: "3px {colors.ink}, no fill"
    description: "Parts are outlines on paper; the axle or focal mark takes teal."
  leader:
    stroke: "2.5px {colors.ink}, dot end on the part"
  bar:
    backgroundColor: "{colors.ink}"
    focal: "{colors.teal}"
    description: "One focal bar in teal, the rest ink; value above, label below."
---

# Showhow - Frame (video / frame layer)

## Overview

Ink on warm paper, drawn like a textbook plate. Garamond carries the title, Inter carries every label and number. Teal marks the one thing the narration points at. Not showhowai.com: no cream-and-orange-dot, and the paper is a flat colour, not a gradient.

## The Frame

1920x1080 primary. Chrome text is at least 28px at 1080p. Margins 6cqw, one focal element per frame, at least half of a declarative frame empty.

## Colors

Two neutrals (paper, ink), one muted ink for captions, one accent (teal). Teal is for the focal element only; a second accent is a defect.

## Typography

Two families: EB Garamond 700 for the title, Inter 400/700 for labels, captions and numbers. Sentence case. Tracking no tighter than -0.02em.

## Depth & Surface

Zero shadow, zero blur, zero fill on parts. Depth is line weight and white space.

## Shapes

Square corners on bars. Gears and parts are outlines. No rounded cards.

## Composition Rules

### Do

- One stroke weight for every drawing.
- Leader lines end in a dot on the part and a short horizontal run to the label.
- Teal on the focal bar or mark only.

### Don't

- No tracked all-caps labels or eyebrow above the title.
- No shadows, glows or gradient fills.
- No second accent colour, and no orange.

## Aspect-Ratio Behavior

- 16:9: title top-left, figure left, chart right.
- 9:16: one column, title then figure then chart; figure and chart each span the full measure.
- 1:1: title across the top over two lines, figure and chart side by side below; labels step up to keep 28px effective.

## Numerals & Claims (hard rule)

Never invent figures, dates or counts. Chart values come from the script or the source; the sample numbers (60, 120, 180, 240) exist only in the sample.

## Pre-Render Self-Audit

- **Squint** - the Garamond title is the dominant mass.
- **Palette** - paper, ink, muted, teal only.
- **Lines** - one stroke weight.
- **Contrast** - muted on paper at least 4.5:1; run npx hyperframes check.
- **Fabrication** - every number traces to the script.

## Known Gaps

- Motion is out of scope; the showhow motion signature lives in the design floor.
- Sampled on one scene (title, labelled part, bar chart); maps, timelines and 3D need their own pass.
- Fonts are the OFL files in `fonts/` beside this file (licences next to them); copy them to `composition/assets/fonts/` and declare `@font-face` with `src: url(assets/fonts/...)`. No CDN.
