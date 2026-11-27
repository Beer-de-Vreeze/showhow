"""Self-check for stage.py, offline: npm tarballs come from a fake cache folder. Run:
  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/test_stage.py
"""

import io
import re
import shutil
import tarfile
import tempfile
from pathlib import Path

import stage

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
PRESET = SKILL / "assets" / "frame-presets" / "showhow"
BRAND = HERE / "fixtures" / "brand-kit"
GSAP_FILES = ("gsap", "DrawSVGPlugin", "MorphSVGPlugin", "SplitText", "MotionPathPlugin")
HTML = '<!doctype html>\n<html>\n  <head>\n    <meta charset="utf-8" />\n  </head>\n  <body></body>\n</html>\n'


def tgz(path: Path, files: dict[str, str]) -> Path:
    with tarfile.open(path, "w:gz") as tar:
        for name, text in files.items():
            data = text.encode()
            info = tarfile.TarInfo(f"package/{name}")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return path


def fake_cache(root: Path):
    """A folder of npm-pack tarballs, and a fetch that only reads it (no network)."""
    root.mkdir(parents=True)
    tgz(root / "gsap.tgz", {f"dist/{n}.min.js": f"/*{n}*/" for n in GSAP_FILES})
    tgz(root / "three.tgz", {
        "LICENSE": "MIT",
        "build/three.module.js": "export {};",
        "build/three.core.js": "export {};",
        "examples/jsm/loaders/FontLoader.js": "export {};",
        "examples/fonts/helvetiker_bold.typeface.json": "{}",
        "examples/fonts/LICENSE": "MIT",
    })
    asked = []

    def fetch(spec: str) -> Path:
        asked.append(spec)
        return root / f"{spec.split('@')[0]}.tgz"

    return fetch, asked


def composition(root: Path) -> Path:
    root.mkdir(parents=True)
    (root / "index.html").write_text(HTML, encoding="utf-8")
    return root


def fails(fn, text: str) -> None:
    try:
        fn()
    except SystemExit as e:
        assert text in str(e), f"expected {text!r} in: {e}"
        return
    raise AssertionError(f"expected a failure naming {text!r}")


def shipped():
    """Files of the skill, not generated output (scripts/out) or the virtualenv."""
    return (p for p in SKILL.rglob("*") if p.is_file() and not {"out", ".venv", "node_modules"} & set(p.relative_to(SKILL).parts))


