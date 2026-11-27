"""Self-check for the video gates. Run:
  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/test_video_gates.py
The end-to-end part needs ffmpeg on PATH and is skipped without it.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from video_gates import blank_runs, caption_problems, last_caption_end, measure

HERE = Path(__file__).parent


def units() -> None:
    f = 1 / 30
    busy, flat = 120, 2
    # 3 blank frames pass, 4 fail, a trailing run is still reported.
    assert blank_runs([(i * f, flat if 5 <= i < 8 else busy) for i in range(20)]) == []
    assert blank_runs([(i * f, flat if 5 <= i < 9 else busy) for i in range(20)]) == [(5 * f, 4)]
    # A cut to black at the very end may run 15 frames; 16 fail.
    assert blank_runs([(i * f, flat if i >= 15 else busy) for i in range(30)]) == []
    assert blank_runs([(i * f, flat if i >= 14 else busy) for i in range(30)]) == [(14 * f, 16)]
    # The same 15 frames mid-video still fail.
    assert blank_runs([(i * f, flat if 5 <= i < 20 else busy) for i in range(30)]) == [(5 * f, 15)]

    with tempfile.TemporaryDirectory() as d:
        bad = Path(d) / "c.srt"
        bad.write_text("no cues here\n", encoding="utf-8")
        try:
            last_caption_end(bad)
        except SystemExit as e:
            assert "no cue times" in str(e), e
        else:
            raise AssertionError("expected SystemExit for an srt without cues")


def cue(text: str, end: str = "00:00:04,000") -> str:
    return f"1\n00:00:00,000 --> {end}\n{text}\n"


def caption_units() -> None:
    # BBC limit of 37 characters per line: 37 passes, 38 fails.
    assert caption_problems(cue("x" * 37), False) == []
    assert any("38 characters" in p for p in caption_problems(cue("x" * 38), False))
    # 3 lines fail in landscape, pass with --vertical; 4 fail either way.
    three = cue("one two\nthree four\nfive six")
    assert any("3 lines" in p for p in caption_problems(three, False))
    assert caption_problems(three, True) == []
    assert caption_problems(cue("a\nb\nc\nd"), True) != []
    # Worked example: 5 words need 5 x 0.3 = 1.5s, so 1.2s fails and 1.5s passes.
    five = "one two three four five"
    assert any("1.2s" in p for p in caption_problems(cue(five, "00:00:01,200"), False))
    assert caption_problems(cue(five, "00:00:01,500"), False) == []


def gates(video: Path, srt: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(HERE / "video_gates.py"), str(video), "--srt", str(srt), *extra],
                          capture_output=True, text=True)


def end_to_end() -> None:
    if not shutil.which("ffmpeg"):
        print("skipped end-to-end: no ffmpeg on PATH")
        return
    with tempfile.TemporaryDirectory() as d:
        video, srt = Path(d) / "v.mp4", Path(d) / "captions.srt"
        # 1s moving, 0.3s black (9 frames), 1s moving, then the last frame held for 3s: 5.3s in all.
        graph = (
            "testsrc2=s=320x180:r=30:d=1[a];color=black:s=320x180:r=30:d=0.3[b];"
            "testsrc2=s=320x180:r=30:d=1[c];[a][b][c]concat=n=3,tpad=stop_mode=clone:stop_duration=3[v]"
        )
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-filter_complex", graph, "-map", "[v]",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(video)], check=True)

        frames, duration = measure(video)
        runs = blank_runs(frames)
        assert len(runs) == 1 and abs(runs[0][0] - 1.0) < 0.05 and runs[0][1] == 9, runs
        assert abs(duration - 5.3) < 0.05, duration

        # Last caption ends at 3.0s: a 2.3s tail fails without credits, passes with them.
        srt.write_text("1\n00:00:00,000 --> 00:00:03,000\nHello\n", encoding="utf-8")
        assert last_caption_end(srt) == 3.0
        cli = gates(video, srt)
        assert cli.returncode == 1 and "G-blank FAIL" in cli.stdout and "G-end FAIL" in cli.stdout, cli.stdout
        (Path(d) / "credits.txt").write_text("Music: test\n", encoding="utf-8")
        cli = gates(video, srt)
        assert "G-end PASS:" in cli.stdout and "credits.txt found" in cli.stdout, cli.stdout
        # Last caption ends 0.1s before the video: passes with a note.
        srt.write_text("1\n00:00:00,000 --> 00:00:05,200\nHello\n", encoding="utf-8")
        assert "G-end PASS (note)" in gates(video, srt).stdout

        # G-captions through the CLI: a 38-character line fails; 3 lines fail unless --vertical.
        srt.write_text(cue("x" * 38, "00:00:05,200"), encoding="utf-8")
        cli = gates(video, srt)
        assert cli.returncode == 1 and "G-captions FAIL" in cli.stdout, cli.stdout
        srt.write_text(cue("one two\nthree four\nfive six", "00:00:05,200"), encoding="utf-8")
        assert "G-captions FAIL" in gates(video, srt).stdout
        assert "G-captions PASS" in gates(video, srt, "--vertical").stdout


if __name__ == "__main__":
    units()
    caption_units()
    end_to_end()
    print("ok")
