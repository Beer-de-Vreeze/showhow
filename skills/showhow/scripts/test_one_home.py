"""Self-check: each threshold has one home. Run:
  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/test_one_home.py

The gate scripts own the numbers; the docs name the gate (G-captions, P-time) instead.
At most one doc may still state a threshold (the teaching law in SKILL.md, the measured level in audio.md),
so a threshold change is one gate edit, its test, and at most one doc.
"""

import re
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL / "scripts"

# threshold -> (wording in a doc, the gate that owns the number, the number as the gate writes it)
THRESHOLDS = {
    "caption characters": (r"37 char", "video_gates.py", "CAPTION_LINE_MAX = 37"),
    "caption lines": (r"\b(2|two) lines \((3|three)", "video_gates.py", "3 in a video taller than wide"),
    "caption reading time": (r"0\.3 ?s per word", "video_gates.py", "CAPTION_SECONDS_PER_WORD = 0.3"),
    "duration hard limit": (r"hard limit \d|limit 60 ?s|\d ?s hard limit", "plan_gates.py", '"howto": 180.0'),
    "duration target": (r"\b(45|30|60)-(90|120) ?s\b", "plan_gates.py", "60 <= total <= 120"),
    "music level": (r"0\.035", None, None),
}


def docs_stating(pattern: str) -> list[str]:
    return sorted(
        str(p.relative_to(SKILL))
        for p in SKILL.rglob("*.md")
        if re.search(pattern, p.read_text(encoding="utf-8"), re.I)
    )


def main() -> None:
    for name, (pattern, gate, number) in THRESHOLDS.items():
        found = docs_stating(pattern)
        assert len(found) <= 1, f"{name} is stated in {len(found)} docs, keep one and name the gate: {found}"
        if gate:
            assert number in (SCRIPTS / gate).read_text(encoding="utf-8"), f"{name}: {gate} must own the number"
    print("ok")


if __name__ == "__main__":
    main()
