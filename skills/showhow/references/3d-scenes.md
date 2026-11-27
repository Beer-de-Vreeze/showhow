# 3D scenes

A `scene3d` visual is one 3D stage per video, built in three.js and reused across scenes, so viewers see one consistent object.
Use it only when the shape is the point (`general.md`, "3D when the shape is the point"); never for UI, screens or charts.
The code lives in `assets/scene3d/`; copy that folder into the project's `assets/scene3d/` like the kit.
The recipe below is the one that held up in the gear-train fixture (`scripts/fixtures/gear-train/`); the research behind it is `docs/research/3d-machine-cutaways.md` in the repo.

## Plan

The scene carries `Visual: scene3d` and a `Params:` JSON object on one line:

```
Visual: scene3d
Params: {"kind": "machine", "driver": 12, "idler": 24, "driven": 36}
```

- `kind` picks a recipe from the Kinds table.
- `model` is the escape hatch for anything without a recipe: a glTF (`.gltf` or `.glb`) the user supplies, or one with a clear CC0 or CC BY licence noted in `work/sources.md`.
  It replaces the procedural build; `kind` may then be left out.
- Every number in `Params:` is spoken somewhere in the narration, so the model never contradicts the voice.
  `plan_gates.py` checks both rules as P-params; an unknown `kind` with no `model` fails, naming the kind.

## Kinds

| Kind | What it builds | Status |
|---|---|---|
| `machine` | Gears, shafts, discs, springs and blade rows from `Params` numbers, moving by closed-form kinematics | `assets/scene3d/machine.js` |
| `globe` | Natural Earth globe, highlighted country, great-circle route arcs, zoom to the region, match cut to the flat map | `assets/scene3d/globe.js` |
| `hero-number` | One key figure as extruded 3D text | `assets/scene3d/hero-number.js` |

A new kind is one row here, one entry in `SCENE3D_KINDS` in `scripts/plan_gates.py`, and one module in `assets/scene3d/` built on `scene3d.js`.

## The scaffold every kind uses

`assets/scene3d/scene3d.js` (three.js) and `scene3d-math.js` (pure, checked by `scripts/test_scene3d.mjs`):

| Export | What it does |
|---|---|
| `onSeek(key, build)` | Registers `window.__hf.buildReady[key]` at once, awaits `build()` and the fonts, then calls the `render(t)` that `build()` returned on every `hf-seek`; `?t=<seconds>` previews one frame in a plain browser |
| `createStage({ canvas, width, height, background, viewHeight, view })` | Renderer with pixel ratio 1, `preserveDrawingBuffer` and `stencil`; flat ambient plus one key light; `project(point)` gives frame pixels |
| `orthoCamera`, `VIEWS` | Orthographic camera from `iso`, `dimetric`, `front` or `top`; animate `camera.zoom` for a dive, never the distance |
| `part(geometry, stage, { color, edges, silhouette })` | Three-step toon fill with polygon offset, fat edge lines (`LineSegments2`, pixels at stage size), optional inverted-hull silhouette |
| `loadModel(url, stage, { size })` | Loads `Params.model`, fits and centres it, gives it the same flat look; a load failure fails the build |
| `labels(container, stage, items)` | HTML plates with SVG leaders; returns `layout(t)` for `render(t)`; plates fade in at each item's `at` |
| `hash(i, seed)`, `seedOf(text)` | Integer hash to [0, 1) and an FNV-1a seed from text; the only randomness allowed |
| `timeMap(t, keys)` | Piecewise-linear time for slow motion; slope 1 outside the keys |
| `layoutLabels(anchors, opts)` | Left and right slot columns sorted by anchor y, one pitch apart, so leaders never cross |

## Recipes

### Loading three.js

- An import map pins `three` and `three/addons/` to `three@0.184.0` on jsdelivr, as the HyperFrames registry's 3D blocks do (`runtimes.md` does not ask for a vendored copy).
- Register an empty paused GSAP timeline in `window.__timelines`; HyperFrames' static guard wants one even when the frame is drawn from `hf-seek`.
- Copy the fixture's `index.html` head as the starting point.

### Every frame from t

- `render(t)` sets every rotation, position, zoom and label from `t` alone: no clock, no `+=`, no `requestAnimationFrame`.
- Heavy work goes inside `build()`: geometry, `loadModel`, `await renderer.compileAsync(scene, camera)`.
- Slow motion goes through `timeMap`, never a changed speed plus accumulation.

### Machine: gears

- `gearGeometry({ teeth, module, width, bore })` extrudes an involute outline (`machine-math.js`, `gearOutline`), lying flat so `rotation.y` turns it; cached by its parameters.
- Two gears mesh at centre distance `module * (N1 + N2) / 2`.
- `meshAngle(parentAngle, parentTeeth, teeth, dir)` gives the meshing gear's angle, with `dir` the direction from the parent's centre to its own.
  It is checked for odd and even tooth counts in any direction: placed by it, gears touch without overlapping; half a pitch off, they overlap by most of a module.
  The often-quoted offset `pi / N2` alone is only right for an even `N2`.
