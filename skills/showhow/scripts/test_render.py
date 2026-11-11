"""Self-check for the render wrapper. Run:
  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/test_render.py
"""

import os
import tempfile
from pathlib import Path

from render import normalize_loudness, parse, render

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
        assert out.read_bytes() == b"rendered"

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

    print("render self-check passed")


if __name__ == "__main__":
    main()
