"""Stage a composition folder: every asset it may use, local, plus the theme's token set.

  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/stage.py <composition-dir> (--theme <name> | --brand <name>)

Copies into <composition-dir>/assets/: kit/, scene3d/ (with its data), gsap/ (GSAP and the DrawSVG, MorphSVG,
SplitText and MotionPath plugins), three/ (build, examples/jsm addons, the helvetiker_bold typeface), fonts/
(the theme's font files and licences), brand/ (the FRAME.md `logo:` and `music:` files, when given), and writes theme.css: @font-face for each font file and one :root
token set, --paper --ink --accent --muted --font-display --font-body, from the theme's FRAME.md.
A stock Hyperframes preset (no fonts/ folder, other colour keys) is mapped by the ALIASES rule below and
gets its font names with a system-font fallback stack instead of @font-face. A preset the table can't map, or
an accent under 3:1 against paper, stops staging and names the work/theme path.
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

from PIL import ImageColor

from brand_kit import check, file_problems, font_faces, frontmatter, parse_colors, scalar, valid_color

# Every version pin for staged assets lives here.
GSAP = "gsap@3.14.2"
THREE = "three@0.184.0"

SKILL = Path(__file__).resolve().parent.parent
PRESETS = (SKILL / "assets" / "frame-presets", SKILL.parent / "hyperframes" / "assets" / "frame-presets")
BRANDS = Path.home() / ".showhow" / "brands"
CACHE = Path.home() / ".cache" / "showhow" / "npm"
GSAP_FILES = ("gsap", "DrawSVGPlugin", "MorphSVGPlugin", "SplitText", "MotionPathPlugin")
TOKENS = ("paper", "ink", "accent", "muted")
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


# Stock Hyperframes presets name colours and fonts differently from showhow's FRAME.md. The rule, deterministic:
# each token takes the first alias present in `colors:`; muted falls back to ink; a preset with no accent alias is
# never guessed, it fails into the work/theme path. Title and label fonts: brand_kit.FONT_ALIASES.
ALIASES = {
    "paper": ("paper", "bg", "background", "canvas", "cream", "surface"),
    "ink": ("ink", "text", "black", "fg", "foreground"),
    "accent": ("accent", "primary", "brand"),
    "muted": ("muted", "text-muted", "gray", "grey", "text-light"),
}
MIN_ACCENT_CONTRAST = 3.0  # WCAG 1.4.11 non-text contrast: rings, ripples and highlights sit on paper
UNMAPPED = "write work/theme/FRAME.md with paper, ink, accent and muted picked for this video and pass --theme work/theme (general.md)"


def contrast(a: str, b: str) -> float:
    """WCAG contrast ratio of two CSS colours (1 to 21)."""
    def lum(c: str) -> float:
        rgb = (v / 255 for v in ImageColor.getrgb(c)[:3])
        return sum(w * (v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4) for w, v in zip((0.2126, 0.7152, 0.0722), rgb))
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def map_colors(colors: dict[str, str]) -> tuple[dict[str, str | None], list[str]]:
    """The four tokens from a FRAME.md colour map, and a problem naming each token that cannot be mapped."""
    out = {k: next((colors[n] for n in names if n in colors), None) for k, names in ALIASES.items()}
    out["muted"] = out["muted"] or out["ink"]
    problems = [f"FRAME.md colors: missing '{k}' (or an alias: {', '.join(ALIASES[k][1:]) or 'none'}); {UNMAPPED}" for k in TOKENS if out[k] is None]
    problems += [f"FRAME.md colors: '{k}' is not a CSS colour: {out[k]}" for k in TOKENS if out[k] and not valid_color(out[k])]
    if not problems and (ratio := contrast(out["accent"], out["paper"])) < MIN_ACCENT_CONTRAST:
        problems.append(f"FRAME.md colors: accent {out['accent']} on paper {out['paper']} is {ratio:.2f}:1, under {MIN_ACCENT_CONTRAST:g}:1, "
                        f"so rings and highlights would not show; pick a darker or stronger accent, or {UNMAPPED}")
    return out, problems


def theme_css(theme: Path) -> str:
    """@font-face rules and the :root token set, from theme/FRAME.md and the files in theme/fonts/."""
    head = frontmatter((theme / "FRAME.md").read_text(encoding="utf-8"))
    colors, problems = map_colors(parse_colors(head))
    families, faces, font_problems = font_faces(theme, head)
    problems += font_problems
    stock = not (theme / "fonts").is_dir()
    if problems:
        raise SystemExit(f"theme {theme} cannot be staged:\n" + "\n".join(f"FAIL {p}" for p in problems))

    tokens = [f"  --{k}: {colors[k]};" for k in TOKENS]
    tokens += [f'  --font-display: "{families["title"]}", {"system-ui, sans-serif" if stock else "serif"};',
               f'  --font-body: "{families["label"]}", {"system-ui, sans-serif" if stock else "sans-serif"};']
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
    # A kit's logo and music bed go to assets/brand/ (brand-kits.md); a path outside the theme folder is refused.
    head = frontmatter((theme / "FRAME.md").read_text(encoding="utf-8"))
    extras = [(theme / name, file_problems(theme, name, key)) for key in ("logo", "music") if (name := scalar(head, key))]
    if problems := [p for _, ps in extras for p in ps]:
        raise SystemExit(f"theme {theme} cannot be staged:\n" + "\n".join(f"FAIL {p}" for p in problems))

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
    for src, _ in extras:
        copy(src, a / "brand" / src.name)
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
