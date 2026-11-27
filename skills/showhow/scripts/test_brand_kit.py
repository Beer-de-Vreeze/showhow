"""Self-check for brand_kit.py against the fictional Northwind kit. Run:
  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/test_brand_kit.py
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = HERE / "fixtures" / "brand-kit"


def check(kit: Path) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(HERE / "brand_kit.py"), "check", str(kit)], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def broken(tmp: Path, mutate) -> tuple[int, str]:
    kit = tmp / "kit"
    shutil.copytree(KIT, kit)
    mutate(kit)
    return check(kit)


def main() -> None:
    code, out = check(KIT)
    assert code == 0, f"fixture kit must pass:\n{out}"
    assert "PASS" in out, out

    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)

        code, out = broken(tmp / "a", lambda k: (k / "FRAME.md").unlink())
        assert code == 1 and "FRAME.md" in out, f"missing FRAME.md: {code} {out}"

        code, out = broken(tmp / "b", lambda k: (k / "fonts" / "Inter-400.woff2").unlink())
        assert code == 1 and "Inter-400.woff2" in out, f"missing font: {code} {out}"

        code, out = broken(tmp / "c", lambda k: (k / "logo.svg").unlink())
        assert code == 1 and "logo" in out, f"missing logo: {code} {out}"

        def bad_accent(k: Path) -> None:
            f = k / "FRAME.md"
            f.write_text(f.read_text(encoding="utf-8").replace('"#B5651D"', '"not-a-colour"'), encoding="utf-8")

        code, out = broken(tmp / "d", bad_accent)
        assert code == 1 and "accent" in out, f"bad accent: {code} {out}"

        # muted is optional (stage.py falls back to ink), so kits saved before it existed still pass.
        def no_muted(k: Path) -> None:
            f = k / "FRAME.md"
            f.write_text(f.read_text(encoding="utf-8").replace('  muted: "#4A5B6A"\n', ""), encoding="utf-8")

        code, out = broken(tmp / "m", no_muted)
        assert code == 0, f"a kit without muted must pass: {code} {out}"

        # A kit stage.py would reject fails here too: no title or label fontFamily in typography.
        def no_title(k: Path) -> None:
            f = k / "FRAME.md"
            f.write_text("\n".join(ln for ln in f.read_text(encoding="utf-8").splitlines() if "fontFamily" not in ln) + "\n", encoding="utf-8")

        code, out = broken(tmp / "t", no_title)
        assert code == 1 and "title" in out and "label" in out, f"no typography: {code} {out}"

        # A third-party kit's paths stay inside the kit: a relative escape or an absolute path to a file that
        # exists elsewhere fails, even though the file is there.
        def escape(k: Path) -> None:
            (k.parent / "secret.txt").write_text("x", encoding="utf-8")
            f = k / "FRAME.md"
            text = f.read_text(encoding="utf-8").replace("fonts/Inter-400.woff2", "../secret.txt")
            f.write_text(text.replace("logo: logo.svg", f"logo: {(k.parent / 'secret.txt').as_posix()}"), encoding="utf-8")

        code, out = broken(tmp / "e", escape)
        assert code == 1 and out.count("outside the kit") == 2, f"escaping paths: {code} {out}"

        # Colours: only what both PIL (bake_highlights) and THREE.Color (scene3d) parse; comma rgb() and hsl() pass.
        def comma(k: Path) -> None:
            f = k / "FRAME.md"
            f.write_text(f.read_text(encoding="utf-8").replace('"#B5651D"', '"hsl(28, 72%, 41%)"').replace('"#4A5B6A"', '"rgb(74, 91, 106)"'), encoding="utf-8")

        code, out = broken(tmp / "f", comma)
        assert code == 0, f"comma colours: {code} {out}"
        # oklch(), a deg hue, space-separated rgb() and 8-digit hex crash bake_highlights or whiten scene3d: they fail.
        for i, colour in enumerate(("oklch(0.6 0.1 200)", "hsl(28deg 70% 51%)", "rgb(181 101 29)", "#B5651DFF")):
            def modern(k: Path, colour=colour) -> None:
                f = k / "FRAME.md"
                f.write_text(f.read_text(encoding="utf-8").replace('"#B5651D"', f'"{colour}"'), encoding="utf-8")

            code, out = broken(tmp / f"g{i}", modern)
            assert code == 1 and "accent" in out, f"{colour}: {code} {out}"
    print("ok")


if __name__ == "__main__":
    main()
