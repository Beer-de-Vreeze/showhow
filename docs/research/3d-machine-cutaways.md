# 3D machine cutaways in three.js, deterministic under Hyperframes

Research for the machine explainer mode (jet engine, 110-part watch movement).
Read 2026-11-27.
Claims marked (secondary) come from search summaries or forum posts, not a primary page I read in full.
Claims marked (from knowledge) are standard geometry or three.js behaviour I did not re-verify against a page today.

## Summary

- Build every part from small parametric functions (Shape + ExtrudeGeometry for gears, LatheGeometry for round parts, TubeGeometry for springs), one function per part type, parameters straight from the script.
- Get the technical-illustration look from flat/toon fill + EdgesGeometry lines + an orthographic camera; add CSG or clipping planes only for the cutaway moment.
- Labels are plain projected HTML (CSS2DRenderer-style, but computed from `t`), with leader lines drawn in SVG and a fixed slot layout so nothing overlaps at 1080x1920.
- Motion is a pure function: gear angle = driver angle x ratio, cycle phase = (t / period) mod 1, particles = hash(index) + t; no clock, no accumulation, no `Math.random()`.
- Capture goes through headless Chrome on SwiftShader or a real GPU; that renderer difference is the main determinism risk, so pin one capture path per video and test by re-rendering frames.

## What the target looks like

The showhowai.com page (read in the browser 2026-11-27) shows a light, line-drawn isometric cutaway of a machine behind the hero.
It sells a "cutaway" scene type: `{"type": "cutaway", "parts": 5}`, labels Fan / Compressor / Combustor / Turbine / Nozzle, live numbers tied to the script ("air squeezed 40x", "1,700 C", "600 m/s"), `stages = ratio / 3.5`, and a watch movement with 110 parts where one 4 Hz beat plays in slow motion.
So the look is light background, thin dark edges, soft flat fills, one accent colour for the part being discussed.
(The screenshot was low resolution; the style notes are my reading of it.)

## 1. Procedural mechanical geometry

Rule: every part is `makeX(params) -> BufferGeometry`, centred on its own axis, with no hidden state.
Cache by params so a 110-part movement does not build 110 unique tooth profiles.

### Gears

- Spur gear = 2D `THREE.Shape` outline (tooth profile around the circle) + bore as a `Path` hole + `ExtrudeGeometry({ depth, bevelEnabled: false, curveSegments })`.
- Involute flank, base radius `rb = r_pitch * cos(pressureAngle)` (20 degrees standard):

```
// theta from 0..thetaMax
x = rb * (cos(theta) + theta * sin(theta))
y = rb * (sin(theta) - theta * cos(theta))
// mirror around tooth centre, add root arc and tip arc, repeat N times
```

- Module `m`: pitch radius `r = m*N/2`, addendum `m`, dedendum `1.25*m`, tip radius `r + m`, root radius `r - 1.25*m`.
- Meshing: two gears of the same module mesh when centre distance `a = m*(N1+N2)/2`; angular velocity ratio `w2/w1 = -N1/N2`.
- Phase so teeth interleave: `theta2 = -theta1 * N1/N2 + pi/N2 + k*2*pi/N2` (from knowledge; check visually at t=0 and flip the half-pitch offset if teeth collide).
- Pure function of time: `theta_i(t) = theta_0 + sign * omega_driver * t * (N_driver / N_i)`, chained along the train, never integrated.
- Real watch gears are mostly cycloidal (secondary); an involute look is fine for explainers, but escape wheel and pallets need their own profile.
- Helical gears are not possible with plain ExtrudeGeometry (secondary: no twist option); skip in v1 or loft rings manually.
- Generators to read, not depend on:
  - `codemonkeyricky/gear-design`: three.js Shape + Extrude, gear-train ratio solver, Swiss lever escapement model (secondary); no licence found.
  - `jamesgregson/gear_generator`: involute profile maths in JS; no licence found.
  - Write our own 60-line version instead.

### Blades, discs, shafts, housings

