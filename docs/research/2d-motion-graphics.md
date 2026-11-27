# 2D motion graphics for the showhow explainer mode

Researched 2026-11-27.
Claims carry a source number from the Sources section.
"Secondary" means I only saw it in a search summary or a blog, not the owner's own page.
"General knowledge" means no source was read; treat it as unverified.

## Summary

- Best fit for a code-only, deterministic, agent-built pipeline: stroke reveal, kinetic typography, infographic/data animation, shape morphing, and flat vector or isometric scenes built from SVG primitives.
- GSAP and all its plugins (DrawSVG, MorphSVG, SplitText, MotionPath) are free for commercial use under the Webflow-era license effective 2025-04-30 [1][2].
- Only GSAP (timeline `progress()`/seek) and lottie-web (`goToAndStop`) can be driven to an exact time inside our HTML page; Remotion, Motion Canvas and Manim are their own renderers [7][9][11][13][15].
- Evidence favors representational animation that is slow enough to perceive and free of decoration; irrelevant extras cost learning [21][22][23][24].
- Character animation, cutout/collage and hand-drawn whiteboard need hand-made art; do not offer them as agent-built styles.

## Styles

Technique lists are my synthesis from general motion-design practice plus the cited examples; only cited lines are sourced claims.

### Kinetic typography
- Defined by: words are the visual, timed to the spoken word.
- Techniques: per-word or per-line stagger, mask reveals, scale or colour emphasis on the key word, ease-out entrances, hard cuts between phrases.
- House rule: showhow already says words arrive whole, 4-6 frames apart, never letter by letter [25].
- Suits: definitions, rules, a claim to remember, quote cards.
- GSAP: SplitText with `mask: "lines"` and `onSplit` returning the tween [6].
- Example: GSAP's SplitText docs demos [6]; no reputable explainer example read.

### Flat vector (Kurzgesagt style)
- Defined by: flat fills, small palette, soft gradients and glow, rounded shapes, characters built from primitives.
- Techniques: artwork split into hundreds of layers, rigged joints, anticipation, overshoot, follow-through, staggered entrances; narration sets timing [18, secondary].
- Cost: the studio says at least 1,200 hours per video, made in Illustrator plus After Effects [18, secondary].
- Suits: concept explainers, science, systems.
- Agent-buildable subset: icons and scenes from SVG primitives with palette and gradient tokens; no rigged characters.
- GSAP: timeline with `stagger`, `back.out`, grouped `<g>` transforms.
- Example: Kurzgesagt [18].

### Infographic / data animation
- Defined by: quantities as shapes (bars, rings, counters, icon arrays).
- Techniques: grow from baseline, count-up with tabular numerals, highlight one series at a time (signaling), consistent scale, labels next to marks.
- Suits: statistics, comparisons, before/after; overlaps the already decided chart type.
- GSAP: tween `scaleY` or attributes; tween an object value with `onUpdate` for counters.
- Example: Manim's `BarChart`, `NumberLine`, `Axes` show the idiom [13].

### Whiteboard / hand-drawn
- Defined by: a hand appears to draw sketches on a white surface while the narrator speaks.
- Real production: an illustrator draws on a whiteboard, it is filmed and re-timed to narration in After Effects [19, secondary].
- Code version: reveal a pre-made drawing with a mask or stroke, optionally with a hand image [19, secondary].
- Suits: abstract ideas, talks, history.
- Needs hand-made art: the drawings and the hand.
  Stroke reveal of generated shapes is the no-art fallback (below).
- Example: RSA Animate by Cognitive Media [19, secondary].

### Isometric illustration
- Defined by: objects on a 30-degree grid, no perspective, usually three flat tones per solid (general knowledge).
- Techniques: cube/prism helpers that project (x, y, z) to 2D, lift and slide along grid axes, exploded views, stagger by depth order, explicit z-order.
- Suits: infrastructure, stacks, cloud diagrams, process layers.
- Agent-buildable: yes, SVG polygons.
- Overlap: the decided three.js cutaway covers the "shape is the point" case [25]; isometric SVG is the cheaper 2D cousin.
- GSAP: transform a group along the iso axes; `stagger` by distance from origin.
- Example: none read.

