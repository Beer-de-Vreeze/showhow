"""Stage a fixture and check it draws every frame from t alone.

  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/check_fixture.py <fixture> [--theme showhow] [--at 3,10,3]

Copies scripts/fixtures/<fixture> to scripts/out/<fixture>/composition, stages it with stage.py, snapshots it
with the pinned HyperFrames (SwiftShader, --no-browser-gpu) at the given times, and diffs the first and the
last still, which must be the same time: any changed pixel is hidden state. Prints the count and exits 1 if
it is not 0. The stills stay in scripts/out/<fixture>/stills for a look.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageChops

from render import run_cli, write_stills
from stage import resolve, stage

HERE = Path(__file__).resolve().parent


def snapshot_pair(comp: Path, at: str, stills: Path, run=run_cli) -> tuple[Path, Path]:
    """Snapshots of comp at the --at times (render.write_stills, SwiftShader), and the first and last, which must share a time."""
    times = [float(t) for t in at.split(",")]
    if len(times) < 2 or times[0] != times[-1]:
        raise SystemExit(f"--at {at}: the first and last snapshot must be the same time")
    os.environ.setdefault("npm_config_yes", "true")  # npx fetches the pinned version without a prompt nobody would see
    write_stills(comp, times, stills, run=run, extra=["--no-browser-gpu"])
    return stills / "scene-01.png", stills / f"scene-{len(times):02d}.png"


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
    first, last = snapshot_pair(comp, args.at, out / "stills")
    n = changed_pixels(first, last)
    print(f"{args.fixture}: {n} changed pixels between {first.name} and {last.name} (stills in {out / 'stills'})")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
