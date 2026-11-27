#!/usr/bin/env python3
"""Check showhow's teaching laws on the plan, and on the render's chapters when given.

  uv run --project <skill-dir>/scripts <skill-dir>/scripts/plan_gates.py showhow-plan.md \
      [--chapters chapters.txt --video <video-name>.mp4]

Run it after writing the plan (Step 2) and again after the render with --chapters and --video,
so the timing the viewer actually gets is checked, not only the timing that was planned.

This module owns the plan format (the template in references/step-2-plan.md; a test parses it as shipped).
Parsing is strict: a "### Scene" heading or a storyboard field it can't read is a P-parse failure naming the line,
and the other gates wait until the plan parses. A field runs from "Field:" at the start of a line up to the next
field line, so narration may span lines. Mode (## Mode) and style (- Preset:) are independent; the quick-tip style
only changes the step limits of a howto or general video.

parse_plan(text) returns a dict other scripts may use (render.py reads formats and scene starts):
  mode     howto | update | general | explainer
  style    clean | friendly | release | quick-tip (clean when the plan names none)
  formats  format names in FORMATS order: an explainer's "## Formats", else the one "## Format: <name> - WxH"
           (other modes ignore "## Formats"), else all three for an explainer and ["landscape"] otherwise
  scenes   in plan order, each {n, name, secs, start, line, counter, action, on_screen, narration, visual, params};
           start is the sum of the durations before it (seconds), line is the heading's line number,
           counter is (k, of) or None (a quick-tip numbers its action scenes itself)
  script   the "## Narration script" section text
  errors   the P-parse messages, "line N: ..."; empty when the plan reads cleanly

P-parse:  every scene heading reads as "### Scene N - name - Ns", fields are written "Field:" at the start of a
          line (no markup, each once per scene), a Counter reads as "Step 1 of 4" or none, a Preset is a known
          style and a format line names a known format.
P-steps: the step (or change) counters run 1..N with one N, and N fits the mode
          (howto 1-8 steps, update 2-5 changes).
P-action: each step does one thing; catches the usual joins in its Action line: "then", ";",
          arrows, and "and click/press/select/type/open/choose/drag".
P-time:   each step lasts at least 6s (quick-tip 5s, update changes 10s); the whole video stays
          under the hard limit (HARD_LIMIT: howto and general 180s, quick-tip 60s, update 120s).
P-end:    a howto (and a general task) ends on a "Now try it" scene, not a recap; a credits outro
          after it is fine; quick-tip ends on the result and a general topic video on its recap.
P-described: every number and **bold label** in a scene's optional "On screen:" line is also in that
          scene's "Narration:" line (WCAG 1.2.5); numbers match by digits ("40x" and "1,700" match
          "40" and "1700"), labels ignore case. Runs in every mode; skipped without "On screen:" lines
          and on outro, credit or end-card scenes (their credit line is not narrated).
Explainer mode (no counters, so no P-steps or P-action; P-time has no step minimum):
P-need:   no "[NEED" marker left in the narration (scenes or the "## Narration script" section).
P-visual: every voiced scene has exactly one "Visual:" from VISUALS; parallax only on the first scene.
P-time:   total under 180s; a total outside 60-120s passes with a warning.
P-end:    the last scene before the outro is a recap.
P-params: a "Visual: scene3d" scene has a "Params:" JSON object with a known "kind" (SCENE3D_KINDS) or a
          "model"; a globe has a known "country" code or a "route" of 2+ {name, lat, lon} places; every number in it, strings included, appears in the narration ("stages": 12 and "value": "40%" need "12" and "40" spoken).
P-render: with --chapters, the rendered steps match the plan's count and each lasts the minimum; in explainer
          mode there is one chapter per "### " section of the narration script (2-4 when it has none).
Exit code 1 when a gate fails.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from video_gates import video_duration

MODES = ("howto", "update", "general", "explainer")
STYLES = ("clean", "friendly", "release", "quick-tip")  # any style works in any mode (SKILL.md "Styles")
FORMATS = ("landscape", "vertical", "square")
# The storyboard fields of references/step-2-plan.md; a test holds the template to exactly this list.
FIELDS = ("Source", "Screen", "Counter", "Highlight", "Action", "Result", "Narration", "Visual", "Params", "Caption", "On screen", "Audio", "Transition")
MIN_STEP = {"howto": 6.0, "quick-tip": 5.0, "update": 10.0, "general": 6.0}  # explainer has no steps
HARD_LIMIT = {"howto": 180.0, "quick-tip": 60.0, "update": 120.0, "general": 180.0, "explainer": 180.0}
# The visual menu for explainer scenes; a new type is one entry here and one row in references/explainer.md.
VISUALS = ("flow", "chart", "map", "photo", "card", "stroke-reveal", "kinetic-type", "data-anim", "morph", "flat-scene", "parallax", "scene3d")
FIRST_SCENE_ONLY = ("parallax",)  # intro motion; it never competes with an explanation
# Params.kind values with a recipe in assets/scene3d (references/3d-scenes.md); Params.model replaces any kind.
SCENE3D_KINDS = ("machine", "globe", "hero-number")
MAX_STEPS = {"howto": 8, "quick-tip": 3, "update": 5, "general": 8}
MULTI_ACTION = re.compile(r"\bthen\b|;|->|→|\band\s+(?:click|press|select|type|open|choose|drag)\b", re.I)


def parse_plan(text: str) -> dict:
    """The plan as data; see the module docstring for the fields. Unreadable lines land in "errors" (P-parse)."""
    mode_line = re.search(r"^## Mode\s*\n+\s*\[?(\w[\w-]*)", text, re.M)
    if not mode_line:
        raise SystemExit("no '## Mode' section with howto, update, general or explainer in the plan")
    mode = mode_line.group(1).lower()
    if mode not in MODES:
        raise SystemExit(f"unknown mode {mode!r} in the plan")
    errors: list[str] = []
    lines = text.splitlines()

    style = "clean"
    for i, line in enumerate(lines, 1):
        if m := re.match(r"- Preset:[ \t]*\[?`?([\w-]+)", line):
            style = m.group(1).lower()
            if style not in STYLES:
                errors.append(f"line {i}: unknown Preset {style!r} (styles: {', '.join(STYLES)})")

    scenes: list[dict] = []
    fields: dict = {}
    field = None
    for i, line in enumerate(lines, 1):
        if re.match(r"#{1,6}\s*scene\b", line, re.I):
            m = re.fullmatch(r"### Scene (\d+) - (.+) - (\d+(?:\.\d+)?)\s*s\s*", line)
            if not m:
                errors.append(f"line {i}: can't read scene heading {line.strip()!r}; write '### Scene N - name - Ns'")
                field = fields = None
                continue
            fields = {}
            scenes.append({"n": int(m.group(1)), "name": m.group(2).strip(), "secs": float(m.group(3)), "line": i, "fields": fields})
            field = None
        elif line.startswith("#"):
            field = fields = None  # any other heading ends the scene
        elif fields is None:
            continue
        elif m := re.match(rf"({'|'.join(FIELDS)}):(.*)", line):
            field = m.group(1)
            if field in fields:
                errors.append(f"line {i}: second {field}: in scene {scenes[-1]['n']}")
            fields[field] = m.group(2).strip()
        elif m := re.match(rf"[\s>*_`-]*({'|'.join(FIELDS)})[\s*_`]*:", line, re.I):
            errors.append(f"line {i}: can't read field {line.strip()!r}; write '{m.group(1).capitalize()}:' at the start of the line, no markup")
        elif field and line.strip():
            fields[field] = (fields[field] + " " + line.strip()).strip()  # a field runs up to the next "Field:" line

    start = 0.0
    for sc in scenes:
        f = sc.pop("fields")
        counter = f.get("Counter", "")
        c = re.match(r"(?:(?:Step|Change|Point)\s+)?(\d+)\s+of\s+(\d+)", counter.lstrip("[*`\" "), re.I)
        if counter and not c and counter.strip("[]*`\" ").lower() not in ("none", "-", "n/a"):
            errors.append(f"line {sc['line']}: can't read the Counter of scene {sc['n']} ({counter!r}); write 'Step 1 of 4' or none")
        sc.update({
            "start": start,
            "counter": (int(c.group(1)), int(c.group(2))) if c else None,
            "action": f.get("Action", ""),
            "on_screen": f.get("On screen", ""),
            "narration": f.get("Narration", ""),
            "visual": f.get("Visual", "").strip("[]*` ").lower(),
            "params": f.get("Params", "").strip("`"),
        })
        start += sc["secs"]
    if not scenes and not errors:
        raise SystemExit("no '### Scene N - name - Ns' blocks in the plan's storyboard")
    if style == "quick-tip" and mode in ("howto", "general"):
        # A quick-tip shows no counter (SKILL.md): its action scenes are the steps.
        acts = [sc for sc in scenes if has_action(sc)]
        for k, sc in enumerate(acts, 1):
            sc["counter"] = (k, len(acts))

    formats = list(FORMATS) if mode == "explainer" else ["landscape"]
    # An explainer's "## Formats" wins over the single "## Format: <name> - WxH" line; other modes read only that line,
    # so a howto that keeps the template's "## Formats" section (filled, empty or n/a) still renders one format.
    many = mode == "explainer" and re.search(r"^## Formats\b[^\n]*\n?(.*?)(?=^#|\Z)", text, re.M | re.S)
    source = many or re.search(r"^## Format:(.*)$", text, re.M)
    if source:
        where = f"line {text.count(chr(10), 0, source.start()) + 1}"
        found = [f for f in FORMATS if re.search(rf"\b{f}\b", source.group(1))]
        if not many and "[" in source.group(1):
            errors.append(f"{where}: the '## Format:' line is still the template placeholder; write one format, e.g. '## Format: landscape - 1920x1080'")
        elif not many and len(found) > 1:
            errors.append(f"{where}: '## Format:' names {', '.join(found)}; write one format (an explainer lists several under '## Formats')")
        elif found:
            formats = found
        else:
            errors.append(f"{where}: no format name ({', '.join(FORMATS)}) in {source.group(1).strip()!r}")

    script = re.search(r"^## Narration script\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return {"mode": mode, "style": style, "formats": formats, "scenes": scenes, "errors": errors,
            "script": script.group(1) if script else ""}


def gate_mode(plan: dict) -> str:
    """The rule set: a quick-tip howto or general video is held to the quick-tip limits."""
    return "quick-tip" if plan["style"] == "quick-tip" and plan["mode"] in ("howto", "general") else plan["mode"]


def numbers(text: str) -> set[str]:
    """Digits as spoken: no thousands commas, no sign, no trailing decimal zeros ("2.50" and "2.5" match)."""
    found = re.findall(r"\d+(?:\.\d+)?", re.sub(r"(?<=\d),(?=\d{3})", "", text))
    return {n.rstrip("0").rstrip(".") if "." in n else n for n in found}


def described_gaps(scene: dict) -> list[str]:
    shown, said = scene["on_screen"], scene["narration"]
    labels = re.findall(r"\*\*(.+?)\*\*", shown)
    spoken = said.replace("*", "").lower()
    return sorted(numbers(shown) - numbers(said)) + [f"'{b}'" for b in labels if b.lower() not in spoken]


def body_scenes(scenes: list[dict]) -> list[dict]:
    """The scenes minus any credits, outro or end card: P-end judges the last of these."""
    return [sc for sc in scenes if not re.search(r"outro|credit|end card", sc["name"], re.I)] or scenes


def has_action(scene: dict) -> bool:
    return bool(scene["action"]) and scene["action"].strip("[]*` ").lower() not in ("none", "-", "n/a")


def step_scenes(plan: dict) -> list[dict]:
    return [s for s in plan["scenes"] if s["counter"]]


def check_plan(plan: dict) -> list[tuple[str, bool, str]]:
    if plan["errors"]:
        # The other gates would judge a misread plan, so they wait until it parses.
        return [("P-parse", False, "; ".join(plan["errors"]))]
    mode, scenes, steps = gate_mode(plan), plan["scenes"], step_scenes(plan)
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
        body = body_scenes(scenes)
        ok = "try" in body[-1]["name"].lower()
        results.append(("P-end", ok, f"last scene is {body[-1]['name']!r}" + ("" if ok else "; end on 'Now try it' with a concrete example, not a recap")))

    return results + check_described(scenes)


def check_described(scenes: list[dict]) -> list[tuple[str, bool, str]]:
    if not any(s["on_screen"] for s in scenes):
        return []
    # The outro's credit line ("CC BY 4.0") is a licence notice, not a fact the voice must say.
    gaps = [f"scene {s['n']} missing {', '.join(g)}" for s in body_scenes(scenes) if s["on_screen"] and (g := described_gaps(s))]
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

    body = body_scenes(scenes)
    ok = "recap" in body[-1]["name"].lower()
    results.append(("P-end", ok, f"last scene is {body[-1]['name']!r}" + ("" if ok else "; end on a recap")))
    return results + check_params(plan)


def param_numbers(value) -> list[str]:
    """Every figure in Params, normalised like numbers(): strings too ("40%" reaches the screen as text)."""
    if isinstance(value, dict):
        # lat and lon are map coordinates the plan states, not figures; a model's file name is not a figure either.
        return [n for k, v in value.items() if k not in ("lat", "lon", "model") for n in param_numbers(v)]
    if isinstance(value, list):
        return [n for v in value for n in param_numbers(v)]
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return sorted(numbers(format(value, "f")))  # "f": 1e-05 is spoken 0.00001
    if isinstance(value, str):
        return sorted(numbers(value))
    return []


COUNTRIES = Path(__file__).resolve().parent.parent / "assets" / "scene3d" / "data" / "ne_110m_admin_0_countries.min.geojson"


def country_codes() -> set[str]:
    """The alpha-3 and alpha-2 codes globe.js can find in the bundled Natural Earth file."""
    features = json.loads(COUNTRIES.read_text(encoding="utf-8"))["features"]
    return {f["properties"][k] for f in features for k in ("a3", "a2") if f["properties"].get(k)}


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
            route, country = params.get("route"), params.get("country")
            if not country and not (isinstance(route, list) and len(route) >= 2):
                bad.append(f"scene {s['n']} globe needs Params.country or a Params.route of 2+ places")
            if country and str(country).upper() not in country_codes():
                bad.append(f"scene {s['n']} globe country {country!r} is not an ISO alpha-3 or alpha-2 code in the bundled map")
            for p in route if isinstance(route, list) else []:
                if not (isinstance(p, dict) and all(isinstance(p.get(k), (int, float)) and not isinstance(p.get(k), bool) for k in ("lat", "lon"))):
                    bad.append(f"scene {s['n']} globe route place {p!r} needs {{\"name\", \"lat\", \"lon\"}} with numbers")
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
    mode = gate_mode(plan)
    if mode == "explainer":
        # One chapter per "### " section of the narration script; a script without sections still needs 2-4.
        sections = len(re.findall(r"^### ", plan["script"], re.M))
        ok = len(chapters) == sections if sections else 2 <= len(chapters) <= 4
        return ("P-render", ok, f"{len(chapters)} chapters vs " + (f"{sections} sections in the narration script" if sections else "2-4 sections expected"))
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
    if args.chapters and not plan["errors"]:
        chapters = parse_chapters(args.chapters.read_text(encoding="utf-8"), video_duration(args.video))
        results.append(check_render(plan, chapters))

    for name, ok, msg in results:
        print(f"{name} {'PASS' if ok else 'FAIL'}: {msg}")
    return 0 if all(ok for _, ok, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main())
