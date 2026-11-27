# gear-train

A 12-second `scene3d` machine: a 12-tooth driver, a 24-tooth idler and a 36-tooth driven gear, labelled, with slow motion from 5s to 9s and a slow dive.
Render it after changing `assets/scene3d/` or upgrading HyperFrames or three.js, and check it.

From `skills/showhow/scripts`, stage a copy with `stage.py` (theme `showhow`) and snapshot it, the first and last time twice:

```bash
uv run --project . python check_fixture.py gear-train
```

It copies the fixture to `out/gear-train/composition`, stages it, diffs the first and last still (0 changed pixels, or it exits 1) and keeps the stills in `out/gear-train/stills`.

Expect:

- Teeth interleaved where the gears meet, never overlapping; the idler turns the other way from the driver, the driven gear the same way at a third of the driver's speed.
- Labels fade in at 0.5s, 1.0s and 1.5s, in a left and a right column, clear of the teeth.

`sample-model.gltf` is a stand-in user model (three octagonal discs named `driver`, `idler`, `driven`).
To check the `Params.model` path, add `"model": "sample-model.gltf"` to `data-params` in `out/gear-train/composition/index.html` after a check and snapshot that folder: the discs take the gears' places, motion and labels.
