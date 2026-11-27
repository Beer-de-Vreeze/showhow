# Three.js scenes for showhow explainer videos

Research note, read 2026-11-27.
Scope: everything three.js can do for teaching videos beyond a single schematic object, and how to keep it deterministic under Hyperframes.
Machine cutaways (procedural gears and blades, outline rendering, labels, kinematics, exploded views, headless WebGL determinism) are covered in `3d-machine-cutaways.md`; this note does not repeat them.
Claims marked **(secondary)** come from memory or from search snippets, not from a page I read; re-verify before relying on them.

## Summary

- Almost every scene type below is "load assets once, then draw as a pure function of `t`", the same contract as `hyperframes/references/types/3d.md` and `runtimes.md` [1][2].
- Clearly licensed sources exist for most topics: Natural Earth (public domain), Poly Haven and Kenney (CC0), NASA 3D resources (free, with usage guidelines), OSM (ODbL, attribution), BodyParts3D (CC BY).
- 3D earns its place for spatial data (globes, terrain, molecules, anatomy, buildings) and loses to 2D for comparing quantities (3D bars, extruded maps).
- Postprocessing and noise-based effects (AO, DoF, TAA, bloom) are the main determinism risk; prefer baked or analytic looks and diff two renders of the same frame.
- Of the wrappers, only plain three.js, GSAP-driven state and Theatre.js core (as a keyframe store) fit a seeked HTML composition; Remotion's `@remotion/three` and R3F are other render pipelines whose ideas port, not their code.

## 0. The determinism contract (applies to every scene)

- Draw only from `e.detail.time` inside the `hf-seek` listener; no `requestAnimationFrame` loop, no `THREE.Clock`, no `OrbitControls` damping [2].
- Do every slow thing once at load and register it with `window.__hf.buildReady`: texture and glTF loads, TopoJSON parsing, font SDF generation, shader compiles (`renderer.compileAsync`), simulations [1][2].
- Vendor every asset into the project (no CDN at render time); a render machine may be offline and a CDN may change.
- Fix `renderer.setPixelRatio(1)` at the output resolution; size the canvas to the composition, not the window.
- Seed all randomness (star fields, scatter, noise offsets) with a hashed index (mulberry32), never `Math.random()` [1][2].
- Test: render the same `t` twice, in different frame orders, and compare pixel hashes.
- Library animations with their own tween loops (three-globe arc dashes, 3Dmol spin, camera controls) must be replaced by values you set per frame from `t`.

## 1. 3D globes and maps

**Libraries.**
three-globe is a three.js object (not a renderer) with layers for points, arcs, polygons, hexed polygons, paths, labels and more [3].
globe.gl is a convenience wrapper around three-globe, MIT licensed [4].
Use three-globe directly inside your own scene, because globe.gl owns the render loop and controls and fights the seek protocol.
three-globe's arc layer has built-in dash animation (`arcDashAnimateTime`) that runs on its own timer [3]; in a seeked composition set it to 0 and drive the dash gap or a draw range yourself per frame **(secondary: confirm accessor names in the README)**.

**Vector data.**
Natural Earth is public domain, usable in any manner, no attribution required (credit is appreciated) [5][6].
`world-atlas` redistributes Natural Earth as TopoJSON at 110m and 50m (ISC licence for the packaging) [7].
Convert with `topojson-client` to GeoJSON, then either use three-globe polygons or triangulate yourself with `d3-geo` and `earcut`.
Natural Earth draws borders and disputed areas by its own policy; for a video that names countries, decide which version (including point-of-view variants) fits your audience **(secondary)**.

**Textured globe.**
Bake an equirectangular texture (Natural Earth raster, or a styled map rendered to a canvas) and map it onto a `SphereGeometry`.
Baking beats vector rendering for looks you control, such as flat country fills, and is deterministic.
Use anisotropy and mipmaps; check the poles and the date line seam.

**Country highlighting.**
Cheapest: draw a highlight mask into a second canvas texture (one country filled) and tween its alpha by `t`.
Alternative: extrude the country polygon by a small height as a separate mesh.

