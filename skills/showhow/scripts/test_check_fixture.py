"""Self-check for check_fixture.py's snapshot pair and its diff. Run:
  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/test_check_fixture.py
"""

import tempfile
from pathlib import Path

from PIL import Image

from check_fixture import changed_pixels, snapshot_pair


def main() -> None:
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        a = Image.new("RGB", (40, 30), (243, 236, 221))
        a.save(d / "same.png")
        b = a.copy()
        b.putpixel((5, 5), (35, 32, 27))
        b.save(d / "one.png")

        assert changed_pixels(d / "same.png", d / "same.png") == 0
        assert changed_pixels(d / "same.png", d / "one.png") == 1
        b.putpixel((6, 5), (243, 236, 222))  # one channel off by one still counts
        b.save(d / "x.png")
        assert changed_pixels(d / "same.png", d / "x.png") == 2

        Image.new("RGB", (41, 30)).save(d / "wide.png")
        try:
            changed_pixels(d / "same.png", d / "wide.png")
        except SystemExit as e:
            assert "size" in str(e), e
        else:
            raise AssertionError("stills of different sizes must fail, not compare")

        # The pair is the first and the last --at time, in --at order even past 10 stills (frame-10 sorts before
        # frame-2 as text), taken by render.write_stills with --no-browser-gpu (SwiftShader).
        calls = []

        def snapshot(cmd):
            calls.append(cmd)
            dest = Path(cmd[cmd.index("-o") + 1])
            dest.mkdir(parents=True, exist_ok=True)
            for i, at in enumerate(cmd[cmd.index("--at") + 1].split(",")):
                (dest / f"frame-{i}-at-{at}s.png").write_text(f"{i}", encoding="utf-8")
            return 0, "ok\n"
        at = "3," + ",".join(str(n) for n in range(4, 14)) + ",3"
        first, last = snapshot_pair(d / "comp", at, d / "stills", run=snapshot)
        assert (first.read_text(encoding="utf-8"), last.read_text(encoding="utf-8")) == ("0", "11"), (first, last)
        assert "--no-browser-gpu" in calls[0], calls

        try:
            snapshot_pair(d / "comp", "3,10,4", d / "stills", run=snapshot)
        except SystemExit as e:
            assert "same time" in str(e), e
        else:
            raise AssertionError("the first and last stills must be at the same time")
    print("ok")


if __name__ == "__main__":
    main()
