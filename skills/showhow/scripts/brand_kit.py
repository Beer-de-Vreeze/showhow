"""Validate a showhow brand kit folder before a run uses it.

  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/brand_kit.py check <kit-dir>

Prints PASS and exits 0, or one line per problem and exits 1.
Stdlib only. FRAME.md is read the way the bundled `showhow` preset is laid out:
YAML-ish frontmatter between the first two `---` lines.
"""

import re
import sys
from pathlib import Path

REQUIRED_COLORS = ("paper", "ink", "accent")
NAMED = {  # shortcut: a small set of CSS names, add more when a real kit needs one
    "black", "white", "red", "green", "blue", "yellow", "orange", "purple", "pink", "gray", "grey",
    "teal", "navy", "maroon", "silver", "cyan", "magenta", "brown", "gold", "transparent",
}
# shortcut: shape-only check (hex, colour functions with comma or space args, a name from NAMED), not a full CSS
# parser; it accepts out-of-range values. Use a real CSS parser if a kit ever ships a colour it gets wrong.
ARG = r"[-+]?[0-9.]+(?:%|deg|turn|rad|grad)?"
COLOR_RE = re.compile(
    rf"^(#(?:[0-9a-f]{{3,4}}|[0-9a-f]{{6}}|[0-9a-f]{{8}})|(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\(\s*{ARG}(?:\s*[, /]\s*{ARG}){{2,3}}\s*\))$",
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


def check(kit: Path) -> list[str]:
    frame = kit / "FRAME.md"
    if not frame.is_file():
        return [f"missing FRAME.md in {kit}"]
    head = frontmatter(frame.read_text(encoding="utf-8"))
    problems = []
    if not head.strip():
        return ["FRAME.md has no frontmatter"]

    colors = {}
    for ln in block(head, "colors"):
        m = re.match(r"([\w-]+):\s*[\"']?([^\"']+?)[\"']?\s*$", ln)
        if m:
            colors[m.group(1)] = m.group(2)
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