**Animated routes and arcs.**
Do it by hand: convert two lat/lon pairs to unit vectors, `slerp` between them, lift by `sin(pi * s) * h` for the arc height, and build a `TubeGeometry` or `Line2` once.
Reveal with `geometry.setDrawRange` or a shader uniform `progress` set from `t` (ease it, do not loop).
Add a moving "head" sprite at `progress`.
A great circle is the shortest path; say so in the narration if the route is not literally flown.

**Zoom from globe to region.**
Move the camera along the line to the target point (dolly, not an fov change) and swap in higher-resolution texture or a 50m polygon set at a threshold, crossfading rather than popping.
For a clean match cut to a flat 2D map, switch to an orthographic camera looking straight down at the target, so the 3D frame equals a `d3.geoOrthographic` or azimuthal projection used in the 2D scene, then cross-dissolve over a few frames.
A perspective globe and `d3.geoOrthographic` only match when the camera is far with a narrow fov; verify by overlaying the two at the cut frame.

**Terrain from elevation data.**

| Dataset | Licence / terms | Notes |
|---|---|---|
| AWS Terrain Tiles (Mapzen/Tilezen) | Mixed upstream sources; attribution list at the joerd attribution page [8] | Tile pyramid; Terrarium PNG height decode is `R*256 + G + B/256 - 32768` **(secondary)** |
| GEBCO_2026 grid (land and ocean, 15 arc-second) | Acknowledge the source with the supplied citation and DOI [9] | Best for bathymetry and global relief |
| SRTM (NASA) | US government work, generally public domain **(secondary)** | 30 m to 90 m, voids in places |
| Copernicus DEM GLO-30 | Free with attribution under Copernicus terms **(secondary, handbook not readable here)** | Better quality than SRTM |
| Mapbox terrain-RGB | Provider terms restrict use outside their products **(secondary)** | Avoid unless the account terms allow it |

Build a `PlaneGeometry` (or sphere patch), displace vertices on the CPU at load, compute normals once, and show the exaggeration factor on screen ("vertical scale x3").
Cite the dataset on an end card or in the companion text.

## 2. Scale and science scenes

**Solar system.**
Real scale cannot be shown (planets vanish); use a log or stepped scale and label it, or a "walk the real scale" scene as a long linear pan where the emptiness is the lesson.
Positions: Kepler elements evaluated at `t`, or a precomputed ephemeris table sampled at load; both are pure functions of `t`.
Models and textures: NASA 3D Resources are free to download and use, with the NASA media usage guidelines applying [10].
Other texture sets (for example Solar System Scope) carry their own CC terms **(secondary)**; read each.

