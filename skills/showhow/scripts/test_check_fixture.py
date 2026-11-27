"""Self-check for check_fixture.py's diff of the two 3s stills. Run:
  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/test_check_fixture.py
"""

import tempfile
from pathlib import Path

from PIL import Image

from check_fixture import changed_pixels, repeated_pair


def main() -> None:
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        a = Image.new("RGB", (40, 30), (243, 236, 221))
        a.save(d / "frame-00-at-3s.png")
        a.save(d / "frame-02-at-3s.png")
        b = a.copy()
        b.putpixel((5, 5), (35, 32, 27))
        b.save(d / "frame-01-at-10s.png")
        (d / "contact-sheet.jpg").write_bytes(b"not a frame")

        # The first and the last still are the repeated time, in the snapshot's own frame order.
        first, last = repeated_pair(d)
        assert (first.name, last.name) == ("frame-00-at-3s.png", "frame-02-at-3s.png"), (first, last)

        assert changed_pixels(first, last) == 0
        assert changed_pixels(first, d / "frame-01-at-10s.png") == 1
        b.putpixel((6, 5), (243, 236, 222))  # one channel off by one still counts
        b.save(d / "x.png")
        assert changed_pixels(first, d / "x.png") == 2

        Image.new("RGB", (41, 30)).save(d / "wide.png")
        try:
            changed_pixels(first, d / "wide.png")
        except SystemExit as e:
            assert "size" in str(e), e
        else:
            raise AssertionError("stills of different sizes must fail, not compare")

        (d / "frame-02-at-3s.png").rename(d / "frame-02-at-4s.png")
        try:
            repeated_pair(d)
        except SystemExit as e:
            assert "same time" in str(e), e
        else:
            raise AssertionError("the first and last stills must be at the same time")
    print("ok")


if __name__ == "__main__":
    main()
