"""Validate a showhow brand kit folder before a run uses it.

  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/brand_kit.py check <kit-dir>

Prints PASS and exits 0, or one line per problem and exits 1.
Stdlib only. FRAME.md is read the way the bundled `showhow` preset is laid out:
YAML-ish frontmatter between the first two `---` lines.
"""

import re
import sys
from pathlib import Path

REQUIRED_COLORS = ("paper", "ink", "accent")  # muted is optional: stage.py falls back to ink
NAMED = {  # shortcut: a small set of CSS names, add more when a real kit needs one
    "black", "white", "red", "green", "blue", "yellow", "orange", "purple", "pink", "gray", "grey",
    "teal", "navy", "maroon", "silver", "cyan", "magenta", "brown", "gold",
}
# Only the forms both PIL's ImageColor (bake_highlights rings) and THREE.Color (scene3d) parse: 3- or 6-digit hex,
# comma rgb() in integers or integer percents, comma hsl(); anything else crashes the bake or turns scene3d white.
# shortcut: shape-only, it accepts out-of-range values; use a real CSS parser if a kit ships a colour it gets wrong.
N = r"\d+(?:\.\d+)?"
COLOR_RE = re.compile(
    rf"^(#(?:[0-9a-f]{{3}}|[0-9a-f]{{6}})|rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)|rgb\(\s*\d+%\s*,\s*\d+%\s*,\s*\d+%\s*\)"
    rf"|hsl\(\s*{N}\s*,\s*{N}%\s*,\s*{N}%\s*\))$",
    re.I,
)


def valid_color(v: str) -> bool:
    return bool(COLOR_RE.match(v)) or v.lower() in NAMED


def frontmatter(text: str) -> str:
    parts = text.split("---")
    return parts[1] if len(parts) > 2 else ""


def block(head: str, key: str) -> list[str]:
    """Indented lines under a top-level `key:` line."""
    lines = head.splitlines()
    for i, ln in enumerate(lines):
        if ln.rstrip() == f"{key}:":
            out = []
            for nxt in lines[i + 1:]:
                if nxt.strip() and not nxt.startswith(" "):
                    break
                if nxt.strip():
                    out.append(nxt.strip())
            return out
    return []


def scalar(head: str, key: str) -> str | None:
    m = re.search(rf"^{key}:\s*(.+)$", head, re.M)
    return m.group(1).strip().strip("\"'") if m else None


def parse_colors(head: str) -> dict[str, str]:
    colors = {}
    for ln in block(head, "colors"):
        m = re.match(r"([\w-]+):\s*[\"']?([^\"']+?)[\"']?\s*$", ln)
        if m:
            colors[m.group(1)] = m.group(2)
    return colors


FONT_ALIASES = {"title": ("title", "h1", "headline", "hero-title", "display"), "label": ("label", "body")}
FONT_TYPES = (".woff2", ".woff", ".ttf", ".otf")


def font_faces(theme: Path, head: str) -> tuple[dict[str, str], list[str], list[str]]:
    """The title and label families (first alias in `typography:`), an @font-face per theme/fonts/<Family>-<weight>
    file, and the problems; stage.py writes theme.css from these, so check() rejects what staging would."""
    ramp = {}
    for ln in block(head, "typography"):
        m = re.match(r"([\w-]+):\s*\{.*fontFamily:\s*[\"']([^\"']+)[\"']", ln)
        if m:
            ramp[m.group(1)] = m.group(2)
    families, problems = {}, []
    for role, names in FONT_ALIASES.items():
        found = next((ramp[n] for n in names if n in ramp), None)
        if found:
            families[role] = found
        else:
            problems.append(f"FRAME.md typography: no fontFamily for '{role}' (or an alias: {', '.join(names[1:]) or 'none'})")

    # Font files are named <Family without spaces>-<weight>.<ext>, e.g. EBGaramond-700.woff2.
    # shortcut: a theme with no fonts/ folder (every stock Hyperframes preset) gets the family names plus a system
    # font stack and no @font-face, so the render uses whatever is installed; ship fonts/ to pin the faces.
    faces = []
    if (theme / "fonts").is_dir():
        files = sorted(p for p in (theme / "fonts").glob("*") if p.suffix.lower() in FONT_TYPES)
        for family in dict.fromkeys(families.values()):
            mine = [(p, w) for p in files for f, _, w in [p.stem.rpartition("-")] if f == family.replace(" ", "") and w.isdigit()]
            if not mine:
                problems.append(f"no font file for '{family}' in {theme / 'fonts'} (name it {family.replace(' ', '')}-<weight>.woff2)")
            faces += [f'@font-face {{ font-family: "{family}"; src: url("fonts/{p.name}"); font-weight: {w}; }}' for p, w in mine]
    return families, faces, problems


def check(kit: Path) -> list[str]:
    frame = kit / "FRAME.md"
    if not frame.is_file():
        return [f"missing FRAME.md in {kit}"]
    head = frontmatter(frame.read_text(encoding="utf-8"))
    problems = []
    if not head.strip():
        return ["FRAME.md has no frontmatter"]

    colors = parse_colors(head)
    for key in REQUIRED_COLORS:
        if key not in colors:
            problems.append(f"FRAME.md colors: missing key '{key}'")
    for key, val in colors.items():
        if not valid_color(val):
            problems.append(f"FRAME.md colors: '{key}' is not a CSS colour: {val}")

    fonts = [ln[1:].strip().strip("\"'") for ln in block(head, "fonts") if ln.startswith("-")]
    if not fonts:
        problems.append("FRAME.md fonts: no font files listed")
    for f in fonts:
        problems += file_problems(kit, f, "font")
    problems += font_faces(kit, head)[2]

    logo = scalar(head, "logo")
    if not logo:
        problems.append("FRAME.md: no 'logo:' line")
    else:
        problems += file_problems(kit, logo, "logo")

    music = scalar(head, "music")
    if music:
        problems += file_problems(kit, music, "music")
    return problems


def file_problems(kit: Path, name: str, what: str) -> list[str]:
    """A kit file must exist and sit inside the kit, so a third-party FRAME.md can't point the copy step elsewhere."""
    path = (kit / name).resolve()
    if not path.is_relative_to(kit.resolve()):
        return [f"{what} file {name} is outside the kit folder"]
    return [] if path.is_file() else [f"missing {what} file {name}"]


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[1] != "check":
        print("usage: brand_kit.py check <kit-dir>", file=sys.stderr)
        return 2
    problems = check(Path(argv[2]))
    if problems:
        print("\n".join(f"FAIL {p}" for p in problems))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