- Chain a train from the driver: `a1 = meshAngle(a0, ...)`, `a2 = meshAngle(a1, ...)`; the driver angle is a function of `timeMap(t)`.
- Small tooth counts (12) look pinched at the root, as real undercut pinions do; fine for an explainer.

### Machine: other parts and motion

- `latheGeometry(profile)` for shafts, hubs, discs and casings; `springGeometry` for coil springs (scale the group to compress); `bladeRow` for an instanced blade ring (spin the row, no per-blade edges yet).
- `crankSlider(angle, r, l)` gives piston distance and rod angle in closed form.
- No escapement: a Swiss lever beat as a function of t was prototyped, but no pallet layout in the search kept the pallets out of the escape-wheel teeth, so it is not shipped; a crank-slider is the fallback linkage.

### Look

- Light background, toon fills, dark 2.5 px edges, one accent colour for the part the narration names.
- Colours come from the composition's CSS variables `--paper`, `--ink` and `--accent` (and `--muted`), read once by `createStage` into `theme`; the `showhow` frame preset's values are the fallback.
  Fills are `tint(theme.paper, theme.ink, u)` and the highlight is `theme.accent`, so a brand kit or another preset restyles the scene; never hard-code a hex in a recipe.
  Define the variables on the composition root and use `var(--ink)` for the label plates and leaders (the fixtures show it).
- Labels at least 40 px, at most 5 to 7 on screen, inside the title-safe band; check that no plate covers the object at the most zoomed frame.
- Pass `avoid: machine` to `labels` and the plate columns step outward to stay 70 px clear of the object's screen bounds, whatever the zoom or exploded height (`labelEdges`).
- In a 1080 px wide frame (vertical, square) the columns run out of room and are clamped to the edge, over the object: widen `viewHeight` (about `110 * height / width` for the gear train), keep plates to a word or two, and pass a smaller `margin` and `gap`.

### Params.model

- Name the model's nodes like the recipe's parts (the fixture uses `driver`, `idler`, `driven`), each with its origin on its own axis; `getObjectByName` then gives them the same motion and labels.
- `loadModel` centres the model's bounding box, so lay the procedural build out centred the same way when both must line up.

## Check it

- Snapshot a frame, a later one, then the first again in one run, and diff the two stills: `npx hyperframes snapshot <dir> --at 3,10,3 --no-end`; frames 90 and 300 at 30 fps.
  The two 3s stills must match pixel for pixel; any difference is hidden state.
- Do it with `--no-browser-gpu` (SwiftShader) and with `--browser-gpu`, and render one video on one path only: the two paths differ slightly from each other.
- Look at a frame sheet across the scene: teeth interleaved at the mesh points, labels clear of the object.

## Globe

`Params`:

```
{"kind": "globe", "country": "BRA", "route": [{"name": "Seville", "lat": 37.39, "lon": -5.98, "side": "right"}, {"name": "Rio de Janeiro", "lat": -22.91, "lon": -43.17, "side": "left"}]}
```

- `country` is an ISO 3166-1 code, alpha-3 or alpha-2 (`BRA`, `BR`), from the Natural Earth `ADM0_A3` and `ISO_A2_EH` columns; it fills in the accent colour over the first second.
  A code that is not in the bundled map fails P-params.
