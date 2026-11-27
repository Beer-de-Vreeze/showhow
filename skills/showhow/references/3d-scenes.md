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
| `globe` | Natural Earth globe, highlighted country, great-circle route arcs | #24 |
| `hero-number` | One big extruded 3D number | #24 |

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
- Labels at least 40 px, at most 5 to 7 on screen, inside the title-safe band; check that no plate covers the object at the most zoomed frame.

### Params.model

- Name the model's nodes like the recipe's parts (the fixture uses `driver`, `idler`, `driven`), each with its origin on its own axis; `getObjectByName` then gives them the same motion and labels.
- `loadModel` centres the model's bounding box, so lay the procedural build out centred the same way when both must line up.

## Check it

- Snapshot a frame, a later one, then the first again in one run, and diff the two stills: `npx hyperframes snapshot <dir> --at 3,10,3 --no-end`; frames 90 and 300 at 30 fps.
  The two 3s stills must match pixel for pixel; any difference is hidden state.
- Do it with `--no-browser-gpu` (SwiftShader) and with `--browser-gpu`, and render one video on one path only: the two paths differ slightly from each other.
- Look at a frame sheet across the scene: teeth interleaved at the mesh points, labels clear of the object.
