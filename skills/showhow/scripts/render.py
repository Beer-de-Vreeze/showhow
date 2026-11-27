#!/usr/bin/env python3
"""Render a HyperFrames composition to mp4, loudly.

A `--quiet` render can exit non-zero with no message and no file, so this never
passes it: it logs everything to <work>/render.log, succeeds only when the CLI
exits 0 and this run wrote a non-empty mp4, retries once, and prints the log
tail on failure.

  uv run --project <skill-dir>/scripts <skill-dir>/scripts/render.py \
      <output-dir>/composition <output-dir>/<video-name>.mp4 --work <output-dir>/work --plan <output-dir>/showhow-plan.md \
      [--stills] [--format <names>] [--poster-at <s>] [--no-fast-capture] [--no-loudnorm] [-- --docker --quality high]

--plan: the formats come from the plan (parse_plan in plan_gates.py; a plan that does not parse renders
nothing). One format renders the composition as is to <video-name>.mp4 (its own size; log in <work>/render.log).
Several formats render one file each, <video-name>-<format>.mp4 (landscape 1920x1080, vertical
1080x1920, square 1080x1080). Each of those renders a copy of the
composition in <work>/formats/<format>/ whose root gets data-format and whose composition elements sized
like the root (root, sub-composition hosts, compositions/*.html roots) get the format's data-width and
data-height; the original is never edited, and CSS keys layout off [data-format="vertical"]. The root needs
data-width and data-height. A failing format is named and exits non-zero; formats that rendered are kept,
each finished (loudnorm, poster) as it rendered, with its log in <work>/<format>/render.log.

Settled moment of a scene: 0.1s after its last caption cue ends (captions.srt next to the plan), at most
0.1s before the scene ends; 0.3s before the end for a scene without a cue.

--stills (with --plan): write the format copies and one still per scene at its settled moment to
<work>/preview/<format>/scene-NN.png, then stop; no render. For the explainer's Stop 2.

Poster: after loudnorm each mp4 gets <same name>.jpg, its own frame at the settled moment of the first scene
that holds without voice (no caption on screen; scene 1's, with a warning, when every scene talks to its end),
baked in as frame 0. --poster-at <s> picks another moment; when every mp4 is newer than every composition file,
it only re-takes and re-bakes the poster, with no render. Without --plan or --poster-at there is no poster (it says so).

--format: overrides the plan's formats, renders resized copies and always suffixes the name, so re-running one
failed format lands next to the others. Without --plan and --format the composition renders as is.

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

from plan_gates import parse_plan

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

    if copy.resolve().is_relative_to(composition.resolve()):
        raise SystemExit(f"--work {copy.parent.parent} is inside the composition {composition}; copying it would recurse. Put work next to the composition.")
    try:
        # A stale copy that can't be removed (a preview or Explorer holding a file on Windows) fails this format by name.
        if copy.exists():
            shutil.rmtree(copy)
        shutil.copytree(composition, copy)
    except OSError as e:
        raise SystemExit(f"could not rebuild the {fmt} copy at {copy}: {e}. Close anything using it and rerun.")
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
    """One render per format, each to <stem>-<format>; `after(mp4, work)` (loudnorm, poster) runs as each one finishes,
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
            failed.append(f"{f} ({str(e).splitlines()[0]})")
            print(f"format {f} failed: {e}", file=sys.stderr)
    if failed:
        raise SystemExit(f"render failed for format {'; '.join(failed)}; kept: {', '.join(map(str, done)) or 'none'}")
    return done


CUE = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)")


def settled_times(scenes: list[dict], srt_text: str) -> list[float]:
    """Each scene's settled moment: 0.1s after its last caption cue ends (a cue belongs to the scene it starts in),
    at most 0.1s before the scene ends; 0.3s before the end for a scene without a cue."""
    cues = [(a[0] * 3600 + a[1] * 60 + a[2] + a[3] / 1000, a[4] * 3600 + a[5] * 60 + a[6] + a[7] / 1000)
            for a in ([int(x) for x in m] for m in CUE.findall(srt_text))]
    times = []
    for s in scenes:
        start, end = s["start"], s["start"] + s["secs"]
        ends = [b for a, b in cues if start <= a < end]
        times.append(round(max(start, min(max(ends) + 0.1, end - 0.1) if ends else end - 0.3), 2))
    return times


