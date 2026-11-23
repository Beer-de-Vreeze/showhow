#!/usr/bin/env python3
"""Measure two gates on the rendered mp4 and print PASS or FAIL for each.

  uv run --project <skill-dir>/scripts <skill-dir>/scripts/video_gates.py video.mp4 [--srt captions.srt]

G-blank: no run of more than 3 consecutive blank frames (one flat colour: an empty ground,
         a black or white flash). Catches dead frames and flash frames the eye skims past.
         A designed cut to black at the very end may run 15 frames (0.5s at 30fps).
G-end:   the video ends no more than 1.4s after the last caption (needs --srt); 3.5s when a
         credits.txt sits next to the srt, because the outro credit line needs 2.5s with no caption
         over it. Under 0.5s is a note: the result may cut off before the viewer has read it.

Adapted from motionmaxxing's G2 and G3 gates (github.com/Tejashmakwana/motionmaxxing, Apache-2.0).
Mid-video holds are not gated: showhow holds results on purpose.
Exit code 1 when a gate fails.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# max-min of Y, U and V below this = one flat colour (H.264 noise stays under it).
# shortcut: heavy grain or a vignette over an empty ground reads as busy, and a near-black real frame
# can read as blank; upgrade to an edge or entropy measure if either shows up in a real render.
FLAT_SPREAD = 10
MAX_BLANK_RUN = 3
END_BLACK_MAX = 15  # frames: a designed cut to black at the very end (energy outros) may run 0.5s at 30fps
END_TAIL_MAX = 1.4
END_TAIL_MAX_CREDITS = 3.5  # 2.5s credit line + the outro's entrance + a short result hold
END_TAIL_MIN = 0.5


def blank_runs(frames: list[tuple[float, int]]) -> list[tuple[float, int]]:
    """frames: (time, widest Y/U/V spread). Returns (start time, length) of blank runs over MAX_BLANK_RUN.
    A run that reaches the last frame is allowed up to END_BLACK_MAX frames."""
    runs, start = [], None
    for i, (_, spread) in enumerate(frames + [(0.0, FLAT_SPREAD)]):  # sentinel closes a trailing run
        if spread < FLAT_SPREAD:
            start = i if start is None else start
            continue
        if start is not None:
            count = i - start
            limit = END_BLACK_MAX if i == len(frames) else MAX_BLANK_RUN
            if count > limit:
                runs.append((frames[start][0], count))
            start = None
    return runs


def last_caption_end(srt: Path) -> float:
    ends = re.findall(r"-->\s*(\d+):(\d+):(\d+)[,.](\d+)", srt.read_text(encoding="utf-8"))
    if not ends:
        raise SystemExit(f"no cue times found in {srt}")
    h, m, s, ms = ends[-1]
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def video_duration(video: Path) -> float:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
        capture_output=True, encoding="utf-8", errors="replace", check=False,
    )
    if probe.returncode != 0 or not probe.stdout.strip():
        raise SystemExit(f"ffprobe could not read {video}: {(probe.stderr or '').strip()}")
    return float(probe.stdout.strip())


def measure(video: Path) -> tuple[list[tuple[float, int]], float]:
    duration = video_duration(video)
    result = subprocess.run(
        ["ffmpeg", "-v", "info", "-nostats", "-i", str(video), "-an",
         "-vf", "signalstats,metadata=mode=print:file=-", "-f", "null", "-"],
        capture_output=True, encoding="utf-8", errors="replace", check=False,
    )
    if result.returncode != 0:
        raise SystemExit(f"ffmpeg failed on {video}: {(result.stderr or '').strip()[-500:]}")

    frames, t, stats = [], None, {}
    for line in (result.stdout or "").splitlines():
        if line.startswith("frame:"):
            if t is not None:
                frames.append((t, spread(stats)))
            t, stats = float(line.rsplit("pts_time:", 1)[1]), {}
        elif line.startswith("lavfi.signalstats."):
            key, _, value = line[len("lavfi.signalstats."):].partition("=")
            stats[key] = float(value)
    if t is not None:
        frames.append((t, spread(stats)))
    if not frames:
        raise SystemExit(f"no frames measured in {video}")

    return frames, duration


def spread(stats: dict[str, float]) -> int:
    return int(max(stats.get(f"{c}MAX", 255) - stats.get(f"{c}MIN", 0) for c in "YUV"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video", type=Path)
    parser.add_argument("--srt", type=Path, help="captions.srt, to time the end hold from the last spoken line")
    args = parser.parse_args()

    frames, duration = measure(args.video)
    failed = False

    runs = blank_runs(frames)
    if runs:
        failed = True
        where = ", ".join(f"{s:.2f}s ({n} frames)" for s, n in runs)
        print(f"G-blank FAIL: blank runs over {MAX_BLANK_RUN} frames at {where}")
    else:
        print(f"G-blank PASS: no blank run over {MAX_BLANK_RUN} frames in {len(frames)} frames")

    if args.srt:
        tail = duration - last_caption_end(args.srt)
        credits = (args.srt.parent / "credits.txt").exists()
        limit = END_TAIL_MAX_CREDITS if credits else END_TAIL_MAX
        why = ", credits.txt found" if credits else ""
        if tail > limit:
            failed = True
            print(f"G-end FAIL: video runs {tail:.2f}s past the last caption (max {limit}s{why}); end sooner")
        elif tail < END_TAIL_MIN:
            print(f"G-end PASS (note): {tail:.2f}s past the last caption; under {END_TAIL_MIN}s the result may cut off before it is read")
        else:
            print(f"G-end PASS: {tail:.2f}s past the last caption (max {limit}s{why})")
    else:
        print("G-end SKIPPED: no --srt given")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