- Axisymmetric parts (shafts, discs, hubs, casings, nozzles, cones, balance wheels): `LatheGeometry(points, segments)` from a 2D profile; 48 to 64 segments for smooth silhouettes.
- Compressor and turbine blades: thin extruded airfoil `Shape` (camber curve from two arcs), `ExtrudeGeometry` along the span, twist applied once at build by rotating vertices around the span axis proportional to span.
- Blade rows: one blade geometry, `InstancedMesh` for N blades around a hub, `setMatrixAt` once at build; the row spins by rotating the parent group, not by rewriting matrices per frame.
- Stage count from the script: `rows = Math.round(stages)`; radius tapers from inlet to exit; rotor and stator alternate.
- Springs (hairspring, mainspring, valve spring): `TubeGeometry(curve, tubularSegments, radius, radialSegments)` with a custom `Curve` (helix, or Archimedean spiral for a hairspring).
- Spring motion: rebuilding the tube per frame is too slow, so scale the group along the axis for coil springs and rotate the end for spirals (cheat, cheap).
- Housings with holes or slots: `Shape` with `holes` + Extrude, or CSG (below).

### CSG for cutaways

- `three-bvh-csg` (MIT per its package.json; peer deps three >=0.179 and three-mesh-bvh >=0.9.7; npm 0.0.17 to 0.0.18) provides `Brush`, `Evaluator`, and operations `ADDITION`, `SUBTRACTION`, `REVERSE_SUBTRACTION`, `INTERSECTION`, `DIFFERENCE`, `HOLLOW_SUBTRACTION`, `HOLLOW_INTERSECTION`.

```
const a = new Brush(casingGeo, mat), b = new Brush(wedgeGeo, mat)
a.updateMatrixWorld(); b.updateMatrixWorld()
const cut = new Evaluator().evaluate(a, b, SUBTRACTION)
```

- README constraints: geometry must be two-manifold (watertight, no interpenetrating triangles); do not modify a brush's geometry after creating it.
- LatheGeometry is only watertight if the profile is a closed ring section (inner wall, outer wall, end caps joined); an open profile gives bad CSG (from knowledge).
- Run CSG at load time, once per cut, never per frame.
  A fixed quarter-wedge removed from the casing is the cheap deterministic default.
- Register the heavy step in `window.__hf.buildReady` (3d.md, runtimes.md).

### Section planes and cut faces without CSG

- `material.clippingPlanes = [plane]` with `renderer.localClippingEnabled = true` clips in world space; points with negative signed distance are clipped (Material docs).
- Capping the hole: the official `webgl_clipping_stencil` example draws back and front faces into the stencil buffer, then a plane mesh draws the cap where the stencil is set.
  The renderer is created with `stencil: true`, and `renderOrder` controls pass order.
- Animating the plane constant is a pure function of t: `plane.constant = lerp(a, b, ease(u))`.
- Choice: clipping planes for animated section sweeps (cheap, no CSG); CSG for a fixed cutaway where wall thickness must be real geometry.

## 2. Technical-illustration look

- Camera: `OrthographicCamera`.
  Isometric = position `(d, d, d)` looking at the origin, or dimetric (about 35.264 degrees elevation, 45 azimuth).
  Parallel lines stay parallel, which is the whole look.
  Animate `zoom` plus `updateProjectionMatrix()` for a dive, not camera distance.
- Fill: `MeshToonMaterial` with a 2 or 3 step `gradientMap` (`DataTexture`, `NearestFilter`), or flat `MeshBasicMaterial` colours.
  No PBR, no environment lighting.
  One directional light plus ambient.
- Edges, by increasing cost:
  1. `EdgesGeometry(geo, thresholdAngle)` (default 1 degree) drawn with `LineSegments`; 1 px lines are too thin at 1080x1920, so:
  2. `LineSegments2` + `LineMaterial({ linewidth, resolution })` from `three/addons/lines/`; convert with `LineSegmentsGeometry.fromEdgesGeometry()` (secondary); `linewidth` is in pixels and `resolution` must match the render size.
     Fat lines are the practical default for video.
  3. Inverted hull: duplicate mesh with `side: BackSide`, vertices pushed along normals in the vertex shader; gives silhouettes of curved surfaces, which EdgesGeometry does not (threejsdemos toon demo, secondary).
  4. Post-process outline (`OutlinePass` or a depth/normal Sobel): silhouettes and creases in one pass but a full-screen cost and resolution-dependent width.
