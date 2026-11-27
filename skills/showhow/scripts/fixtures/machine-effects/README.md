# machine-effects

A 16-second `scene3d` machine on the gear-train build with four scenes, one per effect: airflow (0-4s), cutaway (4-8s), exploded view (8-12s) and slow motion (12-16s).
Each scene's `Params:` is a boolean switch (`"flow": true`, `"cut": true`, `"explode": true`, `"slowmo": true`) next to the usual `kind` and tooth counts.
Render it after changing `assets/scene3d/` or upgrading HyperFrames or three.js.

From `skills/showhow/scripts`, stage a copy with `stage.py` (theme `showhow`) and snapshot it, the first and last time twice:

```bash
uv run --project . python check_fixture.py machine-effects --at 3,6,10,14,3
```

It copies the fixture to `out/machine-effects/composition`, stages it, diffs the first and last still (0 changed pixels, or it exits 1) and keeps the stills in `out/machine-effects/stills`.

Expect:

- Airflow at 3s (ink dots, all labels), cutaway at 6s (sparse 45-degree hatch on the cap faces only), exploded at 10s (every part clear of the next, shafts highest), slow motion at 14s (labels clear of the zoomed machine).