- `route` lists places in order; each pair of neighbours becomes one great-circle arc that draws on over 2 s.
  Each place is an object `{"name", "lat", "lon"}` with numeric `lat` and `lon`; the plan states every coordinate, nothing is geocoded.
  Plain names (`["Seville", "Rio de Janeiro"]`, the shorthand spec #14 shows) fail P-params: look the coordinates up and write them in.
  `lat` and `lon` are exempt from the "numbers are spoken" half of P-params; any other number in `Params` still has to be narrated.
  `side` (`left` or `right`) is optional and picks the label column.
- A globe needs a `country` or a `route` of 2 or more places; `plan_gates.py` fails it otherwise.
  Say in the narration that the arc is the shortest path if the route is not literally flown.
- `focus` (`{lat, lon}`) overrides the centre the globe settles on; the default is the mean direction of the route, or of the country's largest polygon (France settles on France, not French Guiana).
- Avoid antipodal route pairs: they have no single shortest arc.
- Data: `assets/scene3d/data/ne_110m_admin_0_countries.min.geojson`, Natural Earth 110m, public domain (see `data/README.md`).
  Pass its URL to `buildGlobe`; the file is fetched, so serve it next to the composition.
- The country borders are baked into one 6144 px equirectangular canvas texture (flat fills, no lighting), the highlight into a second one on a slightly larger shell whose opacity is a function of `t`.
  Arcs are rebuilt from `t` each frame (draw-on range and lift), which stays pure because nothing is accumulated.
- three-globe was not used: plain three.js on the scaffold is about 150 lines, and the library's arc animation runs on its own clock.

### Zoom and the match cut

- `globeTiming(P)` gives the beats: legs from 1.2 s, then a 2.5 s zoom to `ZOOM_END` while the globe settles on the centre, then the cut at `zoomEnd + 0.3 s` with a 0.4 s dissolve.
- The camera is orthographic and looks at the globe straight on, so the globe's final frame is an azimuthal orthographic map: `orthoProject(place, centre)` in `globe-math.js` is `d3.geoOrthographic().rotate([-centre.lon, -centre.lat])`.
- The 2D locator map lines up when it uses that projection with the same centre and radius `R_px = R * (pixels per world unit) * ZOOM_END` (`0.4 * frameHeight * ZOOM_END` at `viewHeight: 10`), and the arcs have settled onto the surface (their lift reaches 0 by the end of the zoom).
- `globe.flatAt(place)` gives a place's pixel position on that map, for a label or marker placed over it (a country-only globe has no route plates).
- Portrait and square: pass `viewHeight: 10 * height / min(width, height)` so the globe fits the narrow side; the scale follows the camera.
- `flatMap(canvas)` draws exactly that map, route, markers and names; the fixture stacks it above the 3D canvas and fades it in over the cut.
  A different `map` visual (an SVG or an image) has to use the same projection, centre and radius, or the cut jumps; overlay the last 3D frame and the first 2D frame to check.
- Measured on the fixture: the frames at 6.5 s (3D) and 7.2 s (flat) differ in the labels, the title plate edge and the anti-aliasing of the lines.
- A perspective camera would not match `geoOrthographic`; do not switch the camera for the zoom.

## Hero number

`Params`: `{"kind": "hero-number", "value": 1200}`.

- The text is `String(value)`, so the screen shows the digits P-params checked are spoken.
- `TextGeometry` from `three/addons/geometries/TextGeometry.js` with the `helvetiker_bold` typeface JSON that ships with three.js (MIT); `buildHeroNumber(stage, P, { fontUrl })` takes another converted font.
- The number swings in over 1.6 s with a slight sway after, all from `t`.
- Each glyph is its own mesh, spaced by `glyphOffsets` from its extruded, projected bounds plus a gap, so no glyph reaches into the next at any turn; the fill is `theme.accent`.
- Use it for one number per scene, 1 to 8 glyphs; longer strings are heavy geometry and unreadable.

Fixtures: `scripts/fixtures/globe-route/` and `scripts/fixtures/hero-number/`; both follow the gear-train recipe for the determinism check.

## Machine effects: cutaway, exploded view, slow motion, airflow

These are options on `kind: machine`, not a new kind.
`Params` switches them on with booleans (`"cut": true`, `"explode": true`, `"slowmo": true`, `"flow": true`), which the number gate ignores; when each plays is the scene's own timing.
`scripts/fixtures/machine-effects/` shows each in its own scene.
Every one is a pure function of `t`.

- Cutaway: `sectionCut(stage, machine)` returns `set(level)`.
  It clips every part under `machine` with one horizontal plane, writes the stencil (back faces +1, front faces -1) and draws a hatched cap where the count is not zero.
  Parts must be closed solids.
  Sweep the plane with `set(level)` from `render(t)`; a level of 50 or more means closed.
  Shipped: the hatch, not the flat-cap fallback: thin ink lines at 45 degrees on screen, 10 px apart and 2 px wide at 1080p (`spacing`, `line`), only on the cap; uncut surfaces keep their flat fill.
  It held up with rotating gears, a shaft in a bore and lifted parts; the cap does not outline parts that touch, so adjacent sections read as one hatched field.
- Exploded view: `explodeOffsets(parts, gap)` stacks parts `[{ y, t }]` (home height, thickness along the axis) in array order, each `gap` clear of the next, and returns each part's offset; place it at `home + offset * explodeAmount(i, t, { at, stagger, dur })`.
  Order the array so the stack climbs against the row's slope on screen (the fixture stacks the driven gear first), or an isometric view hides the levels; zoom out and lower the group as it grows.
  Spin stays a function of `t`, so parts keep turning.
- Slow motion: `timeMap`, as in the gear train; add a slow dive with `camera.zoom`.
- Airflow: `flowParticles(stage, { count, seed, size, speed, length, spread })` and `points.update(t, amount)`; ink dots with a paper ring, 16 px across, so they read on paper and on any part.
  Keep the cloud out of the group you pass to `avoid`.
  Capture a frame sheet while the particles are on screen (the fixture: 3 s) and after the labels have faded in.
  Position is `flowPoint(i, t, seed, ...)`, a hash of the index and seed, so it is stateless and repeats every `1 / speed` seconds; take the seed from `seedOf(text)`.
- three-bvh-csg is not used: no part needs real wall thickness yet.