- v1 combination: EdgesGeometry fat lines for creases + inverted hull for silhouettes on lathe parts.
  Give fills `polygonOffset` (factor 1, units 1) against z-fighting; polygon offset can change at runtime without `needsUpdate` (manual).
- Conditional lines: the LDraw example (`webgl_loader_ldraw`, `LDrawConditionalLineMaterial`) draws a segment only when its control points lie on the same side of the line in screen space, giving clean edges on smooth surfaces without tessellation lines.
  Garrett Johnson's `threejs-sandbox/conditional-lines` generalises it to any geometry (MIT).
  Worth a v2 spike; v1 does fine with the hull.
- Hidden lines (see-through behind a cutaway): second pass with low alpha and `depthFunc: GreaterDepth` (from knowledge).
- Cross-hatched cut faces: cap plane (stencil cap or CSG cut face) with a `ShaderMaterial` that computes hatch from object-space or world-space coordinates, never screen-space or noise:

```
float h = step(0.5, fract((p.x + p.y) * density));   // 45 degree lines
// smooth the step with fwidth to anti-alias
```

  World-space or object-space keeps the hatch glued to the part during camera moves.
  Rotate the hatch angle per part so adjacent parts read as separate (drawing convention).
- Colour discipline: neutral grey-blue parts, one accent for the part under discussion, one hatch colour for cut faces.

## 3. Labels

- `CSS2DRenderer` + `CSS2DObject` (official addon): each DOM element is wrapped in an object in the scene graph; each render projects its 3D position and applies a CSS translate; overlay needs `pointer-events: none`; supports only 100% browser and display zoom (docs).
  It updates every element every render and cost climbs at 200+ elements (secondary).
  It cannot occlude behind geometry (secondary).
- Recommended for showhow: project ourselves inside the same `render(t)` call (`v.clone().project(camera)`, NDC to pixels) and set `transform` on absolutely positioned elements.
  Same result as CSS2DRenderer, but explicit in the seek path.
  If using CSS2DRenderer, call `labelRenderer.render` in the same `hf-seek` handler.
- Leader lines: one SVG line per label from anchor pixel to label box edge, plus an anchor dot.
  Occlusion: have the script mark which anchors are visible per camera keyframe, or fade a label when its anchor is behind a part (ray test or comparing depth).
- Overlap avoidance, deterministic and cheap, no physics solver: fixed label columns at left and right (portrait: top and bottom bands), sort labels by anchor y, assign slots in order one row pitch apart; leaders then cannot cross.
  For label sets that change with time, compute the layout from `t` only.
