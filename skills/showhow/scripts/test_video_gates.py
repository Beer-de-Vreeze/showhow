"""Self-check for the video gates. Run:
  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/test_video_gates.py
The end-to-end part needs ffmpeg on PATH and is skipped without it.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from video_gates import blank_runs, last_caption_end, measure

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


def gates(video: Path, srt: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(HERE / "video_gates.py"), str(video), "--srt", str(srt)],
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


if __name__ == "__main__":
    units()
    end_to_end()
    print("ok")
