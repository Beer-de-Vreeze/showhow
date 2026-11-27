# globe-route

A 12-second `scene3d` globe: Brazil highlighted, a great-circle arc from Seville to Rio de Janeiro drawing on from 1.2 s, a zoom to the region and a match cut to the flat locator map at 6.7 s.
Render it after changing `assets/scene3d/` or upgrading HyperFrames or three.js.

From `skills/showhow/scripts`, stage a copy with `stage.py` (theme `showhow`) and snapshot it, the first and last time twice:

```bash
uv run --project . python check_fixture.py globe-route
```

It copies the fixture to `out/globe-route/composition`, stages it, diffs the first and last still (0 changed pixels, or it exits 1) and keeps the stills in `out/globe-route/stills`.

Expect:

- At 6.5s (3D) and 7.2s (flat) the same map: coastlines, Seville and Rio markers and the route in the same places.
- Labels fade in at the ends of the legs, left and right of the globe, and are gone once the zoom starts.
