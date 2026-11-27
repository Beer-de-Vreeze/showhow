# globe-route

A 12-second `scene3d` globe: Brazil highlighted, a great-circle arc from Seville to Rio de Janeiro drawing on from 1.2 s, a zoom to the region and a match cut to the flat locator map at 6.7 s.
Render it after changing `assets/scene3d/` or upgrading HyperFrames or three.js.

From `skills/showhow/scripts`:

```bash
mkdir -p fixtures/globe-route/assets/scene3d && cp -r ../assets/scene3d/* fixtures/globe-route/assets/scene3d/
npx hyperframes snapshot fixtures/globe-route --at 3,10,3 --no-end --no-browser-gpu -o out/globe-route
```

Expect:

- The two 3s stills identical pixel for pixel (diff them; the 10s still must differ).
- At 6.5s (3D) and 7.2s (flat) the same map: coastlines, Seville and Rio markers and the route in the same places.
- Labels fade in at the ends of the legs, left and right of the globe, and are gone once the zoom starts.