### Cutout / collage
- Defined by: photos or paper-textured shapes cut out and moved as flat pieces, often with a held-frame, jittery feel (general knowledge).
- Techniques: stepped easing, jittered position, torn edges, layered parallax.
- Suits: history, culture, news explainers, mood.
- Needs hand-made or sourced art: clean cutouts need background removal and licensed assets.
- GSAP: `steps(n)` ease for the held-frame look.
- Example: none read.

### Simple character animation
- Defined by: a character acts and reacts; rigs with joints or swappable pose and mouth sprites.
- Techniques: squash and stretch, anticipation, follow-through, overlap, arcs; Kurzgesagt rigs characters with joints [18, secondary].
- Suits: story and persona-driven content.
- Needs hand-made art: character and poses.
  Rive and Lottie fit here but need authored files [14][16].

### Shape morphing and transitions
- Defined by: one shape becomes another; scene changes happen through a shape growing, wiping or morphing.
- Techniques: match cuts (same position and size either side), compatible start and end shapes, no blur mid-morph.
- Suits: "A becomes B" (a step, a before/after) and bridges between scenes.
- GSAP: MorphSVG between two paths [4].
  Manim's `Transform` is the same idea [13].
- Example: GSAP MorphSVG demo, diamond to lightning bolt [4].

### Line drawing / stroke reveal
- Defined by: paths draw themselves; diagrams build line by line.
- Techniques: constant drawing speed (duration proportional to path length), draw from the middle outward, connector first then label.
- Suits: diagrams, routes, flows; gives a drawn feel without a drawn asset.
- GSAP: DrawSVG, which drives `stroke-dashoffset` and `stroke-dasharray` [3].
- Example: GSAP's house demo draws each segment in turn at consistent speed [3].

### 2.5D parallax
- Defined by: flat layers at different depths moving at different speeds (general knowledge).
- Techniques: layered scene, slow camera push, offset and scale proportional to depth, eased camera.
- Suits: scene setters, intros, "zoom into the system".
- Needs layered art: generated flat vector layers can work; photographic layers need cutouts.
- GSAP: per-layer `x`/`scale` tweens on one timeline with a depth multiplier.
- Risk: motion for its own sake; see teaching evidence.

### Other common styles found
- Math-object transformation (3Blue1Brown, built with Manim): objects morph into each other to carry an argument [13].
- Screen-recording with callouts and mixed-media type: common, not researched.

## Tools

| Tool | License | Deterministic seek in HTML? | Use for us |
|---|---|---|---|
| GSAP core | Free for everyone incl. commercial; restriction on tools competing with Webflow's visual animation builder [1][2] | Yes: timelines expose `progress()` [7]; the kit already uses seek-safe tweens [26] | Primary engine |
| DrawSVG | Free [1][2] | Yes, tween of dash properties [3] | Stroke reveal, diagrams |
| MorphSVG | Free [1][2] | Yes, tween of the `d` data [4] | Shape morph |
| SplitText | Free [1][2] | Yes after the split; splitting must run after fonts load (not verified in render) [6] | Kinetic type |
| MotionPath | Free [1][2] | Yes, tween along a path [5] | Dot along a route or flow |
| Remotion | Free for individuals, teams up to 3, qualifying non-profits; company license otherwise [8] | No: its own React renderer, content is a function of `useCurrentFrame()` [9]; not embeddable in our composition | Idea source only |
| Motion Canvas | MIT [10] | No: own editor, generator timeline and renderer [11] | Idea source only |
| Manim (Community) | MIT [12] | No: Python, renders its own video [13] | Idea source for transitions |
| Lottie (lottie-web) | MIT [14] | Yes: `goToAndStop(value, isFrame)` [15]; needs authored Lottie JSON | Only for ready-made icons; no authoring from code |
| Rive | Web runtime MIT [16]; editor terms not checked | Not verified; runtime has its own render loop [17] | Skip: needs authored .riv files |

