"""Self-check for the plan gates. Run:
  uv run --project <skill-dir>/scripts python <skill-dir>/scripts/test_plan_gates.py
"""

from plan_gates import check_plan, check_render, parse_chapters, parse_plan


def scene(n: int, name: str, secs: float, counter: str = "none", action: str = "none", on_screen: str = "", narration: str = "", visual: str = "", params: str = "") -> str:
    extra = (f"On screen: {on_screen}\n" if on_screen else "") + (f"Narration: {narration}\n" if narration else "") + (f"Visual: {visual}\n" if visual else "") + (f"Params: {params}\n" if params else "")
    return f"### Scene {n} - {name} - {secs}s\nCounter: {counter}\nAction: {action}\nResult: x\n{extra}\n"


def plan(mode: str, scenes: str, preset: str = "clean") -> str:
    return f"# Showhow Plan: t\n\n## Mode\n{mode} - task\n\n## Style\n- Preset: {preset}\n\n## Storyboard\n\n{scenes}## Chapters\n00:00 x\n"


def verdicts(text: str) -> dict:
    return {name: ok for name, ok, _ in check_plan(parse_plan(text))}


def main() -> None:
    good = plan("howto", scene(1, "Outcome", 4) + scene(2, "Open settings", 8, "Step 1 of 2", "click **Settings**")
                + scene(3, "Save", 7, "Step 2 of 2", "click **Save**") + scene(4, "Now try it", 4))
    assert all(verdicts(good).values()), check_plan(parse_plan(good))

    # The connect-confluence run as it was rendered: bundled actions, a 2s step, ends on a recap.
    bad = plan("howto", scene(1, "Outcome", 10)
               + scene(2, "Account", 5, "Step 2 of 10", "click **Profile picture**, then **Manage account**")
               + scene(3, "Token", 2, "Step 4 of 10", "click **Create API token**")
               + scene(4, "Recap", 9))
    v = verdicts(bad)
    assert not v["P-steps"] and not v["P-action"] and not v["P-time"] and not v["P-end"], v

    # A step may span two scenes (same counter); its time adds up.
    split = plan("howto", scene(1, "Outcome", 4) + scene(2, "Point", 3, "Step 1 of 1", "click **New**")
                 + scene(3, "Result", 3.5, "Step 1 of 1") + scene(4, "Now try it", 4))
    assert all(verdicts(split).values()), check_plan(parse_plan(split))

    # quick-tip: no counter (SKILL.md), its actions are the steps, 5s each, ends on the result.
    tip = plan("howto", scene(1, "Tip", 5, "none", "press **Ctrl+K**") + scene(2, "Result", 3), preset="quick-tip")
    assert parse_plan(tip)["mode"] == "quick-tip" and all(verdicts(tip).values()), check_plan(parse_plan(tip))

    # update: 2-5 changes of 10s+, counters written "1 of 2" or "Change 1 of 2".
    upd = plan("update", scene(1, "Hook", 4) + scene(2, "Search", 12, "Change 1 of 2", "type \"invoice\"")
               + scene(3, "Export", 6, "2 of 2", "click **Export**") + scene(4, "Get it", 4), preset="release")
    assert verdicts(upd) == {"P-steps": True, "P-action": True, "P-time": False}, verdicts(upd)

    # A credits outro after "Now try it" is fine; a general topic video (no actions) ends on its recap.
    outro = plan("howto", scene(1, "Outcome", 4) + scene(2, "Save", 7, "Step 1 of 1", "click **Save**")
                 + scene(3, "Now try it", 4) + scene(4, "Outro", 3))
    assert verdicts(outro)["P-end"], check_plan(parse_plan(outro))
    topic = plan("general", scene(1, "Outcome", 4) + scene(2, "Wire", 9, "Point 1 of 2") + scene(3, "Motor", 9, "2 of 2")
                 + scene(4, "Recap", 5))
    assert all(verdicts(topic).values()), check_plan(parse_plan(topic))

    # Rendered chapters: the real connect-confluence chapters.txt (84.5s video).
    chapters = parse_chapters(
        "00:00 Connect Confluence to AI Workbench\n00:10 Step 1: Log in to Confluence\n00:17 Step 2: Profile picture, Manage account\n"
        "00:22 Step 3: Security, Create and manage API tokens\n00:27 Step 4: Create API token\n00:29 Step 5: Name, expiry date, Create\n"
        "00:35 Step 6: Copy to clipboard\n00:40 Step 7: Settings, Connections & tools, MCP Servers\n"
        "00:48 Step 8: Atlassian Confluence (UVX), Configure my settings\n00:54 Step 9: Confluence email as username, token, save\n"
        "01:06 Step 10: Enabled for me, Connect\n01:11 Result: Connected\n01:15 Recap\n", 84.5)
    assert chapters[4] == ("Step 4: Create API token", 2) and abs(chapters[-1][1] - 9.5) < 1e-9, chapters
    name, ok, msg = check_render(parse_plan(good), chapters)
    assert name == "P-render" and not ok and "10 rendered steps vs 2 planned" in msg and "'Step 4: Create API token' 2s" in msg, msg

    # P-described: on-screen numbers and bold labels must be spoken in the same scene (WCAG 1.2.5).
    spoken = plan("howto", scene(1, "Outcome", 4, on_screen="**Export**, 40×", narration="click **Export** to speed it up 40 times"))
    assert verdicts(spoken)["P-described"], check_plan(parse_plan(spoken))
    silent = plan("howto", scene(1, "Outcome", 4) + scene(2, "Heat", 5, on_screen="1,700 °C", narration="it gets very hot"))
    name, ok, msg = [r for r in check_plan(parse_plan(silent)) if r[0] == "P-described"][0]
    assert not ok and "scene 2" in msg and "1700" in msg, msg
    # Backwards compatibility: no On screen: field means nothing to check (existing plans above).
    assert "P-described" not in verdicts(good)

    # explainer: one visual per voiced scene, no counters, a recap at the end, 180s limit.
    def expl(secs: float = 18, **over) -> str:
        sc = [("Outcome", "card"), ("Name the parts", "photo"), ("Air in", "flow"), ("Thrust", "chart"), ("Recap", "card")]
        return plan("explainer", "".join(scene(i, n, secs, narration=over.get(n, f"Line {i}."), visual=over.get("v" + n, v))
                                         for i, (n, v) in enumerate(sc, 1)) + over.get("tail", ""), preset="friendly")
    good_e = expl()
    assert all(verdicts(good_e).values()) and "P-steps" not in verdicts(good_e), check_plan(parse_plan(good_e))
    assert not verdicts(expl(Thrust="It started in [NEED: launch year]."))["P-need"]
    assert not verdicts(expl(vThrust=""))["P-visual"]
    name, ok, msg = [r for r in check_plan(parse_plan(expl(vThrust="hologram"))) if r[0] == "P-visual"][0]
    assert not ok and "hologram" in msg, msg
    assert not verdicts(expl(38))["P-time"]
    name, ok, msg = [r for r in check_plan(parse_plan(expl(30))) if r[0] == "P-time"][0]
    assert ok and "outside 60-120s" in msg, msg
    assert not verdicts(expl().replace("Recap", "Wrap-up"))["P-end"]
    assert verdicts(expl() + scene(6, "Outro", 3))["P-end"]
    # The template's empty "Narration:" on a silent outro must not swallow the next line as narration.
    silent = expl() + "### Scene 6 - Outro - 3s\nNarration:\nOn screen: The end\nAudio: music\n\n"
    assert parse_plan(silent)["scenes"][-1]["narration"] == "" and verdicts(silent)["P-visual"], check_plan(parse_plan(silent))

    # 2D motion styles: stroke-reveal is a known visual; parallax is for the first scene only.
    assert verdicts(expl(vThrust="stroke-reveal"))["P-visual"]
    for style in ("kinetic-type", "data-anim", "morph", "flat-scene"):
        assert verdicts(expl(vThrust=style))["P-visual"], style
    name, ok, msg = [r for r in check_plan(parse_plan(expl(vThrust="parallax"))) if r[0] == "P-visual"][0]
    assert not ok and "scene 4" in msg and "parallax" in msg, msg
    assert verdicts(expl(vOutcome="parallax"))["P-visual"]

    # scene3d: every number in Params is spoken (spec #14); Params.kind is known or a model replaces it.
    def s3d(params: str) -> str:
        return expl(Thrust="The compressor has 12 stages.", vThrust="scene3d").replace(
            "Visual: scene3d\n", f"Visual: scene3d\nParams: {params}\n")
    assert all(verdicts(s3d('{"kind": "machine", "stages": 12}')).values()), check_plan(parse_plan(s3d('{"kind": "machine", "stages": 12}')))
    name, ok, msg = [r for r in check_plan(parse_plan(s3d('{"kind": "machine", "stages": 14}'))) if r[0] == "P-params"][0]
    assert not ok and "14" in msg, msg
    name, ok, msg = [r for r in check_plan(parse_plan(s3d('{"kind": "volcano"}'))) if r[0] == "P-params"][0]
    assert not ok and "volcano" in msg, msg

    # Numbers written as strings are checked too ("40%" and "2,500" reach the screen through hero-number), signs and
    # float spelling match the narration's, and a model file name's digits are not figures.
    def said(narration: str, params: str) -> tuple[bool, str]:
        text = expl(Thrust=narration, vThrust="scene3d").replace("Visual: scene3d\n", f"Visual: scene3d\nParams: {params}\n")
        return [r for r in check_plan(parse_plan(text)) if r[0] == "P-params"][0][1:]
    ok, msg = said("Most of it is lost.", '{"kind": "hero-number", "value": "40%"}')
    assert not ok and "40" in msg, msg
    assert not said("It is very old.", '{"kind": "hero-number", "value": "2,500"}')[0]
    assert said("Over 2,500 years old.", '{"kind": "hero-number", "value": "2,500"}')[0]
    assert said("It runs at -40 degrees.", '{"kind": "hero-number", "value": -40}')[0]
    assert said("It runs at -40 degrees.", '{"kind": "hero-number", "value": "-40°C"}')[0]
    assert said("It costs 2.5 euros.", '{"kind": "hero-number", "value": 2.50}')[0]
    assert said("It costs 2.50 euros.", '{"kind": "hero-number", "value": 2.5}')[0]
    assert said("A gap of 0.00001 metres.", '{"kind": "hero-number", "value": 1e-05}')[0]
    assert said("A gearbox.", '{"model": "gear-v2.glb"}')[0]

    # globe kind needs a country or a route of 2+ places (spec #14); route coordinates are not narration numbers.
    def p_params(params: str) -> tuple[bool, str]:
        return [r for r in check_plan(parse_plan(s3d(params))) if r[0] == "P-params"][0][1:]
    ok, msg = p_params('{"kind": "globe", "route": []}')
    assert not ok and "globe" in msg, msg
    assert p_params('{"kind": "globe", "country": "BRA"}')[0]
    assert p_params('{"kind": "globe", "route": [{"name": "A", "lat": 37.39, "lon": -5.98}, {"name": "B", "lat": -22.91, "lon": -43.17}]}')[0]
    assert not p_params('{"kind": "globe", "route": [{"name": "A", "lat": 1, "lon": 2}]}')[0]

    for broken in ("no mode here", "## Mode\nhowto\n\n## Storyboard\nnothing\n"):
        try:
            parse_plan(broken)
        except SystemExit:
            continue
        raise AssertionError(f"expected SystemExit for {broken!r}")
    print("ok")


if __name__ == "__main__":
    main()
