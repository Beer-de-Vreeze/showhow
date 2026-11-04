# kit-demo

A 6-second composition that uses every showhow kit function: `move`, `ring`, `ripple` and `counter`.
Render it after changing the kit or upgrading HyperFrames, and look at the frames from the mp4.

From `skills/showhow/scripts`:

```bash
mkdir -p fixtures/kit-demo/assets/kit && cp ../assets/kit/* fixtures/kit-demo/assets/kit/
(cd fixtures/kit-demo && npx hyperframes check)
uv run --project . render.py fixtures/kit-demo out/kit-demo.mp4 --work out/work
uv run --project . frame_sheet.py out/kit-demo.mp4 --at 0,1.2,1.6,2.0,3.5,4.0,4.5,5.8 -o out/work/check.jpg --cols 4
```

Expect in the sheet:

- 0s: "Step 1 of 2", no ring, cursor at the bottom left.
- 1.6s and 2.0s: a ring on "New report", cursor on it; a ripple at 1.5-2.0s.
- 3.5s: "Step 2 of 2", cursor between the buttons.
- 4.0s and 4.5s: a ring on "Export", cursor on it; a ripple at 3.9-4.4s.
- 5.8s: no ring.