Manim ideas reproducible with GSAP (my mapping of the Manim reference [13]):
- `Create`, `Write`, `DrawBorderThenFill`: DrawSVG, then fade in the fill.
- `Transform`, `ReplacementTransform`: MorphSVG between two paths.
- `FadeIn`, `FadeOut`, `GrowFromCenter`, `GrowArrow`: opacity and scale tweens with a transform origin.
- `LaggedStart`, `AnimationGroup`, `Succession`: GSAP `stagger` and timeline positions.
- `Indicate`, `Circumscribe`, `Flash`, `Wiggle`: scale pulse, drawn box around a target, ring burst, small rotation wobble.
- `MoveAlongPath`: MotionPath.
- `ChangingDecimal`, `ValueTracker`: tween an object, write text in `onUpdate`.
- Hard: `TransformMatchingShapes`, `TransformMatchingTex` (need matching glyph shapes), `ApplyMatrix` and complex-function warps.
- Motion Canvas idea: generator scenes with `all()` for parallel work map to nested timelines [11].

## Teaching evidence

- Mayer's principles split into those that reduce extraneous processing (coherence, signaling, redundancy, spatial and temporal contiguity) and those that manage essential processing (segmenting, pre-training, modality) [20, secondary].
- Coherence: people learn more when extraneous material is left out; 23 of 23 tests, median effect 0.86 [20, secondary].
- Redundancy: graphics plus narration beat graphics plus narration plus on-screen text [20, secondary].
- Seductive details (interesting but irrelevant additions) lowered recall and transfer in four experiments, and signaling did not remove the effect [21].
- Rey's meta-analysis found a significant seductive detail effect, small to medium for retention and medium for transfer, with moderators such as cognitive load [22, secondary summary].
- Counter-evidence: one later study found no significant main effect in an animated lesson [22, secondary summary].
  "Decoration always harms" is likely but not settled.
- Animation versus static: Tversky, Morrison and Betrancourt found the evidence for animation not encouraging, because animated versions often carried extra information or interactivity [23].
- They propose the Congruence Principle (the graphic matches the concept) and the Apprehension Principle (changes must be slow and clear enough to perceive) [23].
- Hoffler and Leutner's meta-analysis of 26 studies found an overall advantage for animation, d = 0.37, larger when representational rather than decorational (d = 0.40) [24].
- Contiguity and segmenting are properties of our pipeline: one visual per sentence, labels beside the marks, one idea per segment.

What a motion style should avoid to stay a teaching video:
- Decoration that carries no meaning (floating particles, bouncing icons, looping backgrounds).
- Motion faster than the viewer can follow [23].
- On-screen text that repeats the narration word for word [20, secondary].
- Labels far from the object they name.
- Many things moving at once with no cue to the one that matters; signal with one highlight or one motion.
- Story or character animation unrelated to the content [21].

## Recommendation

Ranked by fit: feasible in GSAP/SVG, deterministic, good for teaching, buildable by an agent without hand-made assets.

1. Stroke reveal and diagram build-up (connectors, outlines, flows).
   GSAP: DrawSVG.
   Same idea as Manim `Create`/`Write`; supports signaling and segmenting directly.
2. Kinetic typography for definitions, rules and quote cards.
   GSAP: SplitText with mask reveals.
   Matches the house rule of whole words, 4-6 frames apart [25].
3. Infographic / data animation (bars, rings, counters, icon arrays).
   GSAP: tween object values with `onUpdate`.
   Representational by nature.
4. Shape morph for "A becomes B" and match-cut transitions.
   GSAP: MorphSVG.
   Equivalent of Manim `Transform`.
5. Flat vector from primitives, with an isometric variant (cube and prism helpers).
   GSAP: timeline `stagger` with `back.out`; MotionPath for things that travel.
   Agent-built scenes only, no rigged characters.
