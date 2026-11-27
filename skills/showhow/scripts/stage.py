"""Stage a composition folder: every asset it may use, local, plus the theme's token set.

  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/stage.py <composition-dir> (--theme <name> | --brand <name>)

Copies into <composition-dir>/assets/: kit/, scene3d/ (with its data), gsap/ (GSAP and the DrawSVG, MorphSVG,
SplitText and MotionPath plugins), three/ (build, examples/jsm addons, the helvetiker_bold typeface), fonts/
(the theme's font files and licences), and writes theme.css: @font-face for each font file and one :root
token set, --paper --ink --accent --muted --font-display --font-body, from the theme's FRAME.md.
Copies FRAME.md to <composition-dir>/frame.md and writes a block into index.html's <head> (between
BEGIN and END, replaced on every run) with the three.js import map and the theme.css link.
Everything is local at render time; npm packages come from `npm pack` into a cache folder, never a CDN.
Re-run it after changing the theme; never edit the staged files.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

from brand_kit import block, check, frontmatter, parse_colors, valid_color

# Every version pin for staged assets lives here.
GSAP = "gsap@3.14.2"
THREE = "three@0.184.0"

SKILL = Path(__file__).resolve().parent.parent
PRESETS = (SKILL / "assets" / "frame-presets", SKILL.parent / "hyperframes" / "assets" / "frame-presets")
BRANDS = Path.home() / ".showhow" / "brands"
CACHE = Path.home() / ".cache" / "showhow" / "npm"
GSAP_FILES = ("gsap", "DrawSVGPlugin", "MorphSVGPlugin", "SplitText", "MotionPathPlugin")
TOKENS = ("paper", "ink", "accent", "muted")
FONT_TYPES = (".woff2", ".woff", ".ttf", ".otf")
BEGIN, END = "<!-- stage.py: generated, re-run stage.py instead of editing -->", "<!-- /stage.py -->"
HEAD = f"""{BEGIN}
    <script type="importmap">
      {{ "imports": {{ "three": "./assets/three/build/three.module.js", "three/addons/": "./assets/three/examples/jsm/" }} }}
    </script>
    <link rel="stylesheet" href="assets/theme.css" />
    {END}"""


def resolve(theme: str | None = None, brand: str | None = None, brands: Path = BRANDS) -> Path:
    """The theme folder (holding FRAME.md) for a preset name, a folder, or a brand kit name; a failing kit stops here."""
    if brand:
        kit = brands / brand
        if not (kit / "FRAME.md").is_file():
            raise SystemExit(f"no brand kit {brand!r}: {kit} has no FRAME.md")
        problems = check(kit)
        if problems:
            raise SystemExit(f"brand kit {brand!r} fails its check:\n" + "\n".join(f"FAIL {p}" for p in problems))
        return kit
    if (Path(str(theme)) / "FRAME.md").is_file():  # a folder: the product's own theme written for this run
        return Path(str(theme))
    for root in PRESETS:
        if (root / str(theme) / "FRAME.md").is_file():
            return root / str(theme)
    raise SystemExit(f"no theme {theme!r} in " + " or ".join(str(r) for r in PRESETS))


def theme_css(theme: Path) -> str:
    """@font-face rules and the :root token set, from theme/FRAME.md and the files in theme/fonts/."""
    head = frontmatter((theme / "FRAME.md").read_text(encoding="utf-8"))
    colors = parse_colors(head)
    problems = [f"FRAME.md colors: missing '{k}'" for k in TOKENS if k not in colors]
    problems += [f"FRAME.md colors: '{k}' is not a CSS colour: {colors[k]}" for k in TOKENS if k in colors and not valid_color(colors[k])]
    families = {}
    for ln in block(head, "typography"):
        m = re.match(r"([\w-]+):\s*\{.*fontFamily:\s*[\"']([^\"']+)[\"']", ln)
        if m:
            families[m.group(1)] = m.group(2)
    for role in ("title", "label"):
        if role not in families:
            problems.append(f"FRAME.md typography: no fontFamily for '{role}'")

    # Font files are named <Family without spaces>-<weight>.<ext>, e.g. EBGaramond-700.woff2.
    faces = []
    files = sorted(p for p in (theme / "fonts").glob("*") if p.suffix.lower() in FONT_TYPES)
    for family in dict.fromkeys(families.values()):
        mine = [(p, w) for p in files for f, _, w in [p.stem.rpartition("-")] if f == family.replace(" ", "") and w.isdigit()]
        if not mine:
            problems.append(f"no font file for '{family}' in {theme / 'fonts'} (name it {family.replace(' ', '')}-<weight>.woff2)")
        faces += [f'@font-face {{ font-family: "{family}"; src: url("fonts/{p.name}"); font-weight: {w}; }}' for p, w in mine]
    if problems:
        raise SystemExit(f"theme {theme} cannot be staged:\n" + "\n".join(f"FAIL {p}" for p in problems))

    tokens = [f"  --{k}: {colors[k]};" for k in TOKENS]
    tokens += [f'  --font-display: "{families["title"]}", serif;', f'  --font-body: "{families["label"]}", sans-serif;']
    return f"/* Written by stage.py from {theme.name}/FRAME.md; edit the theme and re-run stage.py. */\n" + "\n".join(faces) + "\n:root {\n" + "\n".join(tokens) + "\n}\n"


def npm_fetch(spec: str) -> Path:
    """The `npm pack` tarball for spec (name@version), from the cache folder; packs it there on the first use."""
    name, version = spec.rsplit("@", 1)
    tgz = CACHE / f"{name}-{version}.tgz"
    if not tgz.is_file():
        CACHE.mkdir(parents=True, exist_ok=True)
        npm = shutil.which("npm") or "npm"
        r = subprocess.run([npm, "pack", spec, "--pack-destination", str(CACHE)], capture_output=True, text=True)
        if r.returncode or not tgz.is_file():
            raise SystemExit(f"npm pack {spec} failed:\n{r.stdout}{r.stderr}")
    return tgz


def unpack(tgz: Path, into: Path) -> Path:
    with tarfile.open(tgz) as tar:
        tar.extractall(into, filter="data")  # data filter: no absolute paths, links or files outside `into`
    return into / "package"


def copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)


def stage(comp: Path, theme: Path, fetch=npm_fetch) -> None:
    index = comp / "index.html"
    if not index.is_file():
        raise SystemExit(f"no index.html in {comp}; pass the composition folder")
    html = index.read_text(encoding="utf-8")
    if BEGIN in html and END in html:
        html = html[: html.index(BEGIN)] + HEAD + html[html.index(END) + len(END):]
    else:
        m = re.search(r"<head[^>]*>", html, re.I)
        if not m:
            raise SystemExit(f"{index} has no <head>")
        html = html[: m.end()] + "\n    " + HEAD + html[m.end():]
    css = theme_css(theme)  # validates the theme before anything is copied

    a = comp / "assets"
    for name in ("kit", "scene3d"):
        copy(SKILL / "assets" / name, a / name)
    with tempfile.TemporaryDirectory() as t:
        gsap = unpack(fetch(GSAP), Path(t) / "gsap")
        for n in GSAP_FILES:
            copy(gsap / "dist" / f"{n}.min.js", a / "gsap" / f"{n}.min.js")
        three = unpack(fetch(THREE), Path(t) / "three")
        for f in ("LICENSE", "build/three.module.js", "build/three.core.js", "examples/jsm",
                  "examples/fonts/helvetiker_bold.typeface.json", "examples/fonts/LICENSE"):
            copy(three / f, a / "three" / f)
    if (theme / "fonts").is_dir():
        copy(theme / "fonts", a / "fonts")
    (a / "theme.css").write_text(css, encoding="utf-8")
    shutil.copy2(theme / "FRAME.md", comp / "frame.md")
    index.write_text(html, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("composition", type=Path)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--theme", help="a frame preset name (assets/frame-presets/<name>), or a folder with FRAME.md and fonts/")
    g.add_argument("--brand", help="a brand kit name (~/.showhow/brands/<name>)")
    args = p.parse_args(argv)
    theme = resolve(args.theme, args.brand)
    stage(args.composition, theme)
    print(f"staged {args.composition} with {theme}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
