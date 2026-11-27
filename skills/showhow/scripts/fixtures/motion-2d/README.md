# motion-2d

A 10-second composition with the five 2D motion styles, two seconds each:
stroke-reveal (0s), kinetic-type (2s), data-anim (4s), morph (6s) and flat-scene (8s).
Render or snapshot it after changing the kit or upgrading HyperFrames.

From `skills/showhow/scripts`, stage a copy with `stage.py` (theme `showhow`) and snapshot it, the first and last time twice:

```bash
uv run --project . python check_fixture.py motion-2d --at 0.9,2.9,5.4,7.2,9.5,0.9
```

It copies the fixture to `out/motion-2d/composition`, stages it, diffs the first and last still (0 changed pixels, or it exits 1) and keeps the stills in `out/motion-2d/stills`.

Expect, at each snapshot time:

- 0.9s: a box and an arrow drawn, no ring yet.
- 2.9s: "Heat moves, pressure follows" fully shown, words risen out of their mask.
- 5.4s: the number partway up from 0 to 1,700 and the bar partway up.
- 7.2s: the circle partway to a square.
- 9.5s: three cubes in place and the dot on the route.
