# 2D motion styles

Recipes for the explainer visual types `stroke-reveal`, `kinetic-type`, `data-anim`, `morph`, `flat-scene` and `parallax`.
Each one is a kit helper (`assets/kit/showhow-kit.js`) over a GSAP plugin; the evidence and sources are in `docs/research/2d-motion-graphics.md`.
`scripts/fixtures/motion-2d/` renders all five; copy its structure.

## Setup

- GSAP and its plugins (DrawSVG, MorphSVG, SplitText, MotionPath) are free for commercial use since 2025-04-30.
- Load them as local files from the npm `gsap` package (`dist/*.min.js` copied into `composition/assets/gsap/`), never a CDN at render time.
  From `<output-dir>` in PowerShell:
  `$t = New-Item -ItemType Directory -Force work/gsap-pkg; npm pack gsap@3.14.2 --pack-destination $t; tar -xzf "$t/gsap-3.14.2.tgz" -C $t; New-Item -ItemType Directory -Force composition/assets/gsap | Out-Null; 'gsap','DrawSVGPlugin','MorphSVGPlugin','SplitText','MotionPathPlugin' | ForEach-Object { Copy-Item "$t/package/dist/$_.min.js" composition/assets/gsap/ }`
- Register them once in `index.html`: `gsap.registerPlugin(DrawSVGPlugin, MorphSVGPlugin, SplitText, MotionPathPlugin)`.
- Follow the kit rules in `step-3-compose.md`: one `fromTo` per element with `immediateRender:false`, starting states in CSS, measure by element after `document.fonts.ready`.
- Motion earns its place: it shows the thing the sentence says, slowly enough to follow, and nothing moves for decoration.
  Keep one easing and entrance for the whole video (`design-floor.md`).

## stroke-reveal

For diagrams, structures and routes that should appear being built.

- Draw the paths in the order the voice names them.
- Constant drawing speed: duration proportional to path length.
- Connector first, then its label.
- Set `.sh-draw { opacity: 0 }` in CSS; `kit.draw(t, "#path", d)` fades it in at the first frame of the draw.
- Needs `stroke`, no `fill`, on the path; a filled shape gets a fade after it draws.
- Code-only "whiteboard" means this style on generated shapes; name it stroke reveal.

## kinetic-type

For a definition, a rule or a phrase to remember, with the words as the picture.

- `kit.words(t, "#quote")` splits into words inside a mask and lifts them 5 frames apart, never letter by letter.
- Call it after `document.fonts.ready` so lines break where they will render.
- Short phrase, one idea, held until the sentence ends; the text is not a word-for-word copy of the narration (redundancy).

## data-anim

For a quantity that changes: a counter, bars, a before and after.

- `kit.count(t, "#num", from, to, d, { decimals })` ticks the number; write the from value in the HTML.
- Use `font-variant-numeric: tabular-nums` on anything that ticks.
- Bars grow from their baseline with a plain `fromTo` on `scaleY` (`transform-origin: 50% 100%`), axes before values, scale starting at zero.
- Highlight one series at a time; one format for numbers across the video.

## morph

For "A becomes B", or a match cut into the next scene.

- `kit.morph(t, "#shape", "M... Z", d)` morphs the path's current `d` into the given path.
- Pick start and end shapes at the same position and size so the cut is a match; no blur during the morph.
- Both ends are plain paths; convert rects and circles to a path first.

## flat-scene

For an abstract process that needs a concrete picture: flat fills, a small palette, shapes from SVG primitives.

- Isometric: build solids from three flat-toned polygons (top, left, right) on a 30 degree grid and stack by explicit z-order.
- `kit.rise(t, ["#a", "#b", "#c"])` settles each element up 24px, 0.15s apart, in depth order.
- `kit.along(t, "#dot", "#route", d)` moves something that travels (a packet, a signal) along a drawn route.
- No rigged characters and no hand-made art; limit what moves at once to what the sentence is about.

## parallax

An intro scene setter only; the plan gate fails it on any scene but the first.
Move layers at speeds proportional to depth with plain `fromTo` tweens on `x` or `scale`, a slow push over the whole scene.
