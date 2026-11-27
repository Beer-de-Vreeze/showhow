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
Explainer mode (no counters, so no P-steps or P-action; P-time has no step minimum):
P-need:   no "[NEED" marker left in the narration (scenes or the "## Narration script" section).
P-visual: every voiced scene has exactly one "Visual:" from VISUALS; parallax only on the first scene.
P-time:   total under 180s; a total outside 60-120s passes with a warning.
P-end:    the last scene before the outro is a recap.
P-params: a "Visual: scene3d" scene has a "Params:" JSON object with a known "kind" (SCENE3D_KINDS) or a
          "model"; a globe has a "country" or a "route" of 2+ places; every number in it appears in the narration ("stages": 12 needs "12" spoken).
P-render: with --chapters, the rendered steps match the plan's count and each lasts the minimum.
Exit code 1 when a gate fails.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from video_gates import video_duration

MIN_STEP = {"howto": 6.0, "quick-tip": 5.0, "update": 10.0, "general": 6.0, "explainer": 0.0}
HARD_LIMIT = {"howto": 180.0, "quick-tip": 60.0, "update": 120.0, "general": 180.0, "explainer": 180.0}
# The visual menu for explainer scenes; later tickets add their types here (references/explainer.md).
VISUALS = ("flow", "chart", "map", "photo", "card", "stroke-reveal", "kinetic-type", "data-anim", "morph", "flat-scene", "parallax", "scene3d")
FIRST_SCENE_ONLY = ("parallax",)  # intro motion; it never competes with an explanation
# Params.kind values with a recipe in assets/scene3d (references/3d-scenes.md); Params.model replaces any kind.
SCENE3D_KINDS = ("machine", "globe", "hero-number")
MAX_STEPS = {"howto": 8, "quick-tip": 3, "update": 5, "general": 8}
MULTI_ACTION = re.compile(r"\bthen\b|;|->|→|\band\s+(?:click|press|select|type|open|choose|drag)\b", re.I)


