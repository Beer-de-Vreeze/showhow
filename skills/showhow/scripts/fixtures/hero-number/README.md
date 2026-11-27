# hero-number

A 6-second `scene3d` hero number: `1200` as extruded 3D text swinging into view.

From `skills/showhow/scripts`, stage a copy with `stage.py` (theme `showhow`) and snapshot it, the first and last time twice:

```bash
uv run --project . python check_fixture.py hero-number --at 3,5,3
```

It copies the fixture to `out/hero-number/composition`, stages it, diffs the first and last still (0 changed pixels, or it exits 1) and keeps the stills in `out/hero-number/stills`.

Expect the digits to read `1200` from 3s on, fully inside the frame, with a dark edge line on each glyph.
