"""Self-check for the ring span planner. Run:
  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/test_bake_highlights.py
"""

import json
import tempfile
from pathlib import Path

from PIL import Image

from bake_highlights import bake, plan

BOX = {"x": 10, "y": 10, "w": 50, "h": 20}


def expect_exit(spec: dict, text: str) -> None:
    try:
        plan(spec)
    except SystemExit as e:
        assert text in str(e), e
        return
    raise AssertionError(f"expected an error containing {text!r}")


def main() -> None:
    shows = [{"t": 0, "name": "board"}, {"t": 30, "name": "menu", "fade": 0.12}]

    # Float noise (an end of 21.136 against a ring starting at 21.14) must not drop a ring.
    _, ov = plan({"shows": shows, "rings": [
        {"t": 19.4, "d": 1.736, "screen": "board", **BOX},
        {"t": 21.14, "d": 2, "screen": "board", **BOX},
    ]})
    assert [o["id"] for o in ov] == ["board-r0", "board-r1"], ov
    assert ov[0]["out"] == 21.26 and ov[0]["out_dur"] == 0.01, ov[0]  # touching spans swap
    assert ov[1]["in_dur"] == 0.12 and ov[1]["out_dur"] == 0.2, ov[1]

    # Overlapping rings share a span; a ring still up at a screen change ends with that cut.
    stills, ov = plan({"shows": shows, "rings": [
        {"t": 27, "d": 2, "screen": "board", **BOX},
        {"t": 28, "d": 5, "screen": "board", **BOX},
    ]})
    assert [len(s["rings"]) for s in stills] == [1, 2, 1], stills
    assert ov[-1]["out"] == 30 and ov[-1]["out_dur"] == 0.12, ov[-1]

    expect_exit({"shows": shows, "rings": [{"t": 31, "d": 1, "screen": "board", **BOX}]}, "menu shows then")
    expect_exit({"shows": [{"t": 0, "name": "a~b"}], "rings": [{"t": 1, "d": 1, "screen": "a~b", **BOX}]}, "CSS-safe")

    # A hard cut (fade 0 or none) ends the ring at the cut instead of fading it over the next screen.
    for fade in (0, None):
        _, ov = plan({"shows": [{"t": 0, "name": "board"}, {"t": 30, "name": "menu", "fade": fade}],
                      "rings": [{"t": 29, "d": 5, "screen": "board", **BOX}]})
        assert ov[0]["out"] == 30 and ov[0]["out_dur"] == 0.01, ov[0]

    with tempfile.TemporaryDirectory() as d:
        base = Path(d)
        (base / "screens").mkdir()
        Image.new("RGB", (200, 100), "white").save(base / "screens" / "board.png")
        spec = base / "rings.json"
        theme = base / "theme.css"  # as stage.py writes it
        theme.write_text(":root {\n  --paper: #EEF3F5;\n  --accent: #D9822B;\n}\n", encoding="utf-8")

        # A target at the image edge: the padding is clamped instead of failing.
        spec.write_text(json.dumps({"pad": 6, "shows": [{"t": 0, "name": "board"}],
                                    "rings": [{"t": 1, "d": 1, "screen": "board", "x": 0, "y": 0, "w": 50, "h": 20}]}), encoding="utf-8")
        assert [p.name for p in bake(spec, theme)] == ["board-r0.png"]
        assert (base / "rings.overlays.json").exists()
        # The ring is drawn in the staged theme's accent (#D9822B), here on the top edge of the clamped ring.
        assert Image.open(base / "rings" / "board-r0.png").getpixel((28, 1)) == (0xD9, 0x82, 0x2B)

        # A "color" overrides the accent where it would vanish into the screenshot (a blue ring on a blue toolbar):
        # per ring, or for the whole spec (the older field); the ring's own wins.
        ringed = json.loads(spec.read_text(encoding="utf-8"))
        spec.write_text(json.dumps({**ringed, "color": "#000000"}), encoding="utf-8")
        bake(spec, theme)
        assert Image.open(base / "rings" / "board-r0.png").getpixel((28, 1)) == (0, 0, 0)
        ringed["rings"][0]["color"] = "#0000FF"
        spec.write_text(json.dumps({**ringed, "color": "#000000"}), encoding="utf-8")
        bake(spec, theme)
        assert Image.open(base / "rings" / "board-r0.png").getpixel((28, 1)) == (0, 0, 255)
        ringed["rings"][0].pop("color")
        spec.write_text(json.dumps(ringed), encoding="utf-8")

        # A colour PIL can't read, or a theme without --accent, fails by name instead of a traceback or a default.
        other, t2 = base / "other.json", base / "t2.css"
        for bad_spec, bad_theme, text in (({**ringed, "color": "oklch(0.6 0.1 200)"}, theme.read_text(encoding="utf-8"), "oklch"),
                                          (json.loads(spec.read_text(encoding="utf-8")), ":root { --ink: #000; }", "--accent")):
            other.write_text(json.dumps(bad_spec), encoding="utf-8")
            t2.write_text(bad_theme, encoding="utf-8")
            try:
                bake(other, t2)
            except SystemExit as e:
                assert text in str(e), e
            else:
                raise AssertionError(f"expected a failure naming {text}")

        # A box really outside the image fails, and leaves no overlays file pointing at missing stills.
        (base / "rings.overlays.json").unlink()
        spec.write_text(json.dumps({"shows": [{"t": 0, "name": "board"}],
                                    "rings": [{"t": 1, "d": 1, "screen": "board", "x": 180, "y": 0, "w": 50, "h": 20}]}), encoding="utf-8")
        try:
            bake(spec, theme)
        except SystemExit as e:
            assert "falls outside" in str(e), e
        else:
            raise AssertionError("expected a box outside the image to fail")
        assert not (base / "rings.overlays.json").exists()

        spec.write_text(json.dumps({"scale": 2}), encoding="utf-8")
        try:
            bake(spec, theme)
        except SystemExit as e:
            assert "give" in str(e), e
        else:
            raise AssertionError("expected a spec without rings or stills to fail")
    print("ok")


if __name__ == "__main__":
    main()
