"""Self-check for the render wrapper. Run:
  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/test_render.py
"""

import os
import re
import sys
import tempfile
from pathlib import Path

from render import normalize_loudness, parse, parse_formats, render, render_formats

MEASUREMENT = """[Parsed_loudnorm_0 @ 0x1]
{
	"input_i" : "-23.40",
	"input_tp" : "-4.10",
	"input_lra" : "6.20",
	"input_thresh" : "-33.90",
	"output_i" : "-16.00",
	"target_offset" : "0.30"
}
"""


class FakeFfmpeg:
    """Stands in for ffprobe and ffmpeg: answers each by its role and writes the normalised file."""

    def __init__(self, probe: str = "1\n", measure: tuple[int, str] = (0, MEASUREMENT), write: tuple[int, bytes] = (0, b"norm")):
        self.probe, self.measure, self.write = probe, measure, write
        self.calls: list[list[str]] = []

    def __call__(self, cmd: list[str]) -> tuple[int, str]:
        self.calls.append(cmd)
        if "-select_streams" in cmd:
            return 0, self.probe
        if "null" in cmd:
            return self.measure
        code, data = self.write
        if data:
            Path(cmd[-1]).write_bytes(data)
        return code, "done\n"


class FakeRunner:
    """Stands in for the HyperFrames CLI: records each command and writes `size` bytes to the mp4."""

    def __init__(self, out: Path, code: int, size: int | None, text: str = "frame 1/90\nencode done\n"):
        self.out, self.code, self.size, self.text = out, code, size, text
        self.calls: list[list[str]] = []

    def __call__(self, cmd: list[str]) -> tuple[int, str]:
        self.calls.append(cmd)
        if self.size is not None:
            self.out.write_bytes(b"x" * self.size)
        return self.code, self.text


ROOT_HTML = '<html><body><div id="root" data-composition-id="main" data-start="0" data-duration="1" data-width="1920" data-height="1080"></div></body></html>'


class PerOutputRunner:
    """Fake CLI for several formats: writes the mp4 named by --output unless its name contains an entry of `fail`."""

    def __init__(self, fail: tuple[str, ...] = ()):
        self.fail, self.calls, self.roots = fail, [], []

    def __call__(self, cmd: list[str]) -> tuple[int, str]:
        self.calls.append(cmd)
        out = Path(cmd[cmd.index("--output") + 1])
        root = re.search(r"<[^>]*data-composition-id[^>]*>", (Path(cmd[3]) / "index.html").read_text(encoding="utf-8")).group(0)
        self.roots.append(tuple(re.search(rf'data-{k}="[^"]*"', root).group(0) for k in ("width", "height", "format")))
        if any(f in out.name for f in self.fail):
            return 1, f"Error: chrome crashed on {out.name}\n"
        out.write_bytes(b"x" * 32)
        return 0, "encode done\n"


def expect_exit(fn, text: str) -> None:
    try:
        fn()
    except SystemExit as e:
        assert e.code != 0 and text in str(e), e
        return
    raise AssertionError(f"expected a non-zero exit containing {text!r}")