def parse_plan(text: str) -> dict:
    mode_line = re.search(r"^## Mode\s*\n+\s*\[?(\w[\w-]*)", text, re.M)
    if not mode_line:
        raise SystemExit("no '## Mode' section with howto, update or general in the plan")
    mode = mode_line.group(1).lower()
    if mode not in ("howto", "update", "general", "explainer"):
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
        visual = re.search(r"^Visual:\s*(.+)$", body, re.M)
        params = re.search(r"^Params:\s*(.+)$", body, re.M)
        scenes.append({
            "n": int(m.group(1)), "name": m.group(2).strip(), "secs": float(m.group(3)),
            "counter": (int(counter.group(1)), int(counter.group(2))) if counter else None,
            "action": action.group(1).strip() if action else "",
            "on_screen": on_screen.group(1).strip() if on_screen else "",
            "narration": narration.group(1).strip() if narration else "",
            "visual": visual.group(1).strip("[]*` ").lower() if visual else "",
            "params": params.group(1).strip().strip("`") if params else "",
        })
    if not scenes:
        raise SystemExit("no '### Scene N - name - Ns' blocks in the plan's storyboard")
    if mode == "quick-tip":
        # A quick-tip shows no counter (SKILL.md): its action scenes are the steps.
        acts = [sc for sc in scenes if has_action(sc)]
        for k, sc in enumerate(acts, 1):
            sc["counter"] = (k, len(acts))
    script = re.search(r"^## Narration script\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return {"mode": mode, "scenes": scenes, "script": script.group(1) if script else ""}


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
    if mode == "explainer":
        return check_explainer(plan) + check_described(scenes)

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

    return results + check_described(scenes)


def check_described(scenes: list[dict]) -> list[tuple[str, bool, str]]:
    if not any(s["on_screen"] for s in scenes):
        return []
    gaps = [f"scene {s['n']} missing {', '.join(g)}" for s in scenes if s["on_screen"] and (g := described_gaps(s))]
    return [("P-described", not gaps, "on-screen facts are spoken" if not gaps else "; ".join(gaps))]


def check_explainer(plan: dict) -> list[tuple[str, bool, str]]:
    scenes = plan["scenes"]
    needs = re.findall(r"\[NEED[^\]]*\]?", plan["script"] + " " + " ".join(s["narration"] for s in scenes))
    results = [("P-need", not needs, "no [NEED] markers left" if not needs else "unfilled: " + "; ".join(needs))]

    bad = []
    for s in scenes:
        if s["visual"].strip() in FIRST_SCENE_ONLY and s is not scenes[0]:
            bad.append(f"scene {s['n']} uses {s['visual'].strip()!r}, allowed only on the first scene")
            continue
        if not s["narration"]:
            continue
        kinds = [v.strip() for v in re.split(r"[,/+]|\band\b", s["visual"]) if v.strip()]
        if len(kinds) != 1:
            bad.append(f"scene {s['n']} has {len(kinds) or 'no'} Visual: values (need exactly one)")
        elif kinds[0] not in VISUALS:
            bad.append(f"scene {s['n']} unknown visual {kinds[0]!r} (allowed: {', '.join(VISUALS)})")
    results.append(("P-visual", not bad, "one known visual per voiced scene" if not bad else "; ".join(bad)))

    total = sum(s["secs"] for s in scenes)
    msg = f"total {total:.0f}s (limit {HARD_LIMIT['explainer']:.0f}s)"
    if not 60 <= total <= 120:
        msg += "; warning: outside 60-120s"
    results.append(("P-time", total <= HARD_LIMIT["explainer"], msg))

    body = [sc for sc in scenes if not re.search(r"outro|credit|end card", sc["name"], re.I)] or scenes
    ok = "recap" in body[-1]["name"].lower()
    results.append(("P-end", ok, f"last scene is {body[-1]['name']!r}" + ("" if ok else "; end on a recap")))
    return results + check_params(plan)


def param_numbers(value) -> list[str]:
    if isinstance(value, dict):
        # lat and lon are map coordinates the plan states, not figures the narration speaks.
        return [n for k, v in value.items() if k not in ("lat", "lon") for n in param_numbers(v)]
    if isinstance(value, list):
        return [n for v in value for n in param_numbers(v)]
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return [str(int(value)) if float(value).is_integer() else repr(value)]
    return []


def check_params(plan: dict) -> list[tuple[str, bool, str]]:
    """P-params: a scene3d scene has a known Params.kind or a Params.model, and every number in Params is spoken."""
    scenes = [s for s in plan["scenes"] if s["visual"] == "scene3d"]
    if not scenes:
        return []
    spoken = numbers(plan["script"] + " " + " ".join(s["narration"] for s in plan["scenes"]))
    bad = []
    for s in scenes:
        try:
            params = json.loads(s["params"] or "{}")
        except json.JSONDecodeError as e:
            bad.append(f"scene {s['n']} Params is not JSON ({e.msg})")
            continue
        if not isinstance(params, dict):
            bad.append(f"scene {s['n']} Params is not a JSON object")
            continue
        kind = params.get("kind")
        if not params.get("model") and kind not in SCENE3D_KINDS:
            bad.append(f"scene {s['n']} unknown kind {kind!r} and no model (kinds: {', '.join(SCENE3D_KINDS)})")
        if not params.get("model") and kind == "globe":
            route = params.get("route")
            if not params.get("country") and not (isinstance(route, list) and len(route) >= 2):
                bad.append(f"scene {s['n']} globe needs Params.country or a Params.route of 2+ places")
        missing = [n for n in param_numbers(params) if n not in spoken]
        if missing:
            bad.append(f"scene {s['n']} Params numbers not in the narration: {', '.join(missing)}")
    return [("P-params", not bad, "Params match the narration" if not bad else "; ".join(bad))]


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
    if mode == "explainer":
        return ("P-render", True, f"{len(chapters)} chapters (one per section; no step count to match)")
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