6. 2.5D parallax as a light scene setter.
   GSAP: per-layer tweens on a shared timeline with a depth multiplier.
   Lowest teaching value; offer for intros only.

Needs hand-made art, do not offer as agent-built: character animation, cutout/collage, hand-drawn whiteboard footage, authored Lottie and Rive files.
Offer "whiteboard" only in its code form (stroke reveal on generated shapes) and name it that way.
Keep one motion signature per video, as the design floor already requires [25]; every style above should reuse it.

## Sources

Date read for every source: 2026-11-27.

1. https://gsap.com/pricing/ - GSAP is free for everyone, supported by Webflow.
2. https://gsap.com/standard-license/ - effective 2025-04-30; formerly members-only plugins (SplitText, MorphSVG) free incl. commercial use; prohibited use: tools competing with Webflow's visual animation builder; AI-generated GSAP code allowed.
3. https://gsap.com/docs/v3/Plugins/DrawSVGPlugin/
4. https://gsap.com/docs/v3/Plugins/MorphSVGPlugin/
5. https://gsap.com/docs/v3/Plugins/MotionPathPlugin/
6. https://gsap.com/docs/v3/Plugins/SplitText/ - chars, words, lines, `mask`, `autoSplit`, `onSplit` (v3.13+).
7. https://gsap.com/docs/v3/GSAP/Timeline/ - `progress()` and playhead control.
8. https://www.remotion.dev/docs/license/faq - free license eligibility.
9. https://www.remotion.dev/docs/the-fundamentals - frame number in, React render out.
10. https://github.com/motion-canvas/motion-canvas - MIT license.
11. https://motioncanvas.io/docs/quickstart and https://motioncanvas.io/docs/rendering - generator scenes, editor-based rendering.
12. https://github.com/ManimCommunity/manim/blob/main/LICENSE - MIT.
13. https://docs.manim.community/en/stable/ - reference list of Create, Write, Transform, LaggedStart, Indicate, MoveAlongPath, BarChart and others (class pages themselves not read in detail).
14. https://raw.githubusercontent.com/airbnb/lottie-web/master/LICENSE.md - MIT.
15. https://github.com/airbnb/lottie-web - `goToAndStop(value, isFrame)`.
16. https://github.com/rive-app/rive-wasm - web runtime, MIT.
17. https://rive.app/docs/runtimes/web/web-js
18. https://kurzgesagt.org/what-we-do?visit=videos - studio page; the 1,200 hours, Illustrator plus After Effects and rigging details came from a search summary and write-ups (secondary), not read directly.
19. http://archive.pov.org/blog/news/2011/12/the-rsa-animate-series-straddles-a-squiggly-line-between-web-video-and-documentary/ and https://slurpystudios.com/whiteboard-animation-a-how-to/ - search summaries only (secondary).
20. https://www.cambridge.org/core/books/abs/cambridge-handbook-of-multimedia-learning/principles-for-reducing-extraneous-processing-in-multimedia-learning-coherence-signaling-redundancy-spatial-contiguity-and-temporal-contiguity-principles/CD5B7AE1279A9AB81F8EEBB53DBEC86E - chapter listing; grouping and the 23 of 23 / 0.86 figures come from a search summary (secondary).
21. https://eric.ed.gov/?id=EJ576496 - Harp and Mayer 1998, abstract via search summary.
22. https://www.sciencedirect.com/science/article/abs/pii/S1747938X12000413 - Rey 2012, via search summary.
23. https://www.sciencedirect.com/science/article/abs/pii/S1071581902910177 - Tversky, Morrison and Betrancourt 2002, abstract via search summary.
24. https://www.sciencedirect.com/science/article/abs/pii/S0959475207001077 - Hoffler and Leutner 2007, abstract via search summary.
25. Local: C:\Users\BeerdeVreeze\repos\showhow\skills\showhow\references\design-floor.md and references\general.md (house motion rules, 3D rule).
26. Local: C:\Users\BeerdeVreeze\repos\showhow\skills\showhow\assets\kit\showhow-kit.js (seek-safe `fromTo` tweens).