def main() -> None:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        comp, work, out = root / "composition", root / "work", root / "video.mp4"
        comp.mkdir()

        # missing_composition_fails_fast: no index.html means no render call and no retry.
        never = FakeRunner(out, 0, 1024)
        expect_exit(lambda: render(comp, out, work, run=never), "no index.html")
        assert never.calls == [], never.calls
        (comp / "index.html").write_text("<html></html>", encoding="utf-8")

        # retry_then_success: a first failure is retried once and the second attempt counts.
        class Flaky(FakeRunner):
            def __call__(self, cmd):
                self.calls.append(cmd)
                if len(self.calls) == 1:
                    return 1, "Error: browser closed\n"
                self.out.write_bytes(b"x" * 64)
                return 0, "encode done\n"
        flaky = Flaky(out, 0, None)
        render(comp, out, work, run=flaky)
        assert len(flaky.calls) == 2 and out.stat().st_size == 64, flaky.calls
        assert "browser closed" in (work / "render.log").read_text(encoding="utf-8")
        out.unlink()

        # writes_mp4: one call, returns, log keeps the CLI output.
        ok = FakeRunner(out, 0, 1024)
        render(comp, out, work, run=ok)
        assert len(ok.calls) == 1, ok.calls
        assert "encode done" in (work / "render.log").read_text(encoding="utf-8")
        assert "--quiet" not in ok.calls[0]
        assert "--experimental-fast-capture=false" not in ok.calls[0]
        out.unlink()

        # missing_mp4_retries_then_fails: retried once, then exits with the log tail.
        missing = FakeRunner(out, 1, None, "Error: chrome crashed\n")
        expect_exit(lambda: render(comp, out, work, run=missing), "chrome crashed")
        assert len(missing.calls) == 2, missing.calls

        # empty_mp4_counts_as_missing: exit 0 with a 0-byte file is still a failure.
        empty = FakeRunner(out, 0, 0)
        expect_exit(lambda: render(comp, out, work, run=empty), "no mp4")
        assert len(empty.calls) == 2, empty.calls
        out.unlink()

        # nonzero_exit_with_mp4_is_failure: a crashed render can leave a truncated file.
        crashed = FakeRunner(out, 4, 512, "Error: worker exited\n")
        expect_exit(lambda: render(comp, out, work, run=crashed), "worker exited")
        assert len(crashed.calls) == 2, crashed.calls
        out.unlink()

        # stale_mp4_is_not_success: an mp4 from an earlier run doesn't prove this render.
        out.write_bytes(b"old" * 100)
        os.utime(out, (0, 0))
        stale = FakeRunner(out, 1, None, "Error: out of memory\n")
        expect_exit(lambda: render(comp, out, work, run=stale), "out of memory")
        assert out.read_bytes() == b"old" * 100, "a failed render must not delete the old video"
        out.unlink()

        # fast_capture_off: the flag reaches the command.
        slow = FakeRunner(out, 0, 1024)
        render(comp, out, work, fast_capture=False, run=slow)
        assert "--experimental-fast-capture=false" in slow.calls[0], slow.calls[0]
        out.unlink()

        # extra_flags_pass_through: --docker and --quality reach the CLI unchanged.
        extra = FakeRunner(out, 0, 1024)
        render(comp, out, work, extra=["--docker", "--quality", "high"], run=extra)
        assert extra.calls[0][-3:] == ["--docker", "--quality", "high"], extra.calls[0]

        # multi_format_two_renders: landscape,vertical -> two runs on two copies sized 1920x1080 and 1080x1920.
        fcomp = root / "fcomp"
        fcomp.mkdir()
        original = ROOT_HTML.encode()
        (fcomp / "index.html").write_bytes(original)
        base = root / "multi" / "video.mp4"
        base.parent.mkdir()
        two = PerOutputRunner()
        render_formats(fcomp, base, root / "mwork", parse_formats("landscape,vertical"), run=two)
        assert len(two.calls) == 2, two.calls
        assert [Path(c[3]) for c in two.calls] == [root / "mwork" / "formats" / "landscape", root / "mwork" / "formats" / "vertical"]
        assert two.roots[0] == ('data-width="1920"', 'data-height="1080"', 'data-format="landscape"'), two.roots
        assert two.roots[1] == ('data-width="1080"', 'data-height="1920"', 'data-format="vertical"'), two.roots
        assert (fcomp / "index.html").read_bytes() == original, "the user's composition must not be edited"
        assert sorted(p.name for p in base.parent.iterdir()) == ["video-landscape.mp4", "video-vertical.mp4"]

        # single_format_is_named: --format square alone still writes <video-name>-square.mp4 and logs to work/square,
        # so re-running one failed format of an "all" run lands next to the others.
        one_dir = root / "single"
        one_dir.mkdir()
        one = PerOutputRunner()
        render_formats(fcomp, one_dir / "video.mp4", root / "swork", parse_formats("square"), run=one)
        assert [p.name for p in one_dir.iterdir()] == ["video-square.mp4"] and len(one.calls) == 1
        assert (root / "swork" / "square" / "render.log").is_file()
        assert one.roots[0] == ('data-width="1080"', 'data-height="1080"', 'data-format="square"'), one.roots

        # single_quotes_and_sub_compositions_resize: a single-quoted root, a host div and a sub-composition file at the
        # root's size all become 1080x1920 in the vertical copy; an inset at its own size keeps it.
        sub = root / "sub"
        (sub / "compositions").mkdir(parents=True)
        (sub / "index.html").write_text(
            "<div id='root' data-composition-id='main' data-width='1920' data-height='1080'>\n"
            '  <div id="host"\n    data-composition-id="demo" data-composition-src="compositions/demo.html"\n    data-width="1920" data-height="1080"></div>\n'
            '  <div id="inset" data-composition-id="inset" data-width="640" data-height="360"></div></div>', encoding="utf-8")
        (sub / "compositions" / "demo.html").write_text('<template><div id="root" data-composition-id="demo" data-width="1920" data-height="1080"></div></template>', encoding="utf-8")
        render_formats(sub, root / "sub.mp4", root / "subwork", ["vertical"], run=PerOutputRunner())
        vcopy = root / "subwork" / "formats" / "vertical"
        tags = re.findall(r"<[^<>]*data-composition-id[^<>]*>", (vcopy / "index.html").read_text(encoding="utf-8") + (vcopy / "compositions" / "demo.html").read_text(encoding="utf-8"))
        sizes = [tuple(re.search(rf"data-{k}=[\"']([^\"']*)", t).group(1) for k in ("width", "height")) for t in tags]
        assert sizes == [("1080", "1920"), ("1080", "1920"), ("640", "360"), ("1080", "1920")], sizes
        assert 'data-format="vertical"' in tags[0] and "data-format" not in tags[1], tags

        # root_without_size_fails: nothing to rewrite means a clear error and no render.
        nosize = root / "nosize"
        nosize.mkdir()
        (nosize / "index.html").write_text('<div data-composition-id="main"></div>', encoding="utf-8")
        never2 = PerOutputRunner()
        expect_exit(lambda: render_formats(nosize, root / "n.mp4", root / "nwork", ["vertical"], run=never2), "data-width")
        assert never2.calls == []

        # failed_format_keeps_others: vertical fails -> non-zero exit naming vertical, landscape file kept.
        fdir = root / "fail"
        fdir.mkdir()
        bad_run = PerOutputRunner(fail=("vertical",))
        normalised: list[tuple[str, Path]] = []
        expect_exit(lambda: render_formats(fcomp, fdir / "video.mp4", root / "fwork", parse_formats("landscape,vertical"), run=bad_run,
                                           after=lambda o, w: normalised.append((o.name, w))), "vertical")
        assert (fdir / "video-landscape.mp4").is_file() and not (fdir / "video-vertical.mp4").exists()
        # format_normalised_as_it_finishes: the kept landscape file is loudness-normalised even though vertical failed.
        assert normalised == [("video-landscape.mp4", root / "fwork" / "landscape")], normalised
        assert "chrome crashed" in (root / "fwork" / "vertical" / "render.log").read_text(encoding="utf-8")
        # each_failure_keeps_its_reason: two failed formats are each named with their own cause.
        both = PerOutputRunner(fail=("landscape", "vertical"))
        try:
            render_formats(fcomp, fdir / "two.mp4", root / "f2work", parse_formats("landscape,vertical"), run=both)
            raise AssertionError("expected an exit")
        except SystemExit as e:
            assert "two-landscape.mp4" in str(e) and "two-vertical.mp4" in str(e), e

        # copy_error_is_named: a format copy that can't be rebuilt (here a file in its place) fails that format with
        # a message naming it; the next format still renders.
        cwork = root / "cwork"
        (cwork / "formats").mkdir(parents=True)
        (cwork / "formats" / "landscape").write_text("locked", encoding="utf-8")
        expect_exit(lambda: render_formats(fcomp, fdir / "copy.mp4", cwork, parse_formats("landscape,vertical"), run=PerOutputRunner()), "landscape")
        assert (fdir / "copy-vertical.mp4").is_file()

        # work_inside_composition_refused: copying the composition into its own work folder would recurse.
        expect_exit(lambda: render_formats(fcomp, fdir / "in.mp4", fcomp / "work", ["vertical"], run=PerOutputRunner()), "inside")
        assert not (fcomp / "work").exists()

        assert parse_formats("all") == ["landscape", "vertical", "square"]
        expect_exit(lambda: parse_formats("wide"), "unknown format")

        # loudnorm_two_pass: measure, then normalise with the measured values; the mp4 is replaced.
        out.write_bytes(b"rendered")
        ff = FakeFfmpeg()
        normalize_loudness(out, work, run=ff)
        assert len(ff.calls) == 3, ff.calls
        af = ff.calls[2][ff.calls[2].index("-af") + 1]
        assert "I=-16:TP=-1" in af and "measured_I=-23.4" in af and "offset=0.3" in af, af
        assert ff.calls[2][ff.calls[2].index("-c:v") + 1] == "copy", ff.calls[2]
        assert out.read_bytes() == b"norm"
        assert not list(root.glob("*.loudnorm.mp4")), "temp file left behind"

        # loudnorm_bad_measurement_keeps_mp4: unparsable output exits non-zero, file untouched.
        out.write_bytes(b"rendered")
        bad = FakeFfmpeg(measure=(0, "no json here\n"))
        expect_exit(lambda: normalize_loudness(out, work, run=bad), "unchanged")
        assert out.read_bytes() == b"rendered" and len(bad.calls) == 2

        # loudnorm_measure_exit_keeps_mp4: a failed measuring pass is a failure even with JSON.
        failed = FakeFfmpeg(measure=(1, MEASUREMENT))
        expect_exit(lambda: normalize_loudness(out, work, run=failed), "measurement")
        assert out.read_bytes() == b"rendered" and len(failed.calls) == 2, failed.calls

        # loudnorm_silent_track_skips: an audio stream that is all silence measures -inf; skip, don't fail.
        hush = FakeFfmpeg(measure=(0, MEASUREMENT.replace('"-23.40"', '"-inf"')))
        normalize_loudness(out, work, run=hush)
        assert out.read_bytes() == b"rendered" and len(hush.calls) == 2, hush.calls

        # loudnorm_write_fails_keeps_mp4: a failed second pass leaves the render and no temp file.
        broken = FakeFfmpeg(write=(1, b"half"))
        expect_exit(lambda: normalize_loudness(out, work, run=broken), "normalisation")
        assert out.read_bytes() == b"rendered"
        assert not list(root.glob("*.loudnorm.mp4")), "temp file left behind"

        # loudnorm_silent_video_skips: no audio stream, no ffmpeg pass.
        silent = FakeFfmpeg(probe="")
        normalize_loudness(out, work, run=silent)
        assert len(silent.calls) == 1 and out.read_bytes() == b"rendered"

    # cli_args: --work after the positionals and flags after -- both parse.
    a, extra = parse(["comp", "out.mp4", "--work", "w", "--no-fast-capture", "--", "--docker"])
    assert (a.work, a.no_fast_capture, extra) == (Path("w"), True, ["--docker"]), (a, extra)
    a, extra = parse(["comp", "out.mp4", "--work", "w"])
    assert extra == [] and not a.no_fast_capture and not a.no_loudnorm, (a, extra)
    a, _ = parse(["comp", "out.mp4", "--work", "w", "--no-loudnorm"])
    assert a.no_loudnorm, a

    # main_no_loudnorm: the CLI renders and skips normalisation; without the flag it normalises.
    import render as mod

    seen: list[str] = []
    real = (mod.render, mod.normalize_loudness, sys.argv)
    mod.render = lambda *a, **k: seen.append("render")
    mod.normalize_loudness = lambda *a, **k: seen.append("loudnorm")
    try:
        sys.argv = ["render.py", "comp", "out.mp4", "--work", "w", "--no-loudnorm"]
        mod.main()
        assert seen == ["render"], seen
        sys.argv = ["render.py", "comp", "out.mp4", "--work", "w"]
        mod.main()
        assert seen == ["render", "render", "loudnorm"], seen
    finally:
        mod.render, mod.normalize_loudness, sys.argv = real

    # prepare_only: --prepare-only writes the per-format copies and never renders or normalises.
    with tempfile.TemporaryDirectory() as t:
        pc = Path(t) / "comp"; pc.mkdir(); (pc / "index.html").write_text(ROOT_HTML, encoding="utf-8")
        pw = Path(t) / "work"
        seen.clear()
        mod.render = lambda *a, **k: seen.append("render")
        mod.normalize_loudness = lambda *a, **k: seen.append("loudnorm")
        try:
            sys.argv = ["render.py", str(pc), "o.mp4", "--work", str(pw), "--format", "landscape,vertical", "--prepare-only"]
            mod.main()
        finally:
            mod.render, mod.normalize_loudness, sys.argv = real
        assert seen == [], seen
        assert 'data-format="vertical"' in (pw / "formats" / "vertical" / "index.html").read_text(encoding="utf-8")
        assert (pw / "formats" / "landscape" / "index.html").is_file()

    print("render self-check passed")


if __name__ == "__main__":
    main()
