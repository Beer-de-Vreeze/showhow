# hero-number

A 6-second `scene3d` hero number: `1200` as extruded 3D text swinging into view.

From `skills/showhow/scripts`:

```bash
mkdir -p fixtures/hero-number/assets/scene3d && cp -r ../assets/scene3d/* fixtures/hero-number/assets/scene3d/
mkdir -p fixtures/hero-number/assets/gsap && (cd "$(mktemp -d)" && npm pack gsap@3.14.2 && tar xzf gsap-3.14.2.tgz && cp package/dist/gsap.min.js "$OLDPWD/fixtures/hero-number/assets/gsap/")
npx hyperframes snapshot fixtures/hero-number --at 0.5,3,5 --no-end --no-browser-gpu -o out/hero-number
```

Expect the digits to read `1200` from 3s on, fully inside the frame, with a dark edge line on each glyph.
