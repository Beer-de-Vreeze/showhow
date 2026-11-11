#!/usr/bin/env python3
"""Render a HyperFrames composition to mp4, loudly.

A `--quiet` render can exit non-zero with no message and no file, so this never
passes it: it logs everything to <work>/render.log, succeeds only when the CLI
exits 0 and this run wrote a non-empty mp4, retries once, and prints the log
tail on failure.

  uv run --project <skill-dir>/scripts <skill-dir>/scripts/render.py \
      <output-dir>/composition <output-dir>/<video-name>.mp4 --work <output-dir>/work [--no-fast-capture] [--no-loudnorm] [-- --docker --quality high]

--no-fast-capture: for compositions that tween layout (height, width, position,
padding); fast drawelement capture drops those changes.

After a successful render it normalises the soundtrack to -16 LUFS integrated,
-1 dBTP true peak (AES TD1004) with two-pass ffmpeg loudnorm, copying the video
stream. --no-loudnorm skips it. A failed pass exits non-zero and leaves the
rendered mp4 as it was.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable

ATTEMPTS = 2
TAIL_LINES = 20
TARGET = "I=-16:TP=-1:LRA=11"
MEASURED = ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")


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


def normalize_loudness(
    output: Path,
    work: Path,
    run: Callable[[list[str]], tuple[int, str]] = run_cli,
) -> None:
    """Two-pass loudnorm in place; the mp4 is only replaced after the second pass wrote a file."""
    work.mkdir(parents=True, exist_ok=True)
    log = work / "render.log"

    def logged(cmd: list[str]) -> tuple[int, str]:
        code, text = run(cmd)
        with log.open("a", encoding="utf-8") as f:
            f.write(f"=== {' '.join(cmd)}\n{text}\n=== exit {code}\n")
        return code, text

    def fail(what: str, text: str) -> SystemExit:
        tail = "\n".join(text.splitlines()[-TAIL_LINES:])
        return SystemExit(f"loudness {what} failed; {output} is unchanged. Log tail ({log}):\n{tail}")

    ffmpeg, ffprobe = shutil.which("ffmpeg") or "ffmpeg", shutil.which("ffprobe") or "ffprobe"
    code, text = logged([ffprobe, "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(output)])
    if code != 0:
        raise fail("probe", text)
    if not text.strip():
        print(f"loudnorm skipped: {output} has no audio stream")
        return

    code, text = logged([ffmpeg, "-hide_banner", "-nostats", "-i", str(output), "-af", f"loudnorm={TARGET}:print_format=json", "-f", "null", "-"])
    # ffmpeg prints the measurement as the last {...} block on stderr.
    blocks = re.findall(r"\{[^{}]*\}", text)
    try:
        m = json.loads(blocks[-1]) if code == 0 and blocks else None
        values = [float(m[k]) for k in MEASURED] if m else None
    except (ValueError, KeyError, TypeError):
        values = None
    if values and values[0] == float("-inf"):
        print(f"loudnorm skipped: {output} has a silent audio track")
        return
    if not values or any(v != v or v in (float("inf"), float("-inf")) for v in values):
        raise fail("measurement", text)
    i, tp, lra, thresh, offset = values

    tmp = output.with_name(output.stem + ".loudnorm.mp4")
    af = (f"loudnorm={TARGET}:measured_I={i}:measured_TP={tp}:measured_LRA={lra}"
          f":measured_thresh={thresh}:offset={offset}:linear=true")
    cmd = [ffmpeg, "-y", "-hide_banner", "-nostats", "-i", str(output), "-map", "0:v", "-map", "0:a", "-c:v", "copy", "-af", af,
           "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(tmp)]
    code, text = logged(cmd)
    if code != 0 or not tmp.is_file() or tmp.stat().st_size == 0:
        tmp.unlink(missing_ok=True)
        raise fail("normalisation", text)
    try:
        tmp.replace(output)
    except PermissionError:
        tmp.unlink(missing_ok=True)
        raise SystemExit(f"loudness normalisation could not replace {output} (open in a player?); it is unchanged. Close it and rerun.")
    print(f"loudnorm: {i} LUFS, {tp} dBTP -> {TARGET} ({output})")


def parse(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    # Everything after "--" goes to hyperframes render; argparse.REMAINDER would also swallow --work.
    ours, extra = (argv[: argv.index("--")], argv[argv.index("--") + 1 :]) if "--" in argv else (argv, [])
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("composition", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--work", type=Path, required=True, help="folder for render.log")
    p.add_argument("--no-fast-capture", action="store_true")
    p.add_argument("--no-loudnorm", action="store_true", help="skip loudness normalisation")
    return p.parse_args(ours), extra


def main() -> None:
    a, extra = parse(sys.argv[1:])
    render(a.composition, a.output, a.work, fast_capture=not a.no_fast_capture, extra=extra)
    if not a.no_loudnorm:
        normalize_loudness(a.output, a.work)


if __name__ == "__main__":
    main()
