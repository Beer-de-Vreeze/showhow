---
version: alpha
name: Blue Professional - Frame (video / frame layer)
description: >
  Video-first companion to Blue Professional's design.md. The unit is the frame (1920×1080). Atoms
  are identical and sacred - the warm cream canvas, a single saturated cobalt (#1e2bfa) as the only
  accent, the three-step gray text ladder, Space Grotesk (display/numerals/chrome) + Inter (body),
  soft cobalt-tinted cards (4% fill / 20% border / 10–14px radius) with NO shadows, pill chrome, and
  the cobalt progress bar. Composition + frame scale rewritten. Motion out of scope.
unit: the frame - 1920×1080 primary; 9:16 and 1:1 documented
principle: atoms are sacred · composition is free · numbers come from the script

colors:
  bg: "#fdfae7"
  primary: "#1e2bfa"
  text: "#111111"
  text-muted: "#6b6b6b"
  text-light: "#9a9a9a"
  accent-light: "rgba(30,43,250,0.08)"
  accent-medium: "rgba(30,43,250,0.15)"
  border: "rgba(30,43,250,0.2)"
  card-bg: "rgba(30,43,250,0.04)"
  positive: "#059669"
  negative: "#dc2626"

radii:
  pill: "100px"
  card-lg: "14px"
  card-md: "12px"
  card-sm: "10px"
  bar: "6px"
  circle: "50%"

typography:
  # - reading ramp (Inter body + Space Grotesk chrome) -
  body:    { fontFamily: "Inter", cqw: 0.85, weight: 400, lineHeight: 1.6, color: "text-muted" }
  h4-eyebrow:{ fontFamily: "Space Grotesk", cqw: 0.8, weight: 600, tracking: "0.08em", upper: true, color: "primary" }
  tag:     { fontFamily: "Space Grotesk", px: 12, weight: 500, color: "primary" }
  counter: { fontFamily: "Space Grotesk", px: 13, weight: 500, tracking: "0.05em", color: "text-muted" }
  # - display / numerical ramp (Space Grotesk, near-black headings / cobalt numerals) -
  h3:      { fontFamily: "Space Grotesk", cqw: 1.25, weight: 500, lineHeight: 1.3, tracking: "-0.02em", color: "text" }
  stat-num:{ fontFamily: "Space Grotesk", cqw: 1.9, weight: 700, lineHeight: 1.0, color: "primary" }
  blockquote:{ fontFamily: "Space Grotesk", cqw: 2.4, weight: 500, lineHeight: 1.35, color: "text" }
  h2:      { fontFamily: "Space Grotesk", cqw: 2.6, weight: 600, lineHeight: 1.1, tracking: "-0.02em", color: "text" }
  metric-value:{ fontFamily: "Space Grotesk", cqw: 3.0, weight: 700, lineHeight: 1.0, color: "primary" }
  h1:      { fontFamily: "Space Grotesk", cqw: 4.2, weight: 700, lineHeight: 1.08, tracking: "-0.02em", color: "text" }
  quote-mark:{ fontFamily: "Space Grotesk", cqw: 8.0, weight: 700, lineHeight: 0.5, color: "primary", opacity: 0.15 }

spacing:
  pad-x: "5cqw"
  pad-y-top: "5cqw"
  gap-cards: "1.4cqw"
  accent-line: "60px × 4px"

---