**Molecules and cells.**
3Dmol.js is BSD-3-Clause and renders its own WebGL scene, not a three.js scene [11]; to keep full control, parse the PDB or mmCIF file yourself and build instanced spheres and cylinders (ball-and-stick) or a tube along the backbone in three.js.
PDB data is freely reusable (CC0 by wwPDB policy **(secondary)**); cite the PDB ID and the publication or deposition authors, as RCSB asks [12].
Cells: stylised, simplified shapes beat accurate geometry; label organelles by name with leader lines.
Mol* (RCSB's viewer) is a heavy dependency; skip it unless you need surface or cartoon representations you will not write.

**Atoms.**
Bohr-style rings teach a misconception; show a nucleus plus a probability cloud (points sampled from a seeded distribution) if you mention orbitals at all.
Scale caveat: the nucleus is about 1/100,000 of the atom's size **(secondary)**; do not draw it to scale and do say so.

**Landscapes and geology layers.**
Extrude a cross-section: stacked boxes or an extruded polygon per stratum with a flat palette and a cut face; a slice animation is a clipping plane (`material.clippingPlanes`) moved by `t`.
Terrain from section 1 plus a vertical slice gives the block-diagram look geologists use.

**Human body.**
BodyParts3D is licensed CC BY 4.0 with a required credit line [13].
Z-Anatomy builds on BodyParts3D and Wikipedia-derived definitions; its repository carries its own licence file that I could not read (I recall CC BY-SA 4.0 **(secondary)**) [14].
Share-alike on a model does not necessarily reach a video, but get that reading checked if you publish the model files or a derived mesh.
Medical content: use for orientation and naming, not diagnosis; one system (skeleton, heart) per scene.
Models are heavy: decimate, merge by material, and load as glTF with Draco or Meshopt **(secondary)**.

**Buildings and cities.**
OpenStreetMap data is ODbL; credit OpenStreetMap contributors and state that the data is under ODbL [15].
Extrude building footprints with `ExtrudeGeometry` using `height` or `building:levels` tags (levels x about 3 m as a fallback, **secondary**), merge into one mesh per colour, and bake the lighting.
For a city diorama, clip to a square tile on a plinth with a soft contact shadow.
Photorealistic city tile services usually forbid caching or recording; read their terms before using them **(secondary)**.

## 3. 3D data visualisation

**What the research says.**

- Siegrist (1996): 49 students estimated values on 3D and 2D bar and pie charts; 3D bars took slightly longer (11.6 s vs 11.1 s) with no significant accuracy difference, and 3D pies were slightly less accurate [16] (via search summary; paper not read in full).
- Fischer (2000): bars in a 3D frame took longest to compare, interpreted as higher working-memory load [17].
- Zacks et al. (1998): depth cues lowered accuracy on simple bar graphs, with the gap shrinking after a delay; MeasuringU argues the differences are practically tiny [18].
- A 2024 eye-tracking study found no significant difference in understanding between 2D and 3D bar charts [19].
- Munzner's rule "no unjustified 3D" (*Visualization Analysis and Design*) is the usual summary **(secondary, book not read here)**.
- Net: 3D bars cost time and attention, rarely help accuracy, and add occlusion and perspective distortion.
  Extruded maps add a second problem: a tall block over a large area reads as "more" for both height and area.

**When 3D helps.**
When the data is spatial and three-dimensional: terrain, molecules, anatomy, volumes, flows through a physical structure, or a sense of scale a number cannot give (a stack of N coins next to a building).
Rule for showhow: use 3D charts only as a hook or metaphor (one hero object with a number on it) and put any quantitative comparison on a 2D chart.

**If you must draw 3D bars.**
Orthographic camera, straight-on or fixed isometric, no perspective foreshortening, gridlines and axis labels as 2D overlays (section 5), value labels on the bars, no more than about 6 bars, and a fixed viewpoint (no orbit while the viewer reads values).

## 4. Stylised looks, lighting, postprocessing

**Looks.**

| Look | Technique |
|---|---|
| Low-poly | `flatShading: true`, few segments, limited palette |
| Clay | `MeshStandardMaterial` roughness near 1, soft low-contrast light, subtle AO, bevelled geometry |
| Toon | `MeshToonMaterial` with a 3 to 4 step `gradientMap` (`NearestFilter`), inverted-hull outline (outlines: see `3d-machine-cutaways.md`) |
| Paper-craft | Layers of extruded flat shapes at small z offsets, soft drop shadows between layers, paper texture as `map` or `roughnessMap` |
| Isometric diorama | `OrthographicCamera` at a fixed (1,1,1)-style angle, a square base tile, baked shadows, no perspective |

**Lighting.**
Three-point: warm key about 45 degrees to the side and above, cool low fill opposite, rim from behind to separate the subject (the house recipe in `3d.md` is warm key, cool rim, dark environment with soft strips [1]).
Environment: load a Poly Haven HDRI (all assets CC0, no attribution needed, commercial use allowed [20]) with the RGBE or EXR loader, run it through `PMREMGenerator`, and set `scene.environment`; rotate the environment, not the object, as `3d.md` advises [1].
Use the 1k or 2k HDRI; the background can be a flat colour so the HDRI only lights.
`RectAreaLight` gives soft studio strips but works only with standard and physical materials and needs its uniforms lib initialised **(secondary)**.

**Shadows and AO.**
three.js ships `BasicShadowMap`, `PCFShadowMap`, `PCFSoftShadowMap` and `VSMShadowMap` [21].
Use `PCFSoftShadowMap` with a tight, fixed shadow camera frustum, tuned `bias` and `normalBias`; a fixed frustum avoids shimmer between frames.
For grounded objects use a baked contact shadow (a blurred dark texture on a plane) instead of an AO pass.
Screen-space AO (GTAO, SAO, N8AO) is noise-based **(secondary)**: it is deterministic only if its noise pattern is fixed or seeded per frame index; otherwise bake AO into textures, which is deterministic and cheaper.

**Depth of field and postprocessing.**
pmndrs/postprocessing provides an `EffectComposer` with merged effects (bloom, DoF, vignette, SMAA and more) and recommends a linear workflow and specific renderer attributes [22].
Determinism rules for any post stack:

- Call `composer.render(deltaTime)` yourself from the seek listener with a fixed delta; never let it run on its own loop.
- Avoid effects with temporal accumulation or history (TAA, motion blur from the previous frame, temporal AO, SSR accumulation): frame N would depend on frame N-1, and frames render out of order.
- Prefer SMAA or MSAA over TAA for antialiasing.
- DoF: tween focus distance and aperture from `t` for rack focus; bokeh sampling patterns are usually fixed, but confirm with the render-twice diff.
- Clamp values that can become NaN before bloom, and keep bloom to the brightest points [1].

## 5. 3D text, typography and mixing with 2D

**3D text.**
`TextGeometry` extrudes glyphs from a typeface JSON loaded by `FontLoader`; geometry is heavy for long strings and limited to the font you convert; use it for a few big words, not captions.
troika-three-text renders SDF glyphs, parses `.ttf`, `.otf` and `.woff` directly, handles kerning, ligatures and RTL, and patches any three.js material so lights and PBR still apply [23].
Call `.sync()` after changing text and wait for it (its completion callback) before registering `buildReady`, otherwise early frames render without glyphs [23].
Load the font from a local file, not a Google Fonts URL.

**Layering 3D with HTML and SVG.**
Safest pattern: the WebGL canvas at the back, HTML and SVG labels above in normal DOM, so captions, brand and exact text stay crisp and styleable.
Match cameras: use the composition's aspect; each frame, project a 3D anchor with `vector.project(camera)` and set the element's transform to `((x+1)/2*W, (1-y)/2*H)`; hide the label if the anchor is behind the camera or occluded (raycast against hero meshes).
`CSS2DRenderer` and `CSS3DRenderer` (three.js examples) automate this, but they run on render calls, so call them from the same seek handler.
For leader lines draw SVG paths between the projected anchor and the label box.
Orthographic cameras make overlay alignment trivial and robust.
Do not tilt product UI into 3D [1].

## 6. Camera language for explainers

- Push-in (dolly): move the camera, do not change fov, to keep perspective honest; ease in and out.
- Orbit: slow and partial (a quarter to half turn) while a label appears; keep the horizon level, never roll.
- Rack focus: DoF focus distance tweened between two objects; needs the DoF effect (section 4).
- Fly-through or dive over a single hero object beats circling it [1].
- Match cut 2D to 3D: freeze the 2D element, build the 3D object at the same screen position, size and colour, and swap over 2 to 4 frames; for charts or maps use an orthographic top-down view first, then rotate into perspective.
- Perspective-to-ortho transition: tween fov toward a small value while dollying back to keep the subject size.
- Speed limits (rule of thumb, my judgment, not a standard): rotation under roughly 10 to 15 degrees per second, no peripheral-filling fast motion, no accelerating moves toward the viewer, and cut instead of whipping across big distances.
- Why it matters: the W3C understanding document for WCAG 2.3.3 says large non-essential motion can trigger vestibular reactions (dizziness, nausea), and a working-group wiki page informally treats animation over about a third of the viewport lasting over 3 seconds as significant [24].
  That criterion covers interaction-triggered motion on the web, so for video treat it as a conservative analogy; I found no source for specific vection speed thresholds.
- Give every heavy camera move a calm fallback (crossfade or static frame).

## 7. Asset sources and licences

| Source | Licence | What it gives |
|---|---|---|
| Poly Haven | CC0 for all HDRIs, textures and models; no credit needed; commercial use allowed [20] | HDRIs, PBR textures, props |
| Kenney | Game assets on the asset pages are CC0 [25] | Low-poly props, kits, UI |
| Quaternius | Each kit's licence is shown on its page and in the download's txt file [26] (commonly CC0, **secondary**) | Low-poly characters, nature, city kits |
| Sketchfab | Per-model licence, filterable (CC0, CC BY, others); CC BY needs attribution **(secondary: licence page not read)** | Huge variety, quality varies; check "downloadable" and licence on each |
| NASA 3D Resources | Free to download and use; NASA media usage guidelines apply [10] | Spacecraft, planets, mission models |
| Smithsonian Open Access and Smithsonian 3D | CC0 for Open Access content **(secondary: si.edu returned a bot check to my fetch, which I did not bypass)** | Museum objects; not every 3D item is CC0, check per object |
| Natural Earth | Public domain [5] | Maps and rasters |
| OSM | ODbL, attribution required [15] | Buildings and roads |

Keep an `assets/CREDITS.md` per video with source URL, licence and date read; showhow already saves source URLs with dates for outside steps.
Prefer glTF or GLB; use Draco or Meshopt and KTX2 only if load time matters, since render time is not the bottleneck.

## 8. Wrappers: which fit a seeked HTML composition

| Tool | Fit | Notes |
|---|---|---|
| Plain three.js plus `hf-seek` | Best | The documented route [1][2] |
| GSAP driving a state object | Best for most scenes | Already the runtime in Hyperframes; animate `{progress, camY, focus}` and read it in the seek handler [2] |
| Theatre.js | Good, as a keyframe store | Core `@theatre/core` is Apache 2.0; `@theatre/studio` is AGPL 3.0 [27]. Sequences have a settable position, so `sheet.sequence.position = t` in the seek handler gives a pure function **(secondary: confirm in docs [28])**. Author with Studio, export the state JSON, ship only core in the render. Likely overkill versus GSAP |
| React Three Fiber | Possible, heavy | Needs a bundler and `frameloop="never"` with manual advance **(secondary)**; adds a React build step to a plain-HTML composition |
| Remotion `@remotion/three` | Not inside Hyperframes | `<ThreeCanvas>` lets `useCurrentFrame()` drive scenes declaratively; `<Sequence>` needs `layout="none"` inside it; recommends the `angle` GL renderer [29][30]. Same idea as seek on a different renderer and pipeline; it also has its own licence and pricing terms (thresholds not verified) [31] |

## Scene catalogue

| Scene | Teaches what | Technique | Assets + licence | Effort |
|---|---|---|---|---|
| Globe with highlighted country | Where something is | Textured sphere, highlight mask texture tweened by `t` | Natural Earth, public domain | Low |
| Great-circle route or arc network | Flows between places (flights, trade, data centres) | Slerp arcs, `drawRange` reveal, head sprite | Natural Earth; coordinates from your data | Low-med |
| Globe-to-region zoom with match cut | Context to local detail | Dolly in, tile swap, ortho top-down, dissolve to 2D map | Natural Earth 50m, TopoJSON | Med |
| Terrain relief with labelled exaggeration | Landforms, flooding, watersheds | Displaced plane from DEM, baked light, clipping plane for water level | AWS Terrain Tiles, GEBCO, Copernicus (attribution) | Med |
| Geology block diagram | Strata, faults, erosion | Extruded layers, moving clipping plane | Own geometry; optional DEM | Med |
| Solar system tour (log scale) | Order, scale, orbits | Kepler orbits sampled at `t`, textured spheres, scale caption | NASA 3D resources (guidelines), own textures | Med |
| Molecule or protein walk-through | Shape and function | Instanced ball-and-stick or backbone tube, camera along the chain | PDB data (CC0, secondary) | Med-high |
| Atom and probability cloud | Models vs reality | Seeded point cloud, nucleus-not-to-scale caption | Own geometry | Low |
| Organ or anatomy slice | Where parts sit | Decimated glTF, layer-by-layer fade, 2D HTML labels | BodyParts3D CC BY (credit); Z-Anatomy (check licence) | High |
| City block diorama | Zoning, flooding, transit | Extruded footprints on a plinth, baked shadows, isometric ortho camera | OSM ODbL (credit) | Med |
| 3D hero number (coins vs building) | Magnitude | Instanced meshes, ortho camera, number as HTML overlay | Own geometry; Kenney CC0 props | Low |
| Isometric process diorama | A workflow as a place | Kenney or Quaternius kit, toon or clay material, fixed ortho camera | Kenney CC0, Quaternius (per kit) | Med |
| Paper-craft layered map or timeline | Stages and regions | Extruded flat layers, soft layer shadows, paper texture | Own shapes, Natural Earth | Med |
| Extruded 3D headline text | A title or key term as an object | TextGeometry or troika, HDRI lighting, rack focus | Poly Haven HDRI CC0, licensed font | Low-med |

## Pitfalls

- Hidden clocks: three-globe dash animation, 3Dmol spin, `OrbitControls` damping, `Clock` and CSS animations on overlays all break seek purity [2][3].
- Unawaited async: troika `.sync()`, texture decode, glTF and DEM loads must finish before `buildReady`, or the first frames render empty [23].
- Temporal and noisy postprocessing (TAA, SSR, noise AO) makes frames depend on order; run the render-twice diff.
- Out-of-order frame requests expose stateful code (particle integrators, camera smoothing); precompute into arrays at load [1].
- Perspective mismatch between 3D and the 2D overlay: label misalignment at the edges of a wide fov; use ortho or a narrow fov for overlay-heavy scenes.
- Misleading 3D: perspective bars and extruded maps distort comparison [16][17]; label exaggeration on terrain and scale on solar-system scenes.
- Licence traps: attribution-required sets (OSM, BodyParts3D, GEBCO, Terrain Tiles) need a credit on screen or in the companion; share-alike assets (Z-Anatomy) need a read; Smithsonian and Sketchfab licences vary per item.
- Weight: huge glTFs and 8k HDRIs slow every frame and every seek; profile the heaviest moment once [1].
- Motion comfort: long fast orbits and whip pans; follow section 6 and keep a calm fallback.
- Offline render: any remote URL (fonts, tiles, textures) is a failure waiting to happen.
- Nothing here was installed or run; determinism claims per library are design reasoning plus the Hyperframes contract, so each scene type needs its own render-twice test when built.

## Sources

Read 2026-11-27 unless marked otherwise.

1. `C:\Users\BeerdeVreeze\.agents\skills\hyperframes\references\types\3d.md` (local)
2. `C:\Users\BeerdeVreeze\.agents\skills\hyperframes\references\runtimes.md` (local)
3. https://raw.githubusercontent.com/vasturiano/three-globe/master/README.md
4. https://github.com/vasturiano/globe.gl
5. https://www.naturalearthdata.com/about/terms-of-use/
6. https://github.com/nvkelso/natural-earth-vector
7. https://github.com/topojson/world-atlas
8. https://registry.opendata.aws/terrain-tiles/ (licence points to https://github.com/tilezen/joerd/blob/master/docs/attribution.md, not opened)
9. https://www.gebco.net/data-products/gridded-bathymetry-data
10. https://science.nasa.gov/3d-resources/
11. https://raw.githubusercontent.com/3dmol/3Dmol.js/master/LICENSE
12. https://www.rcsb.org/pages/policies
13. https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html
14. https://github.com/Z-Anatomy/Models-of-human-anatomy (licence file not readable here)
15. https://www.openstreetmap.org/copyright
16. Siegrist 1996, https://www.tandfonline.com/doi/abs/10.1080/014492996120300 (via search summary)
17. Fischer 2000, https://www.researchgate.net/publication/245966272_Do_Irrelevant_Depth_Cues_Affect_the_Comprehension_of_Bar_Graphs (via search summary)
18. https://measuringu.com/is-3d-worse-than-2d/ (via search summary, includes Zacks et al. 1998)
19. https://www.mdpi.com/2673-6470/4/4/46 (via search summary)
20. https://polyhaven.com/license
21. https://threejs.org/docs/#api/en/renderers/WebGLRenderer (shadow map types listed)
22. https://raw.githubusercontent.com/pmndrs/postprocessing/main/README.md
23. https://raw.githubusercontent.com/protectwise/troika/main/packages/troika-three-text/README.md
24. https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html and https://www.w3.org/WAI/GL/wiki/Animation_caused_by_user_interaction (via search summary)
25. https://kenney.nl/support
26. https://quaternius.com/faq.html
27. https://raw.githubusercontent.com/theatre-js/theatre/main/README.md
28. https://www.theatrejs.com/docs/latest/manual/sequences (sequence position setter not confirmed)
29. https://www.remotion.dev/docs/three
30. https://www.remotion.dev/docs/gl-options
31. https://www.remotion.dev/docs/license (index page only; pricing page not read)
