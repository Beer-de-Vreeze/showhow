# motion-2d

A 10-second composition with the five 2D motion styles, two seconds each:
stroke-reveal (0s), kinetic-type (2s), data-anim (4s), morph (6s) and flat-scene (8s).
Render or snapshot it after changing the kit or upgrading HyperFrames.
GSAP and its plugins load from local files, never a CDN; `assets/gsap/` and `assets/kit/` are not committed.

From `skills/showhow/scripts`:

```bash
mkdir -p fixtures/motion-2d/assets/kit fixtures/motion-2d/assets/gsap && cp ../assets/kit/* fixtures/motion-2d/assets/kit/
(cd "$(mktemp -d)" && npm pack gsap@3.14.2 && tar xzf gsap-3.14.2.tgz && cp package/dist/{gsap,DrawSVGPlugin,MorphSVGPlugin,SplitText,MotionPathPlugin}.min.js "$OLDPWD/fixtures/motion-2d/assets/gsap/")
(cd fixtures/motion-2d && npx -y hyperframes@0.9.85 check)
(cd fixtures/motion-2d && npx -y hyperframes@0.9.85 snapshot --at 0.9,2.9,5.4,7.2,9.5)
```

The stills and a contact sheet land in `.hyperframes/artifacts/snapshots/`.
Expect, at each snapshot time:

- 0.9s: a box and an arrow drawn, no ring yet.
- 2.9s: "Heat moves, pressure follows" fully shown, words risen out of their mask.
- 5.4s: the number partway up from 0 to 1,700 and the bar partway up.
- 7.2s: the circle partway to a square.
- 9.5s: three cubes in place and the dot on the route.
