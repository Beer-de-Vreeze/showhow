#!/usr/bin/env python3
"""Render a HyperFrames composition to mp4, loudly.

A `--quiet` render can exit non-zero with no message and no file, so this never
passes it: it logs everything to <work>/render.log, succeeds only when the mp4
exists and is not empty, retries once, and prints the log tail on failure.

  uv run --project <skill-dir>/scripts <skill-dir>/scripts/render.py \
      <output-dir>/composition <output-dir>/<video-name>.mp4 --work <output-dir>/work [--no-fast-capture] [-- --docker --quality high]

--no-fast-capture: for compositions that tween layout (height, width, position,
padding); fast drawelement capture drops those changes.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import time
from pathlib import Path
from typing import Callable

ATTEMPTS = 2
TAIL_LINES = 20


def run_cli(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", check=False)
    return result.returncode, result.stdout


def render(
    composition: Path,
    output: Path,
    work: Path,
    fast_capture: bool = True,
    extra: list[str] | None = None,
    run: Callable[[list[str]], tuple[int, str]] = run_cli,
) -> None:
    # shutil.which finds npx.cmd on Windows, which subprocess can't resolve from a bare "npx".
    cmd = [shutil.which("npx") or "npx", "hyperframes", "render", str(composition), "--output", str(output)]
    if not fast_capture:
        cmd.append("--experimental-fast-capture=false")
    cmd += [a for a in extra or [] if a != "--quiet"]

    work.mkdir(parents=True, exist_ok=True)
    log = work / "render.log"
    log.write_text("", encoding="utf-8")
    # An mp4 left from an earlier run proves nothing; only one written after this start counts.
    started = time.time() - 1
    for attempt in range(1, ATTEMPTS + 1):
        code, text = run(cmd)
        with log.open("a", encoding="utf-8") as f:
            f.write(f"=== attempt {attempt}: {' '.join(cmd)}\n{text}\n=== exit {code}\n")
        if output.is_file() and output.stat().st_size > 0 and output.stat().st_mtime >= started:
            if code != 0:
                print(f"render exited {code} but wrote {output}; check {log}")
            print(f"rendered {output} ({output.stat().st_size} bytes), log: {log}")
            return

    tail = "\n".join(log.read_text(encoding="utf-8").splitlines()[-TAIL_LINES:])
    raise SystemExit(f"render failed: no mp4 at {output} after {ATTEMPTS} attempts (check free disk space). Log tail ({log}):\n{tail}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("composition", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--work", type=Path, required=True, help="folder for render.log")
    p.add_argument("--no-fast-capture", action="store_true")
    p.add_argument("extra", nargs=argparse.REMAINDER, help="after --: flags passed to hyperframes render, e.g. -- --docker --quality high")
    a = p.parse_args()
    extra = a.extra[1:] if a.extra[:1] == ["--"] else a.extra
    render(a.composition, a.output, a.work, fast_capture=not a.no_fast_capture, extra=extra)


if __name__ == "__main__":
    main()
