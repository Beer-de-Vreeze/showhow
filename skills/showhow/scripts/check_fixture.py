"""Stage a fixture and check it draws every frame from t alone.

  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/check_fixture.py <fixture> [--theme showhow] [--at 3,10,3]

Copies scripts/fixtures/<fixture> to scripts/out/<fixture>/composition, stages it with stage.py, snapshots it
with the pinned HyperFrames (SwiftShader, --no-browser-gpu) at the given times, and diffs the first and the
last still, which must be the same time: any changed pixel is hidden state. Prints the count and exits 1 if
it is not 0. The stills stay in scripts/out/<fixture>/stills for a look.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops

from render import HYPERFRAMES
from stage import resolve, stage

HERE = Path(__file__).resolve().parent


def repeated_pair(stills: Path) -> tuple[Path, Path]:
    """The first and last snapshot (frame-NN-at-<t>s.png), which must share a time."""
    frames = sorted(stills.glob("frame-*-at-*.png"))
    if len(frames) < 2:
        raise SystemExit(f"fewer than two snapshots in {stills}")
    times = [re.search(r"-at-(.+)\.png$", f.name).group(1) for f in (frames[0], frames[-1])]
    if times[0] != times[1]:
        raise SystemExit(f"the first and last snapshot must be the same time, got {times[0]} and {times[1]}")
    return frames[0], frames[-1]


def changed_pixels(a: Path, b: Path) -> int:
    with Image.open(a) as x, Image.open(b) as y:
        if x.size != y.size:
            raise SystemExit(f"stills differ in size: {a.name} {x.size}, {b.name} {y.size}")
        r, g, b = ImageChops.difference(x.convert("RGB"), y.convert("RGB")).split()
    # A pixel is changed when any channel differs: the per-pixel channel maximum is above 0.
    most = ImageChops.lighter(ImageChops.lighter(r, g), b)
    return most.width * most.height - most.histogram()[0]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("fixture", help="a folder name in scripts/fixtures")
    p.add_argument("--theme", default="showhow")
    p.add_argument("--at", default="3,10,3", help="snapshot times; the first and last must match")
    args = p.parse_args(argv)
    src = HERE / "fixtures" / args.fixture
    if not (src / "index.html").is_file():
        raise SystemExit(f"no fixture {args.fixture!r}: {src} has no index.html")
    out = HERE / "out" / args.fixture
    shutil.rmtree(out, ignore_errors=True)  # only ever scripts/out/<fixture>, which this script writes
    comp = out / "composition"
    shutil.copytree(src, comp)
    stage(comp, resolve(theme=args.theme))
    npx = shutil.which("npx") or "npx"
    cmd = [npx, "-y", HYPERFRAMES, "snapshot", str(comp), "--at", args.at, "--no-end", "--no-browser-gpu", "-o", str(out / "stills")]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise SystemExit(f"snapshot failed ({r.returncode}):\n{r.stdout[-3000:]}{r.stderr[-3000:]}")
    first, last = repeated_pair(out / "stills")
    n = changed_pixels(first, last)
    print(f"{args.fixture}: {n} changed pixels between {first.name} and {last.name} (stills in {out / 'stills'})")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
