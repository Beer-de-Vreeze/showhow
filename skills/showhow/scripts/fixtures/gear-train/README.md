# gear-train

A 12-second `scene3d` machine: a 12-tooth driver, a 24-tooth idler and a 36-tooth driven gear, labelled, with slow motion from 5s to 9s and a slow dive.
Render it after changing `assets/scene3d/` or upgrading HyperFrames or three.js, and run the determinism check (`references/3d-scenes.md`, "Check it").

From `skills/showhow/scripts`:

```bash
mkdir -p fixtures/gear-train/assets/scene3d && cp ../assets/scene3d/* fixtures/gear-train/assets/scene3d/
npx hyperframes snapshot fixtures/gear-train --at 3,10,3 --no-end --no-browser-gpu -o out/gear-train
```

Expect:

- The two 3s stills identical pixel for pixel.
- Teeth interleaved where the gears meet, never overlapping; the idler turns the other way from the driver, the driven gear the same way at a third of the driver's speed.
- Labels fade in at 0.5s, 1.0s and 1.5s, in a left and a right column, clear of the teeth.

`sample-model.gltf` is a stand-in user model (three octagonal discs named `driver`, `idler`, `driven`).
To check the `Params.model` path, add `"model": "sample-model.gltf"` to `data-params` in a copy of the fixture and snapshot it: the discs take the gears' places, motion and labels.