CLEAR = 0.3  # a poster moment this far before its scene's end has no caption and no transition yet


def poster_time(scenes: list[dict], srt_text: str) -> tuple[float, bool]:
    """The settled moment of the first scene that holds without voice (its last cue ends by CLEAR + 0.1s before the
    scene does, or it has no cue), and True; scene 1's settled moment and False when every scene talks to its end."""
    times = settled_times(scenes, srt_text)
    for s, t in zip(scenes, times):
        if t <= s["start"] + s["secs"] - CLEAR + 1e-6:
            return t, True
    return times[0], False


def rendered_after(composition: Path, mp4s: list[Path]) -> bool:
    """Every mp4 exists and is newer than every file of the composition, so moving the poster needs no new render."""
    if not all(p.is_file() for p in mp4s):
        return False
    newest = max((p.stat().st_mtime for p in composition.rglob("*") if p.is_file()), default=0)
    return min(p.stat().st_mtime for p in mp4s) > newest


def write_stills(copy: Path, times: list[float], dest: Path, run: Callable[[list[str]], tuple[int, str]] = run_cli,
                 extra: list[str] | None = None) -> None:
    """One snapshot per time of the format copy, renamed in time order to dest/scene-NN.png; contact sheets removed.
    `extra` goes to the snapshot command (check_fixture.py passes --no-browser-gpu)."""
    if dest.exists():
        shutil.rmtree(dest)  # stale stills from an earlier plan would pass for this one
    cmd = [shutil.which("npx") or "npx", HYPERFRAMES, "snapshot", str(copy), "--no-end", "--describe", "false",
           "--at", ",".join(f"{t:g}" for t in times), "-o", str(dest), *(extra or [])]
    code, text = run(cmd)
    # The CLI numbers frames in --at order; sort by that number, since frame-10 sorts before frame-2 as text.
    frames = sorted(dest.glob("frame-*-at-*.png"), key=lambda p: int(p.name.split("-")[1])) if dest.is_dir() else []
    if code != 0 or len(frames) != len(times):
        tail = "\n".join(text.splitlines()[-TAIL_LINES:])
        raise SystemExit(f"snapshot of {copy} wrote {len(frames)} of {len(times)} stills (exit {code}):\n{tail}")
    for i, frame in enumerate(frames, 1):
        frame.replace(dest / f"scene-{i:02d}.png")
    for sheet in dest.glob("contact-sheet*.jpg"):
        sheet.unlink()
    print(f"stills: {len(frames)} in {dest}")


