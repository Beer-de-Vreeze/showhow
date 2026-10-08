"""Self-check for the ring span planner. Run:
  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/test_bake_highlights.py
"""

from bake_highlights import plan

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
    print("ok")


if __name__ == "__main__":
    main()