def main() -> None:
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        fetch, asked = fake_cache(tmp / "cache")

        # Stages every asset from the showhow preset, from the cache only.
        comp = composition(tmp / "comp")
        stage.stage(comp, PRESET, fetch=fetch)
        a = comp / "assets"
        for f in ("kit/showhow-kit.js", "kit/showhow-kit.css", "scene3d/scene3d.js", "scene3d/hero-number.js",
                  "scene3d/data/ne_110m_admin_0_countries.min.geojson", "three/build/three.module.js",
                  "three/build/three.core.js", "three/examples/jsm/loaders/FontLoader.js",
                  "three/examples/fonts/helvetiker_bold.typeface.json", "three/LICENSE",
                  "fonts/EBGaramond-700.woff2", "fonts/Inter-400.woff2", "fonts/OFL-inter.txt", "theme.css"):
            assert (a / f).is_file(), f"not staged: {f}"
        for n in GSAP_FILES:
            assert (a / "gsap" / f"{n}.min.js").is_file(), f"not staged: gsap/{n}.min.js"
        assert (comp / "frame.md").read_text(encoding="utf-8") == (PRESET / "FRAME.md").read_text(encoding="utf-8")
        assert sorted(asked) == ["gsap@3.14.2", "three@0.184.0"], asked

        # :root is the one token set, written from FRAME.md (values from assets/frame-presets/showhow/FRAME.md).
        css = (a / "theme.css").read_text(encoding="utf-8")
        for decl in ("--paper: #F3ECDD;", "--ink: #23201B;", "--accent: #0F6E6A;", "--muted: #5B5547;",
                     '--font-display: "EB Garamond", serif;', '--font-body: "Inter", sans-serif;'):
            assert decl in css, f"missing {decl} in theme.css:\n{css}"
        assert re.search(r'font-family: "EB Garamond"; src: url\("fonts/EBGaramond-700\.woff2"\); font-weight: 700;', css), css
        assert re.search(r'font-family: "Inter"; src: url\("fonts/Inter-400\.woff2"\); font-weight: 400;', css), css
        assert "OFL" not in css, "a licence file is not a font"

        # The head gets a local import map and the theme, once, even when staged twice.
        stage.stage(comp, PRESET, fetch=fetch)
        html = (comp / "index.html").read_text(encoding="utf-8")
        assert html.count(stage.BEGIN) == 1 and html.count(stage.END) == 1, html
        assert '"three": "./assets/three/build/three.module.js"' in html, html
        assert '"three/addons/": "./assets/three/examples/jsm/"' in html, html
        assert '<link rel="stylesheet" href="assets/theme.css" />' in html, html
        assert "cdn" not in html.lower() and "http" not in html, html
        assert html.index(stage.BEGIN) < html.index("</head>"), "the block belongs in the head"

        # A brand kit gives its own token set (values from fixtures/brand-kit/FRAME.md).
        comp = composition(tmp / "brand")
        stage.stage(comp, BRAND, fetch=fetch)
        css = (comp / "assets" / "theme.css").read_text(encoding="utf-8")
        for decl in ("--paper: #EEF3F5;", "--ink: #12263A;", "--accent: #B5651D;", "--muted: #4A5B6A;",
                     '--font-display: "Inter", serif;', '--font-body: "Inter", sans-serif;'):
            assert decl in css, f"missing {decl} in brand theme.css:\n{css}"

        # Stock Hyperframes presets map through the alias table (fixture mimics the key shape: accent named primary,
        # no font files).
        sys_stack = "system-ui, sans-serif;"
        comp = composition(tmp / "stock-blue-professional")
        stage.stage(comp, HERE / "fixtures" / "stock-blue-professional", fetch=fetch)
        css = (comp / "assets" / "theme.css").read_text(encoding="utf-8")
        for decl in ("--paper: #fdfae7;", "--ink: #111111;", "--accent: #1e2bfa;", "--muted: #6b6b6b;",
                     f'--font-display: "Space Grotesk", {sys_stack}', f'--font-body: "Inter", {sys_stack}'):
            assert decl in css, f"missing {decl} in stock-blue-professional theme.css:\n{css}"
        assert "@font-face" not in css, css

        # A preset with no accent key is not guessed (capsule's colours are named cream, coral, lime): it fails and
        # names the work/theme path, where the agent picks the accent with judgment.
        fails(lambda: stage.stage(composition(tmp / "c0"), HERE / "fixtures" / "stock-capsule", fetch=fetch), "work/theme")
        fails(lambda: stage.stage(composition(tmp / "c0b"), HERE / "fixtures" / "stock-capsule", fetch=fetch), "'accent'")

        # An accent under 3:1 against paper (biennale-yellow's sun on its paper, about 1.05:1) would hide rings and
        # highlights: staging stops naming both colours.
        pale = tmp / "pale"
        pale.mkdir()
        (pale / "FRAME.md").write_text('---\ncolors:\n  paper: "#E9E5DB"\n  ink: "#111111"\n  accent: "#F1EE2E"\ntypography:\n  body: { fontFamily: "Inter", px: 20 }\n  h1: { fontFamily: "Inter", px: 60 }\n---\n', encoding="utf-8")
        fails(lambda: stage.stage(composition(tmp / "c0c"), pale, fetch=fetch), "#F1EE2E")
        fails(lambda: stage.stage(composition(tmp / "c0d"), pale, fetch=fetch), "#E9E5DB")
        assert round(stage.contrast("#000000", "#ffffff"), 2) == 21.0 and round(stage.contrast("#777777", "#ffffff"), 2) == 4.48

        # Clear failures, never a half-staged fallback.
        fails(lambda: stage.resolve(theme="no-such-theme"), "no-such-theme")
        fails(lambda: stage.resolve(brand="no-such-brand", brands=tmp / "brands"), "no-such-brand")
        broken = tmp / "brands" / "broken"
        shutil.copytree(BRAND, broken)
        (broken / "logo.svg").unlink()
        fails(lambda: stage.resolve(brand="broken", brands=tmp / "brands"), "logo")
        assert stage.resolve(brand="brand-kit", brands=HERE / "fixtures") == HERE / "fixtures" / "brand-kit"
        assert stage.resolve(theme="showhow") == PRESET
        assert stage.resolve(theme=str(BRAND)) == BRAND, "a folder with FRAME.md is a theme (a product's own)"
        fails(lambda: stage.stage(tmp / "nowhere", PRESET, fetch=fetch), "index.html")

        bad = tmp / "bad-theme"
        shutil.copytree(PRESET, bad)
        frame = bad / "FRAME.md"
        frame.write_text(frame.read_text(encoding="utf-8").replace('  paper: "#F3ECDD"\n', ""), encoding="utf-8")
        fails(lambda: stage.stage(composition(tmp / "c1"), bad, fetch=fetch), "paper")
        shutil.rmtree(bad)
        shutil.copytree(PRESET, bad)
        (bad / "fonts" / "EBGaramond-700.woff2").unlink()
        (bad / "fonts" / "EBGaramond-400.woff2").unlink()
        fails(lambda: stage.stage(composition(tmp / "c2"), bad, fetch=fetch), "EB Garamond")

    # Pins live in stage.py only: no other shipped file names a gsap or three version.
    for p in shipped():
        if p.suffix in (".md", ".html", ".js", ".mjs", ".css", ".py", ".ps1") and p.name not in ("stage.py", "test_stage.py"):
            text = p.read_text(encoding="utf-8", errors="ignore")
            assert not re.search(r"(gsap|three)@\d", text), f"version pin outside stage.py: {p}"

    # One token set: the old accent name and its fallback colours are gone everywhere.
    for p in shipped():
        if p.suffix in (".md", ".html", ".js", ".css", ".py") and p.name != "test_stage.py":
            text = p.read_text(encoding="utf-8", errors="ignore")
            for old in ("--sh-accent", "#2f80ed", "#0078d4"):
                assert old not in text, f"{old} still in {p}"
    s3d = (SKILL / "assets" / "scene3d" / "scene3d.js").read_text(encoding="utf-8")
    assert not re.search(r"#[0-9A-Fa-f]{6}", s3d), "scene3d.js must take every colour from the theme"
    kit = (SKILL / "assets" / "kit" / "showhow-kit.css").read_text(encoding="utf-8")
    assert kit.count("var(--accent)") == 2, "rings and ripples use --accent with no fallback"
    print("ok")


if __name__ == "__main__":
    main()