def bake_poster(output: Path, at: float, work: Path, run: Callable[[list[str]], tuple[int, str]] = run_cli) -> None:
    """<output>.jpg from the mp4's own frame at `at`, then baked in as frame 0 (players that show frame 0 before play).
    The bake copies the audio, so it runs after loudnorm; the mp4 is only replaced once the baked file exists."""
    ffmpeg, jpg, tmp = shutil.which("ffmpeg") or "ffmpeg", output.with_suffix(".jpg"), work / "poster.mp4"
    work.mkdir(parents=True, exist_ok=True)
    code, text = run([ffmpeg, "-y", "-hide_banner", "-ss", f"{at:g}", "-i", str(output), "-frames:v", "1", "-q:v", "2", str(jpg)])
    if code != 0 or not jpg.is_file():
        raise SystemExit(f"poster frame at {at:g}s failed for {output}:\n{text[-2000:]}")
    code, text = run([ffmpeg, "-y", "-hide_banner", "-i", str(output), "-i", str(jpg), "-filter_complex",
                      "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]", "-map", "[v]", "-map", "0:a?", "-c:v", "libx264",
                      "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(tmp)])
    if code != 0 or not tmp.is_file() or tmp.stat().st_size == 0:
        tmp.unlink(missing_ok=True)
        raise SystemExit(f"poster bake failed; {output} is unchanged:\n{text[-2000:]}")
    try:
        tmp.replace(output)
    except PermissionError:
        tmp.unlink(missing_ok=True)
        raise SystemExit(f"poster bake could not replace {output} (open in a player?); it is unchanged. Close it and rerun.")
    print(f"poster: {jpg} (frame at {at:g}s, baked as frame 0)")


def parse(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    # Everything after "--" goes to hyperframes render; argparse.REMAINDER would also swallow --work.
    ours, extra = (argv[: argv.index("--")], argv[argv.index("--") + 1 :]) if "--" in argv else (argv, [])
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("composition", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--work", type=Path, required=True, help="folder for render.log")
    p.add_argument("--plan", type=Path, help="showhow-plan.md: the formats to render and the scene times for stills and the poster")
    p.add_argument("--format", default=None, help="all, or a comma list of landscape,vertical,square; overrides the plan, always writes <name>-<format>.mp4")
    p.add_argument("--stills", action="store_true", help="with --plan: write the format copies and one still per scene to <work>/preview/<format>/scene-NN.png, then stop")
    p.add_argument("--poster-at", type=float, help="poster moment in seconds (default: scene 1's settled moment)")
    p.add_argument("--no-fast-capture", action="store_true")
    p.add_argument("--no-loudnorm", action="store_true", help="skip loudness normalisation")
    return p.parse_args(ours), extra


def main(argv: list[str] | None = None, run: Callable[[list[str]], tuple[int, str]] = run_cli) -> None:
    a, extra = parse(sys.argv[1:] if argv is None else argv)
    plan = parse_plan(a.plan.read_text(encoding="utf-8")) if a.plan else None
    if plan and plan["errors"]:
        raise SystemExit(f"{a.plan} does not parse (P-parse); fix it before rendering:\n" + "\n".join(plan["errors"]))
    if a.stills and not plan:
        raise SystemExit("--stills needs --plan: the scene times come from the plan")
    formats = parse_formats(a.format) if a.format else plan["formats"] if plan else None
    poster_at, times = a.poster_at, None
    if plan and (a.stills or poster_at is None):
        srt = a.plan.parent / "captions.srt"
        if not srt.is_file():
            raise SystemExit(f"no captions.srt next to {a.plan}: the settled moments come from it. Write it first (step-4-deliver.md), or pass --poster-at.")
        times = settled_times(plan["scenes"], srt.read_text(encoding="utf-8"))
        if not times:
            raise SystemExit(f"{a.plan} has no scenes to take stills or a poster from")
        if poster_at is None:
            poster_at, clear = poster_time(plan["scenes"], srt.read_text(encoding="utf-8"))
            if not clear:
                print(f"poster at {poster_at:g}s may show a caption: every scene is voiced to its end. Pass --poster-at, or make "
                      "a caption-hidden poster (step-4-deliver.md, \"Pick the poster frame\").")

    # One format from the plan (or no plan) renders the composition as is; --format always renders resized copies.
    as_is = a.format is None and (formats is None or len(formats) == 1)
    outs = {"": a.output} if as_is else {f: a.output.with_name(f"{a.output.stem}-{f}{a.output.suffix}") for f in formats}
    if poster_at is None:
        print(f"no poster: pass --plan (with captions.srt beside it) or --poster-at <s> to get {a.output.stem}.jpg and a baked frame 0")
    elif a.poster_at is not None and not a.stills and rendered_after(a.composition, list(outs.values())):
        print("the composition has not changed since the render: moving the poster only")
        for f, mp4 in outs.items():
            bake_poster(mp4, poster_at, a.work / f, run=run)
        return

    if a.stills:
        for f in formats:
            copy = a.work / "formats" / f
            size_copy(a.composition, copy, f)
            write_stills(copy, times, a.work / "preview" / f, run=run)
        return

    def finish(mp4: Path, work: Path) -> None:
        if not a.no_loudnorm:
            normalize_loudness(mp4, work, run=run)
        if poster_at is not None:
            bake_poster(mp4, poster_at, work, run=run)

    if as_is:  # the composition's own size
        render(a.composition, a.output, a.work, fast_capture=not a.no_fast_capture, extra=extra, run=run)
        finish(a.output, a.work)
    else:
        # Each format is finished (loudnorm, poster) as it renders; a failed format exits here and the others stay done.
        render_formats(a.composition, a.output, a.work, formats, fast_capture=not a.no_fast_capture, extra=extra, run=run, after=finish)


if __name__ == "__main__":
    main()
