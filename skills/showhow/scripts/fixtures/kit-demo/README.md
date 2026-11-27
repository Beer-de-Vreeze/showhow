# kit-demo

A 6-second composition that uses every showhow kit function: `move`, `ring`, `ripple` and `counter`.
Render it after changing the kit or upgrading HyperFrames, and look at the frames from the mp4.

From `skills/showhow/scripts`, stage a copy with `stage.py` (theme `showhow`) and snapshot it, the first and last time twice:

```bash
uv run --project . python check_fixture.py kit-demo --at 1.6,4,1.6
uv run --project . render.py out/kit-demo/composition out/kit-demo.mp4 --work out/work
uv run --project . frame_sheet.py out/kit-demo.mp4 --at 0,1.2,1.6,2.0,3.5,4.0,4.5,5.8 -o out/work/check.jpg --cols 4
```

It copies the fixture to `out/kit-demo/composition`, stages it, diffs the first and last still (0 changed pixels, or it exits 1) and keeps the stills in `out/kit-demo/stills`.

Expect in the sheet:

- 0s: "Step 1 of 2" top right, no ring, cursor at the bottom centre.
- 1.6s and 2.0s: a ring on "New report", cursor on it; the cursor rests from 1.4s, then presses (smaller for 2 frames at about 1.6s) and a ripple runs 1.65-2.15s.
- 3.5s: "Step 2 of 2", cursor between the buttons.
- 4.0s and 4.5s: a ring on "Export", cursor on it; a press at about 4.0s and a ripple 4.05-4.55s.
- 5.8s: no ring.
