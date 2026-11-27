#!/usr/bin/env python3
"""Render a HyperFrames composition to mp4, loudly.

A `--quiet` render can exit non-zero with no message and no file, so this never
passes it: it logs everything to <work>/render.log, succeeds only when the CLI
exits 0 and this run wrote a non-empty mp4, retries once, and prints the log
tail on failure.

  uv run --project <skill-dir>/scripts <skill-dir>/scripts/render.py \
      <output-dir>/composition <output-dir>/<video-name>.mp4 --work <output-dir>/work [--no-fast-capture] [--no-loudnorm] [-- --docker --quality high]

--format: one render per format, each to <video-name>-<format>.mp4 (landscape 1920x1080,
vertical 1080x1920, square 1080x1080), also when only one is given. Each format renders
a copy of the composition in <work>/formats/<format>/ whose root gets data-format and whose
composition elements sized like the root (root, sub-composition hosts, compositions/*.html roots)
get the format's data-width and data-height; the original is never edited, and CSS keys layout off
[data-format="vertical"]. The root needs data-width and data-height. A failing format is named and
exits non-zero; formats that rendered are kept, each normalised as it finished. Without --format
the composition renders as is.

--prepare-only (with --format): write the per-format copies and stop; no render, no loudnorm.

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


# The render is what ships, so it runs a pinned Hyperframes; keep in step with $Hyperframes in install.ps1.
# shortcut: the agent's own `npx hyperframes check/snapshot/tts` calls still take npm's cached or latest
# version; pin those too (a package.json in the output folder) if a version mismatch ever shows up.
HYPERFRAMES = "hyperframes@0.9.85"


def render(
    composition: Path,
    output: Path,
    work: Path,
    fast_capture: bool = True,
    extra: list[str] | None = None,
    run: Callable[[list[str]], tuple[int, str]] = run_cli,
) -> None:
    # A missing composition fails the same way every time: say so instead of retrying a long render.
    if not (composition / "index.html").is_file():
        raise SystemExit(f"no index.html in {composition}; pass the composition folder")
    # shutil.which finds npx.cmd on Windows, which subprocess can't resolve from a bare "npx".
    cmd = [shutil.which("npx") or "npx", HYPERFRAMES, "render", str(composition), "--output", str(output)]
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


FORMATS = {"landscape": (1920, 1080), "vertical": (1080, 1920), "square": (1080, 1080)}


def parse_formats(spec: str) -> list[str]:
    names = list(FORMATS) if spec == "all" else [n.strip() for n in spec.split(",") if n.strip()]
    bad = [n for n in names if n not in FORMATS]
    if bad or not names:
        raise SystemExit(f"unknown format {', '.join(bad) or repr(spec)}; use all or a comma list of {', '.join(FORMATS)}")
    return list(dict.fromkeys(names))


COMPOSITION_TAG = re.compile(r"<[^<>]*data-composition-id[^<>]*>")


def attr(k: str) -> str:
    """data-<k>="..." in either quote style; group 2 is the value."""
    return rf"""data-{k}=(["'])(.*?)\1"""


def size_copy(composition: Path, copy: Path, fmt: str) -> None:
    """Copy the composition; in the copy, every composition element (root, sub-composition hosts and the roots in
    compositions/*.html) sized like the root gets the format's size, and the root gets data-format.
    Elements at another size (an inset) keep theirs. The original is untouched."""
    index = composition / "index.html"
    if not index.is_file():
        raise SystemExit(f"no index.html in {composition}; pass the composition folder")
    m = COMPOSITION_TAG.search(index.read_text(encoding="utf-8"))
    sizes = [re.search(attr(k), m.group(0)) if m else None for k in ("width", "height")]
    if not all(sizes):
        raise SystemExit(f"{index}: the root element (data-composition-id) needs data-width and data-height to render several formats")
    landscape = tuple(s.group(2) for s in sizes)
    width, height = FORMATS[fmt]

    def resize(tag: str) -> str:
        own = [re.search(attr(k), tag) for k in ("width", "height")]
        if not all(own) or tuple(s.group(2) for s in own) != landscape:
            return tag
        return re.sub(attr("height"), f'data-height="{height}"', re.sub(attr("width"), f'data-width="{width}"', tag))

    shutil.rmtree(copy, ignore_errors=True)
    shutil.copytree(composition, copy)
    for page in [copy / "index.html", *sorted((copy / "compositions").glob("*.html"))]:
        html = page.read_text(encoding="utf-8")
        if page == copy / "index.html":
            root = COMPOSITION_TAG.search(html).group(0)
            new = re.sub(r"\s*" + attr("format"), "", root)
            new = new[:-1].rstrip("/").rstrip() + f' data-format="{fmt}"' + ("/>" if root.endswith("/>") else ">")
            html = html.replace(root, new, 1)
        page.write_text(COMPOSITION_TAG.sub(lambda t: resize(t.group(0)), html), encoding="utf-8")


def render_formats(
    composition: Path,
    output: Path,
    work: Path,
    formats: list[str],
    fast_capture: bool = True,
    extra: list[str] | None = None,
    run: Callable[[list[str]], tuple[int, str]] = run_cli,
    after: Callable[[Path, Path], None] | None = None,
) -> list[Path]:
    """One render per format, each to <stem>-<format>; `after(mp4, work)` (loudnorm) runs as each one finishes,
    so a later failed format never leaves the earlier ones un-normalised. Failures are named at the end."""
    done: list[Path] = []
    failed: list[str] = []
    for f in formats:
        # Always suffixed, so re-running one failed format of an "all" run lands next to the others.
        out = output.with_name(f"{output.stem}-{f}{output.suffix}")
        try:
            copy = work / "formats" / f
            size_copy(composition, copy, f)
            render(copy, out, work / f, fast_capture=fast_capture, extra=extra, run=run)
            if after:
                after(out, work / f)
            done.append(out)
        except SystemExit as e:
            failed.append(f); why = str(e).splitlines()[0]
            print(f"format {f} failed: {e}", file=sys.stderr)
    if failed:
        raise SystemExit(f"render failed for format {', '.join(failed)} ({why}); kept: {', '.join(map(str, done)) or 'none'}")
    return done


def parse(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    # Everything after "--" goes to hyperframes render; argparse.REMAINDER would also swallow --work.
    ours, extra = (argv[: argv.index("--")], argv[argv.index("--") + 1 :]) if "--" in argv else (argv, [])
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("composition", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--work", type=Path, required=True, help="folder for render.log")
    p.add_argument("--format", default=None, help="all, or a comma list of landscape,vertical,square; several formats write <name>-<format>.mp4")
    p.add_argument("--prepare-only", action="store_true", help="with --format: write the per-format copies in <work>/formats/ and stop, for preview stills")
    p.add_argument("--no-fast-capture", action="store_true")
    p.add_argument("--no-loudnorm", action="store_true", help="skip loudness normalisation")
    return p.parse_args(ours), extra


def main() -> None:
    a, extra = parse(sys.argv[1:])
    if a.prepare_only:
        if a.format is None:
            raise SystemExit("--prepare-only needs --format")
        for f in parse_formats(a.format):
            size_copy(a.composition, a.work / "formats" / f, f)
            print(f"prepared {a.work / 'formats' / f}")
        return
    if a.format is None:  # today's behaviour: the composition's own size, no format flags
        render(a.composition, a.output, a.work, fast_capture=not a.no_fast_capture, extra=extra)
        outs = [(a.output, a.work)]
    else:
        # Each format is normalised as it finishes; a failed format exits here and the others stay done.
        render_formats(a.composition, a.output, a.work, parse_formats(a.format), fast_capture=not a.no_fast_capture,
                       extra=extra, after=None if a.no_loudnorm else normalize_loudness)
        return
    if not a.no_loudnorm:
        normalize_loudness(a.output, a.work)


if __name__ == "__main__":
    main()
