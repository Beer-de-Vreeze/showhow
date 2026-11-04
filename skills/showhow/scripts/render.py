#!/usr/bin/env python3
"""Render a HyperFrames composition to mp4, loudly.

A `--quiet` render can exit non-zero with no message and no file, so this never
passes it: it logs everything to <work>/render.log, succeeds only when the CLI
exits 0 and this run wrote a non-empty mp4, retries once, and prints the log
tail on failure.

  uv run --project <skill-dir>/scripts <skill-dir>/scripts/render.py \
      <output-dir>/composition <output-dir>/<video-name>.mp4 --work <output-dir>/work [--no-fast-capture] [-- --docker --quality high]

--no-fast-capture: for compositions that tween layout (height, width, position,
padding); fast drawelement capture drops those changes.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable

ATTEMPTS = 2
TAIL_LINES = 20


def run_cli(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
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
    # The 1s slack covers filesystems that store modification times in whole seconds.
    started = time.time() - 1
    for attempt in range(1, ATTEMPTS + 1):
        code, text = run(cmd)
        with log.open("a", encoding="utf-8") as f:
            f.write(f"=== attempt {attempt}: {' '.join(cmd)}\n{text}\n=== exit {code}\n")
        # A non-zero exit fails even with a file: a crashed render can leave a truncated mp4.
        if code == 0 and output.is_file() and output.stat().st_size > 0 and output.stat().st_mtime >= started:
            print(f"rendered {output} ({output.stat().st_size} bytes), log: {log}")
            return

    tail = "\n".join(log.read_text(encoding="utf-8").splitlines()[-TAIL_LINES:])
    raise SystemExit(f"render failed: no mp4 at {output} after {ATTEMPTS} attempts (check free disk space). Log tail ({log}):\n{tail}")


def parse(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    # Everything after "--" goes to hyperframes render; argparse.REMAINDER would also swallow --work.
    ours, extra = (argv[: argv.index("--")], argv[argv.index("--") + 1 :]) if "--" in argv else (argv, [])
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("composition", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--work", type=Path, required=True, help="folder for render.log")
    p.add_argument("--no-fast-capture", action="store_true")
    return p.parse_args(ours), extra


def main() -> None:
    a, extra = parse(sys.argv[1:])
    render(a.composition, a.output, a.work, fast_capture=not a.no_fast_capture, extra=extra)


if __name__ == "__main__":
    main()