- Legibility at 1080x1920 (my judgement, not from a source): text at least 40 px, 2 px leaders, solid or semi-opaque plate behind text, at most 5 to 7 labels visible, label width at most about 40 percent of frame width, keep out of platform UI zones (top about 10 percent, bottom about 20 percent).
- Numbers in labels come from script parameters, so editing the script changes the label (the site's `stages = ratio / 3.5` pattern).

## 4. Motion as a pure function of t

Rule: read `t` from the Hyperframes `hf-seek` listener (`e.detail.time`) and set every transform from scratch (3d.md, runtimes.md).
Frames render out of order, so no `clock.getDelta()`, no `+=`.

```
function render(t) {
  const tau = timeMap(t)                       // slow motion = piecewise-linear time map
  const phase = (tau / period) % 1             // machine cycle 0..1
  gearA.rotation.z = omega * tau
  gearB.rotation.z = -omega * tau * NA / NB + phaseOffset
  setExplode(ease(clamp01((t - te0) / dur)))
  camera.zoom = lerp(z0, z1, ease(...)); camera.updateProjectionMatrix()
  renderer.render(scene, camera); layoutLabels(t)
}
```

- Gear trains: ratios chained from the driver.
  Slow motion multiplies time through `timeMap`, so it is still a pure function; never change `omega` and also integrate.
- Crank-slider: crank angle `a = phase*2*pi`, crank radius `r`, rod length `l`: piston position `x = r*cos(a) + sqrt(l^2 - (r*sin(a))^2)`; rod angle `asin(r*sin(a)/l)`.
  Valve lifts are tables over crank angle.
- Escapement (Swiss lever): tabulate pallet fork angle over one beat (lock, impulse, drop, lock) and step the escape wheel one tooth per beat: `wheelAngle = (floor(beats) + ease(frac(beats))) * 2*pi/N`.
  4 Hz = 28,800 beats per hour (matches the site).
  Balance oscillation `A*sin(2*pi*f*t)` with f = 2 Hz for a 4 Hz beat (two beats per oscillation).
- Mechanisms solved iteratively (four-bar): fixed iteration count from a fixed start pose each frame, never from the previous frame.
  Closed forms where they exist.
- Particles (air, fuel, flame): stateless `p_i(t) = path(fract(u_i + speed*t))` with `u_i = hash(i)` and lateral offset `hash(i+1)`, using an integer hash (mulberry32 style), not `Math.random()` and not `fract(sin())` (GPU-dependent).
  `Points` or `InstancedMesh` with a few thousand points is cheap.
  Compressor squeeze: density up and spacing down per stage index.
- Fluids beyond that (swirl, flame): bake once at load into typed arrays and look up by `t` ("simulate once at load", 3d.md).
  Trails: draw N past samples `p_i(t - k*dt)`, no stored history.
- Exploded view: per part `home` and `explodeVector` (usually along the main axis); position `home + explodeVector * e_i(t)` with `e_i = ease(clamp01((x - i*stagger) / dur))`.
  Moving parts keep running while exploded (their rotation stays a function of `t`).
- Camera paths: `CatmullRomCurve3.getPoint(u)` or keyframed lerp of position, zoom and target with `u = ease((t - t0)/dur)`. showhow general.md: dive or exploded view, not an orbit; moves of 0.8 s or slower.
- RNG: seed from a hash of the script; never `Math.random()`, `Date.now()` or `performance.now()`.

## 5. Headless capture: performance and determinism

What Hyperframes does (heygen-com/hyperframes repo, issues and DeepWiki; all secondary):
- Prefers chrome-headless-shell.
  Two capture modes: BeginFrame (virtual time) and a Puppeteer screenshot fallback after seeking.
- It probes for hardware WebGL; with no GPU it launches with `--use-gl=angle --use-angle=swiftshader`, so WebGL runs on CPU.
- An issue reports, on one setup, two renders differing in 61 of 2768 frames under load; earlier failures were BeginFrame on an NVIDIA GPU with `--use-angle=gl-egl`.
- Under WSL2 the GPU is not used; native Windows with `--browser-gpu` is reported about 5x faster than SwiftShader.
  Beer works on native Windows, so this matters.

Practical rules:
- New headless with `--disable-gpu` has no WebGL at all; since Chrome 137 the automatic SwiftShader fallback is gone, so launch flags `--use-gl=angle --use-angle=swiftshader` (and `--enable-unsafe-swiftshader` on some builds) are needed (secondary).
- `preserveDrawingBuffer: true` matters when frames are read back from the canvas (`toDataURL`, `readPixels`); plain screenshots usually work without it (secondary).
  Set it anyway if unsure; small perf cost.
- `devicePixelRatio`: fix it.
  Use `renderer.setPixelRatio(1)` and a canvas at final composition size; do not read `window.devicePixelRatio` in the capture path.
- Anti-aliasing: MSAA patterns differ between SwiftShader and real GPUs.
  For identical frames across machines, render at 2x and downscale (supersampling) or accept small differences (judgement).
  Stencil capping needs `stencil: true`; test MSAA plus stencil on SwiftShader.
- Other determinism threats: fat-line `resolution`, shader precision and `fwidth` per GPU, `Math.random`, async texture loads, fonts.
- Setup: `await renderer.compileAsync(scene, camera)` inside a `window.__hf.buildReady[key]` promise; never `requestAnimationFrame`, clocks or timers in setup (runtimes.md).
- Fonts: `@font-face` from project files and `await document.fonts.load('600 40px Name')` plus `document.fonts.ready` inside `buildReady` (from knowledge).
  Prefer HTML labels over canvas-texture text at 1080x1920 (resampling blur).
- Performance on SwiftShader (CPU): few draw calls (under about 300; `InstancedMesh`, `mergeGeometries` for static plates per material), no shadow maps, no bloom or SSAO, no full-screen outline pass in v1.
  Profile the heaviest frame once (3d.md).
- Test: render frame N, seek to five other frames, render N again, diff; any difference means hidden state.

## 6. Existing examples and libraries

| What | Use | Licence |
|---|---|---|
| three.js core and addons (ExtrudeGeometry, LatheGeometry, TubeGeometry, EdgesGeometry, LineSegments2, CSS2DRenderer, LDraw) | everything above | MIT (GitHub API) |
| `webgl_clipping`, `webgl_clipping_advanced`, `webgl_clipping_stencil` | section planes and stencil caps | MIT (three.js repo) |
| `webgl_loader_ldraw` + `LDrawConditionalLineMaterial` | conditional edge lines, best technical-drawing reference in three.js | MIT |
| `gkjohnson/three-bvh-csg` | CSG for cutaways | MIT (package.json, secondary) |
| `gkjohnson/three-mesh-bvh` | dependency of the above | MIT (GitHub API) |
| `gkjohnson/threejs-sandbox` `conditional-lines` | conditional lines for any geometry | MIT (GitHub API) |
| `codemonkeyricky/gear-design` | involute gears, gear-train solver, lever escapement | none found; read only |
| `jamesgregson/gear_generator` | involute profile maths | none found; read only |
| `RopleyIT/InvoluteGears` | involute and cycloidal wheel, escape wheel, ratchet vectors (not three.js) | none found; read only |
| `koppi/involute-gear-generator`, `JB07-198/GearGen-3D`, `dymaxionkim/GPG` | other gear generators | not checked |
| threejsdemos.com toon demo | toon, inverted hull, hatching ideas | not checked; read only |

Papers for later (not fetched, from knowledge): Hertzmann, "Introduction to 3D Non-Photorealistic Rendering"; Saito and Takahashi, "Comprehensible Rendering of 3-D Shapes" (G-buffer edges).

## Recipe: v1 machine, ranked

1. Foundation: pure `render(t)` in `hf-seek`, orthographic isometric camera, `buildReady` promise, fixed pixel ratio, seeded integer hash helper.
2. Part library: `makeGear`, `makeLathe`, `makeBladeRow` (`InstancedMesh`), `makeSpring` (`TubeGeometry`), cached by params; machine = data (parts with `home`, `explode` vector, `driver` and ratio) built from script parameters.
3. Look: flat or 3-step toon fills + `LineSegments2` fat edges from `EdgesGeometry` + inverted-hull silhouettes on lathe parts; one accent colour for the focus part.
4. Motion: closed-form kinematics of `tau(t)` (gear-train ratios, crank-slider, escapement beat table), slow motion by time map, exploded view by staggered ease.
5. Labels: our own projected HTML + SVG leaders, sorted slot columns, fonts preloaded, text and numbers bound to script parameters.
6. Cutaway: one animated clipping plane with a world-space hatch cap via stencil; upgrade to a three-bvh-csg wedge only for parts needing real wall thickness.
7. Airflow: stateless particles `path(hash(i) + speed*t)`.
8. Determinism check: render frame N, seek away, render N again, diff.

Skip in v1: conditional lines, post-process outlines, helical gears, shadows, bloom, glTF beyond loading into the same `render(t)`.

## Pitfalls

- Accumulated time (`+= dt`, `clock`) breaks seek; recompute every transform from `t`.
- Non-watertight Lathe or Extrude output into CSG gives holes or garbage; close profiles, merge vertices.
- Z-fighting between fills and edge lines: `polygonOffset` on fills; fat-line pixel width must scale with output size.
- Gear teeth interpenetrating at t=0: wrong phase offset; check at t=0 and half a tooth later.
- Clipping planes are world space; moving the machine moves the cut unless the plane is transformed too.
- Stencil caps with nested or transparent parts get wrong parity; keep capped parts few and closed.
- HTML labels ignore occlusion; labels for hidden parts show unless the script picks visible anchors.
- Label overlap and crossing leaders at portrait width; cap the count, sort anchors.
- SwiftShader and GPU frames differ slightly; do not mix capture paths in one video.
- `devicePixelRatio` differs per host; fix it.
- Fonts not loaded at first capture produce fallback-font frames.
- One NaN pixel can blank a frame via bloom (3d.md); clamp divisions in custom shaders.
- 110 unique small meshes tank SwiftShader; merge static parts, instance repeated ones.

## Not verified

- Hatch shader, escapement table and gear phase formula are from knowledge; not tested here.
- No frame-determinism test was run; Hyperframes behaviour is from search summaries of its repo and issues.
- Licences of the gear-generator repos could not be confirmed.
- three.js example and doc contents were seen through search summaries only (WebFetch was unavailable).

## Sources

All read 2026-11-27 (search summaries unless noted).

1. https://showhowai.com/ (read in browser: page text and screenshot)
2. https://threejs.org/docs/pages/CSS2DRenderer.html
3. https://threejs.org/docs/pages/CSS2DObject.html
4. https://www.intelligentgraphicandcode.com/development/threejs-interfaces/html-integration (secondary: label cost, occlusion)
5. https://threejs.org/examples/webgl_clipping_stencil.html and https://github.com/mrdoob/three.js/blob/dev/examples/webgl_clipping_stencil.html
6. https://threejs.org/examples/webgl_clipping.html
7. https://threejs.org/docs/pages/Material.html (clippingPlanes)
8. https://threejs.org/docs/pages/EdgesGeometry.html
9. https://threejs.org/docs/examples/en/lines/LineSegments2.html
10. https://threejs.org/docs/pages/MeshToonMaterial.html
11. https://threejsdemos.com/demos/shaders/toon (secondary: inverted hull, hatching)
12. https://threejs.org/examples/webgl_loader_ldraw.html and https://threejs.org/docs/pages/LDrawLoader.html
13. https://github.com/gkjohnson/threejs-sandbox/tree/master/conditional-lines and https://discourse.threejs.org/t/ldraw-like-edges/17100
14. https://github.com/gkjohnson/three-bvh-csg and https://github.com/gkjohnson/three-bvh-csg/blob/main/package.json
15. https://github.com/gkjohnson/three-mesh-bvh (licence via GitHub API)
16. https://github.com/mrdoob/three.js/blob/master/src/geometries/ExtrudeGeometry.js
17. https://github.com/codemonkeyricky/gear-design
18. https://github.com/jamesgregson/gear_generator
19. https://github.com/RopleyIT/InvoluteGears
20. https://deepwiki.com/heygen-com/hyperframes/5.1-frame-capture-and-browser-management (secondary)
21. https://github.com/heygen-com/hyperframes/pull/8533 and https://github.com/heygen-com/hyperframes/issues/5548 (secondary)
22. https://github.com/Gharib89/skills/issues/917 (secondary: determinism under load, 61 of 2768 frames)
23. https://renderscreenshot.com/glossary/webgl-headless and https://microlink.io/blog/webgl-without-a-gpu (secondary: SwiftShader flags, preserveDrawingBuffer)
24. Local: skills/showhow/references/general.md ("3D when the shape is the point"), .agents/skills/hyperframes/references/types/3d.md and references/runtimes.md
