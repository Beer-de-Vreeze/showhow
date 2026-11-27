"""Self-check for the bundled `showhow` frame preset. Run:
  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/test_theme_preset.py
"""

import re
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
PRESET = SKILL / "assets" / "frame-presets" / "showhow"


def main() -> None:
    frame = (PRESET / "FRAME.md").read_text(encoding="utf-8")
    head = frame.split("---")[1]
    assert re.search(r"^name: .*Showhow", head, re.M), "frontmatter name"
    for hexval in ("#F3ECDD", "#23201B", "#0F6E6A"):  # paper, ink, teal
        assert hexval in head, f"missing colour {hexval}"
    for section in ("## Overview", "## Colors", "## Typography", "## Aspect-Ratio Behavior", "## Pre-Render Self-Audit"):
        assert section in frame, f"missing {section}"

    fonts = PRESET / "fonts"
    for f in ("EBGaramond-400.woff2", "EBGaramond-700.woff2", "Inter-400.woff2", "Inter-700.woff2", "OFL-eb-garamond.txt", "OFL-inter.txt"):
        assert (fonts / f).is_file(), f"missing fonts/{f}"
    for lic in ("OFL-eb-garamond.txt", "OFL-inter.txt"):
        assert "SIL OPEN FONT LICENSE" in (fonts / lic).read_text(encoding="utf-8").upper(), f"{lic} is not the OFL"

    skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "assets/frame-presets/" in skill and "`showhow`" in skill, "SKILL.md must name the bundled preset"
    assert skill.count("Theme lookup order") == 1, "the lookup order lives in one place"
    explainer = (SKILL / "references" / "explainer.md").read_text(encoding="utf-8")
    assert "`showhow`" in explainer, "explainer.md must name the default theme"
    print("ok")


if __name__ == "__main__":
    main()
