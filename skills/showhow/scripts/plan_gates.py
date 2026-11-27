#!/usr/bin/env python3
"""Check showhow's teaching laws on the plan, and on the render's chapters when given.

  uv run --project <skill-dir>/scripts <skill-dir>/scripts/plan_gates.py showhow-plan.md \
      [--chapters chapters.txt --video <video-name>.mp4]

Run it after writing the plan (Step 2) and again after the render with --chapters and --video,
so the timing the viewer actually gets is checked, not only the timing that was planned.

P-steps:  the step (or change) counters run 1..N with one N, and N fits the mode
          (howto 1-8 steps, update 2-5 changes).
P-action: each step does one thing; catches the usual joins in its Action line: "then", ";",
          arrows, and "and click/press/select/type/open/choose/drag".
P-time:   each step lasts at least 6s (quick-tip 5s, update changes 10s); the whole video stays
          under the hard limit (howto 180s, quick-tip 60s, update 120s).
P-end:    a howto (and a general task) ends on a "Now try it" scene, not a recap; a credits outro
          after it is fine; quick-tip ends on the result and a general topic video on its recap.
P-described: every number and **bold label** in a scene's optional "On screen:" line is also in that
          scene's "Narration:" line (WCAG 1.2.5); numbers match by digits ("40x" and "1,700" match
          "40" and "1700"), labels ignore case. Runs in every mode; skipped without "On screen:" lines.
P-render: with --chapters, the rendered steps match the plan's count and each lasts the minimum.
Exit code 1 when a gate fails.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from video_gates import video_duration

MIN_STEP = {"howto": 6.0, "quick-tip": 5.0, "update": 10.0, "general": 6.0}
HARD_LIMIT = {"howto": 180.0, "quick-tip": 60.0, "update": 120.0, "general": 180.0}
MAX_STEPS = {"howto": 8, "quick-tip": 3, "update": 5, "general": 8}
MULTI_ACTION = re.compile(r"\bthen\b|;|->|→|\band\s+(?:click|press|select|type|open|choose|drag)\b", re.I)


def parse_plan(text: str) -> dict:
    mode_line = re.search(r"^## Mode\s*\n+\s*\[?(\w[\w-]*)", text, re.M)
    if not mode_line:
        raise SystemExit("no '## Mode' section with howto, update or general in the plan")
    mode = mode_line.group(1).lower()
    if mode not in ("howto", "update", "general"):
        raise SystemExit(f"unknown mode {mode!r} in the plan")
    if mode != "update" and re.search(r"^- Preset:\s*`?quick-tip", text, re.M | re.I):
        mode = "quick-tip"

    scenes = []
    for m in re.finditer(r"^### Scene (\d+) - (.+?) - ([\d.]+)\s*s\b(.*?)(?=^### Scene |\Z|^## )", text, re.M | re.S):
        body = m.group(4)
        counter = re.search(r"^Counter:\s*\"?(?:(?:Step|Change|Point)\s+)?(\d+)\s+of\s+(\d+)", body, re.M | re.I)
        action = re.search(r"^Action:\s*(.+)$", body, re.M)
        on_screen = re.search(r"^On screen:\s*(.+)$", body, re.M)
        narration = re.search(r"^Narration:\s*(.+)$", body, re.M)
        scenes.append({
            "n": int(m.group(1)), "name": m.group(2).strip(), "secs": float(m.group(3)),
            "counter": (int(counter.group(1)), int(counter.group(2))) if counter else None,
            "action": action.group(1).strip() if action else "",
            "on_screen": on_screen.group(1).strip() if on_screen else "",
            "narration": narration.group(1).strip() if narration else "",
        })
    if not scenes:
        raise SystemExit("no '### Scene N - name - Ns' blocks in the plan's storyboard")
    if mode == "quick-tip":
        # A quick-tip shows no counter (SKILL.md): its action scenes are the steps.
        acts = [sc for sc in scenes if has_action(sc)]
        for k, sc in enumerate(acts, 1):
            sc["counter"] = (k, len(acts))
    return {"mode": mode, "scenes": scenes}


def numbers(text: str) -> set[str]:
    return set(re.findall(r"\d+(?:\.\d+)?", re.sub(r"(?<=\d),(?=\d{3})", "", text)))


def described_gaps(scene: dict) -> list[str]:
    shown, said = scene["on_screen"], scene["narration"]
    labels = re.findall(r"\*\*(.+?)\*\*", shown)
    spoken = said.replace("*", "").lower()
    return sorted(numbers(shown) - numbers(said)) + [f"'{b}'" for b in labels if b.lower() not in spoken]


def has_action(scene: dict) -> bool:
    return bool(scene["action"]) and scene["action"].strip("[]*` ").lower() not in ("none", "-", "n/a")


def step_scenes(plan: dict) -> list[dict]:
    return [s for s in plan["scenes"] if s["counter"]]


def check_plan(plan: dict) -> list[tuple[str, bool, str]]:
    mode, scenes, steps = plan["mode"], plan["scenes"], step_scenes(plan)
    results = []

    totals = {c[1] for c in (s["counter"] for s in steps)}
    order = [s["counter"][0] for s in steps]
    # A step may span scenes (same counter), so compare the distinct numbers in order.
    distinct = [n for i, n in enumerate(order) if i == 0 or n != order[i - 1]]
    n = max(totals) if totals else 0
    ok = bool(steps) and len(totals) == 1 and distinct == list(range(1, n + 1))
    low = 2 if mode == "update" else 1
    ok = ok and low <= n <= MAX_STEPS[mode]
    results.append(("P-steps", ok, f"{n} {'changes' if mode == 'update' else 'steps'}, counters {distinct or 'none'} of {sorted(totals) or 'none'} (allowed {low}-{MAX_STEPS[mode]})"))

    bad = [f"scene {s['n']}: {s['action']}" for s in steps if MULTI_ACTION.search(s["action"])]
    results.append(("P-action", not bad, "one action per step" if not bad else "more than one action in " + " | ".join(bad)))

    per_step: dict[int, float] = {}
    for s in steps:
        per_step[s["counter"][0]] = per_step.get(s["counter"][0], 0.0) + s["secs"]
    short = [f"step {k} {v:.1f}s" for k, v in per_step.items() if v < MIN_STEP[mode]]
    total = sum(s["secs"] for s in scenes)
    over = total > HARD_LIMIT[mode]
    msg = f"total {total:.0f}s (limit {HARD_LIMIT[mode]:.0f}s), each step at least {MIN_STEP[mode]:.0f}s"
    if short:
        msg += "; too short: " + ", ".join(short)
    results.append(("P-time", not short and not over, msg))

    topic = mode == "general" and not any(has_action(sc) for sc in scenes)
    if mode in ("howto", "general") and not topic:
        # A credits or outro card may follow "Now try it"; judge the last scene before it.
        body = [sc for sc in scenes if not re.search(r"outro|credit|end card", sc["name"], re.I)] or scenes
        ok = "try" in body[-1]["name"].lower()
        results.append(("P-end", ok, f"last scene is {body[-1]['name']!r}" + ("" if ok else "; end on 'Now try it' with a concrete example, not a recap")))

    if any(s["on_screen"] for s in scenes):
        gaps = [f"scene {s['n']} missing {', '.join(g)}" for s in scenes if s["on_screen"] and (g := described_gaps(s))]
        results.append(("P-described", not gaps, "on-screen facts are spoken" if not gaps else "; ".join(gaps)))
    return results


def parse_chapters(text: str, duration: float) -> list[tuple[str, float]]:
    rows = []
    for line in text.splitlines():
        m = re.match(r"\s*(?:(\d+):)?(\d+):(\d+)\s+(.+)", line)
        if m:
            h, mm, ss, title = m.groups()
            rows.append((title.strip(), int(h or 0) * 3600 + int(mm) * 60 + int(ss)))
    if not rows:
        raise SystemExit("no 'MM:SS Title' lines in the chapters file")
    ends = [t for _, t in rows[1:]] + [duration]
    return [(title, end - start) for (title, start), end in zip(rows, ends)]


def check_render(plan: dict, chapters: list[tuple[str, float]]) -> tuple[str, bool, str]:
    mode = plan["mode"]
    word = {"update": r"^change\s*\d+", "general": r"^(?:step|point)\s*\d+"}.get(mode, r"^step\s*\d+")
    steps = [(t, d) for t, d in chapters if re.match(word, t, re.I)]
    planned = max((s["counter"][1] for s in step_scenes(plan)), default=0)
    short = [f"{t!r} {d:.0f}s" for t, d in steps if d < MIN_STEP[mode]]
    ok = len(steps) == planned and not short
    msg = f"{len(steps)} rendered steps vs {planned} planned"
    if short:
        msg += "; too short: " + ", ".join(short)
    return ("P-render", ok, msg)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--chapters", type=Path, help="chapters.txt of the render")
    parser.add_argument("--video", type=Path, help="the rendered mp4, for the last chapter's length")
    args = parser.parse_args()
    if bool(args.chapters) != bool(args.video):
        raise SystemExit("give --chapters and --video together")

    plan = parse_plan(args.plan.read_text(encoding="utf-8"))
    results = check_plan(plan)
    if args.chapters:
        chapters = parse_chapters(args.chapters.read_text(encoding="utf-8"), video_duration(args.video))
        results.append(check_render(plan, chapters))

    for name, ok, msg in results:
        print(f"{name} {'PASS' if ok else 'FAIL'}: {msg}")
    return 0 if all(ok for _, ok, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main())
