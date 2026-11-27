# machine-effects

A 16-second `scene3d` machine on the gear-train build with four scenes, one per effect: airflow (0-4s), cutaway (4-8s), exploded view (8-12s) and slow motion (12-16s).
Each scene's `Params:` is a boolean switch (`"flow": true`, `"cut": true`, `"explode": true`, `"slowmo": true`) next to the usual `kind` and tooth counts.
Render it after changing `assets/scene3d/` or upgrading HyperFrames or three.js.

From `skills/showhow/scripts`:

```bash
mkdir -p fixtures/machine-effects/assets/scene3d && cp ../assets/scene3d/* fixtures/machine-effects/assets/scene3d/
npx hyperframes snapshot fixtures/machine-effects --at 3,10,3 --no-end --no-browser-gpu
```

Expect:

- The two 3s stills (airflow particles on screen) identical pixel for pixel.
- Closed at 0.5s, cut at 5.5s with a hatched cap, exploded at 10s with the shafts highest, slow motion at 14s.
