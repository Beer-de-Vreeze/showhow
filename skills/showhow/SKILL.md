---
name: showhow
description: Turn a project into a narrated how-to video (one task), a feature update video (what's new in a release), or a general video for a process, third-party app, physical task or topic outside the code, with captions, chapters, a written companion and a share post, rendered with Hyperframes. Reads the project's code, docs and git history directly; no screen recording needed. Use when someone says "/showhow", "make a how-to video", "make a tutorial for X", "what's new video", "release video for 2.4", "make a video about X", or wants to show users how something works.
---

# /showhow

Show people how it works, and what's new.
It should feel like a good product support video: calm, exact, and easy to follow the first time.

Usage: `/showhow [task, release or topic] [options]`.
Options (flags or plain language):

| Option | Default |
|---|---|
| `--mode howto\|update\|general\|explainer` | inferred: a task -> `howto`; a version, tag, PR, range or "what's new" -> `update`; a task this project's code can't show (a process, a third-party app, a physical task) -> `general`; a topic or concept ("how X works", "why Y") or a pasted script -> `explainer` |
| `--style <name>` (alias `--tone`; see Styles) or freeform | `clean` for howto and general, `release` for update, `friendly` for explainer |
| `--format landscape\|vertical\|square` | landscape (1920x1080; vertical 1080x1920, square 1080x1080), 30fps; `--format all` or a comma list (`landscape,vertical`) renders several; explainer defaults to all three |
| `--audience <who>` | inferred |
| `--theme <frame preset>` (`assets/frame-presets/` here, then `../hyperframes/assets/frame-presets/`) | product theme; general: the preset that fits the topic; explainer: `showhow` |
| `--brand <name>` (a local brand kit in `~/.showhow/brands/<name>/`; `references/brand-kits.md`) | none |
| `--voice <Kokoro id>` (`npx hyperframes tts --list`) | `af_heart` |
| `--title <text>` | inferred |
| `--duration <seconds>` | none: the narration sets the length; a typed value is the target the script is written to, within the limits below |
| `--no-voice`, `--no-captions`, `--no-sfx` | all on |
| `--music` / `--no-music` | music bed off for `clean`, `friendly`, `quick-tip`, on for `release` and `explainer`; `--no-music` wins |

**Theme lookup order.**
This is the one place the video's theme is resolved; the other files point here.
The first line that applies wins.

1. Typed flags: `--theme <name>` (the folder `<name>` in `assets/frame-presets/` here, else in `../hyperframes/assets/frame-presets/`) replaces the whole theme; `--voice` and `--music` typed in this run beat the kit's `voice` and `music`.
2. `--brand <name>`: the kit `~/.showhow/brands/<name>/` (`references/brand-kits.md`); its check runs first, and a failing kit stops the run naming what is missing.
3. House-style defaults: `brand: <name>` (or a flag) under `## Defaults` in `~/.showhow/verdicts.md`.
4. The product's own theme (howto and update).
5. The mode default: `showhow` for explainer; for general, the preset that fits the topic.

**Other inputs.**
`brand <name> <repo path or URL>`: make no video; create a brand kit (`references/brand-kits.md`) and stop.
`install`: on Windows run `powershell -NoProfile -ExecutionPolicy Bypass -File <skill-dir>/scripts/install.ps1`, report the result, tell the user to restart their agent app (a running session keeps its old PATH), and stop; elsewhere say the installer is Windows-only, list what README.md "Install" lists, and stop.
`options`: list the modes (`howto`, `update`, `general`, `explainer`), the styles, the explainer visual types (the Visual menu in `references/explainer.md`, with the `scene3d` kinds `machine`, `globe` and `hero-number`), the themes (folder names in `assets/frame-presets/` here, `showhow` first, then those in `../hyperframes/assets/frame-presets/`), the brand kits in `~/.showhow/brands/` and the voices, each with its flag, and stop.
`learn <output-dir>`: make no video; record lessons from that run (`references/house-style.md`, "`/showhow learn`") and stop.

`<skill-dir>` is the folder holding this file (Claude Code prints it as "Base directory for this skill"); bundled files are in `assets/` and `scripts/`.
Paths starting `../hyperframes/` here and in `references/` mean the installed `hyperframes` skill next to this one (for example `~/.claude/skills/hyperframes/`); when this skill runs from a repo checkout, that sibling is not in the checkout, so read it from the installed skills folder.
If `ffmpeg`, `uv` or `whisper-cli` is missing, or `HYPERFRAMES_PYTHON` is empty, the session started before the installer ran: ask the user to restart the app; don't reinstall.

**Output.** First decide `<video-name>`: a 2-5 word kebab-case slug of the video's title (`connect-confluence`, `whats-new-2-4-0`).
Write everything to `~/Downloads/showhow-<video-name>/` (Windows: `%USERPROFILE%\Downloads`), the `<output-dir>`; if it exists, append `-YYYY-MM-DD-HHmmss`.
Intermediate files go in `<output-dir>/work/`, the Hyperframes project in `<output-dir>/composition/`; run every command below from `<output-dir>` unless it says otherwise.
Name the video `<video-name>.mp4` and the poster `<video-name>.jpg` (with several formats, `<video-name>-<format>.mp4` and `.jpg`; the render wrapper writes these names); the other files keep their fixed names.

**House style.** Before anything else, read `~/.showhow/verdicts.md` and `~/.showhow/edits.md` if they exist (`references/house-style.md`): typed flags beat its `## Defaults`, which beat the defaults above; its `## Always` and `## Never` rules join the laws below but never override a teaching law, accessibility or "Show the real product".

## 1. Inspect

**howto:** trace the task through the code the way a user does it: the entry point (route, sidebar item, menu), every control they touch in order with its **exact on-screen label**, what visibly happens after each action, prerequisites (roles, settings, data), the one mistake or error a user is most likely to hit and how they recover, and where the result lives afterwards.
More than about 8 actions means two tasks: propose a split and make part 1.

**Outside steps (any mode) and general:** a step this code can't show (an API token made in Atlassian before connecting Confluence, a process, a physical task) is tagged `outside`; `general` is a video of only outside steps.
Read `references/general.md` and follow it.
In short:
- Facts come from the user's material, then the vendor's official docs, then screenshots of the real pages in your browser (never sign in or commit a real change yourself; ask the user to sign in), then only well-established knowledge.
  Never invent a label: describe it and list it as unverified.
- Rebuild screens from those screenshots with fictional data; never rebuild beta or preview screens.
  A rebuilt third-party screen shows "Shown as of <Mon YYYY>", and the outro credit line adds "<Product> is a trademark of <owner>. Not affiliated."
- Topic pictures: the user's, then `media-use resolve --type image`, then freely licensed photos (license in `work/sources.md`, attribution in `credits.txt` and on the outro credit line); invented step cards or diagrams only where nothing real exists, and a different picture for every point.
- A mechanism gets a schematic diagram; when the shape itself is the point (parts that fit together), one schematic 3D object in three.js via Hyperframes (`../hyperframes/references/types/3d.md`); never 3D for UI, screens or charts.
- Physical tasks: ask for first-person, hands-visible photos.
- Everything else (shape, laws, sound, deliverables) works as for howto; a topic without steps uses the points shape in `references/general.md`.

**explainer:** a topic or a pasted script, not a task.
Read `references/explainer.md` and follow it; it reuses `references/general.md` for sourcing, licensing, schematics, chart honesty and the design system, and replaces the step shape.
In short: a pasted script is narrated word for word; a topic gets a drafted, sourced script and the run stops for approval; a fact you can't source is written `[NEED: <what>]`.

**update:** pin the release range (tags, version-bump commits, CHANGELOG; state the range you chose).
Read the team's own release notes first (CHANGELOG, release commit subjects, PR titles, features/status docs), then the commits in the range.
Keep only user-visible changes, rank them, keep 2-5, and trace each into the UI like a howto: what it is, where it lives, one or two actions that show it, why it matters to the viewer.

**Always:** read the styles: exact colors and fonts of the product's brand or default theme (the one its `:root` defines, or that its theme picker marks as default), never a test fixture's or dev build's; write down the theme id with its background and accent values.
Read the README and product docs (the product's own names for things) and the UI copy.

**Nothing secret or personal leaves this step.** Don't open `.env` files, keys, credentials or anything `.gitignore` excludes for that reason (`references/step-1-inspect.md`, "What to skip").
No secrets, tokens, tenant or client IDs, internal hostnames, real customer, colleague or user names, emails, or commit authors in anything you produce; use plausible fictional stand-ins on screen and list them in the plan.

**Gate:** write the answers to the mode's rubric (`references/step-1-inspect.md`) to `work/inspect.md`.

## 2. Script and plan

Write `showhow-plan.md` using the template in `references/step-2-plan.md`, headings and storyboard fields exactly as given: the scripts below parse it.

**Script first; the voice sets the pace.**
Second person, present tense, 8-16 words per sentence, one sentence per action plus at most one of why.
Name controls by their exact label.
No "in this video", "simply", "just", "seamless", "powerful".
Plan about 2.5 words per second.

**Say the result:** every result that matters is spoken ("the file now appears under **Knowledge**"), not only shown.

**Name the likely mistake:** at the step where it happens, one line on the error the user is most likely to hit and how to recover ("If **Save** stays grey, fill in the name first"); skip it when Step 1 found none.

**Shape (howto):** Outcome (3-5s) -> Before you start (only if needed) -> Steps, one action each (6-15s) -> Result (3-6s) -> Now try it, with a concrete example (3-5s).
About 2s of silent hold at each subtask boundary (the end of a group of steps that finishes one part of the task).
Target 45-120s, hard limit 180s (split into parts beyond that); `quick-tip` 20-40s (limit 60s), 1-3 actions, ending on the result.

**Shape (update):** hook: the most visual change already moving with "What's new in [version]" as on-screen text within 3s (3-5s) -> each change: what / where / show / why (10-20s) -> how to get it (3-5s).
Target 30-90s, hard limit 120s.
Every promise on a change card is pictured in its demo, and each change opens on a different screen or crop; a "Fixed" or redesigned screen may morph from the previous release's real screen into the new one (before/after, `references/tones.md`).

**Shape (explainer):** Outcome -> Name the parts -> one scene per voiced sentence, each with one `Visual:`, grouped in sections -> Recap (`references/explainer.md`).
No step counter; chapters per section.
Target 60-120s, hard limit 180s.

**Gate:** `uv run --project <skill-dir>/scripts <skill-dir>/scripts/plan_gates.py showhow-plan.md` passes (first P-parse: every scene heading and field reads as in the template, or the failure names the line; explainer: P-need, P-visual, P-time, P-end, P-params; every mode: including P-described: every number and bold label in a scene's `On screen:` line is also spoken in that scene's narration); fix the plan, never argue a FAIL.

## Teaching laws

- **One job per video.** One task, or one release.
- **Outcome first.** Within 5 seconds the viewer knows what they'll be able to do, or what's new.
- **Show the real product.** Render the project's own components with fictional data, or screenshot the running app (dev server, fictional data, never production), or rebuild the screen from its styles and exact copy - in that order of preference.
  No abstract filler where a real screen exists.
  Reuse the product's own icons and logos (often inline SVG in shared components), never letter badges.
- **State carries forward.** What a step creates stays visible on later screens: the attached file in the sent message, the chosen model in the reply header.
- **Orient, point, act, result.** For every step: show enough of the screen to know where you are; highlight the one target (ring, spotlight or zoom) while the voice names its label; move the cursor and click or type; hold the result until the narration ends plus 0.5-1.0s.
- **Same screen, same camera.** Between steps on one screen, zoom and pan; fade or cut only when the screen changes.
- **Always oriented.** "Step 2 of 4" (howto) or "2 of 3" (update), same place every time; not in a `quick-tip`, and not on a hook or title before the first step.
- **Readable.** Anything the voice names is legible at the chosen zoom (zoom 1.5-2.5x on small controls); on-screen labels hold 1.5s settled; camera moves take 0.6-1.0s.
- **Captions match the voice** verbatim, one phrase at a time, at most 37 characters per line and 2 lines (3 on vertical), each cue on screen at least 0.3s per word, never over the highlight.
- **Works muted.** The first 3 seconds and every title or change card make sense with the sound off.
  A hook with music and no voice carries its point as on-screen text, and the first voiced line says what the video is about.
- **No flashing.** Nothing flashes more than three times in any second, in any style: no white or black flash frames, no strobe (WCAG 2.3.1).
- **Every frame accurate.** A wrong label or wrong order is the worst bug a how-to can ship.
- **Name the likely mistake** at the step where it happens, with the way out (Step 2).
- **Grounded claims.** Anything the video says the product does, its names and its numbers, must appear in the project (for outside steps: in the user's material, the official docs or your screenshots).
  Fictional demo data (names, files, replies) is fine and listed in the plan; invented capabilities are not.

## Styles

| Style | Feel | Pacing / transitions |
|---|---|---|
| `clean` | Neutral, precise, product docs; no music unless `--music` | 6-12s per step; cuts between screens |
| `friendly` | Warm, patient, explains why in half a sentence | 8-15s per step, max 5 steps; soft fades |
| `release` | High energy around clear demos: punchy hook, change cards with "New"/"Fixed" tags, beat-locked reveals; the version slam may be the one 3D moment (a WebGL block, `../hyperframes/references/types/3d.md`), the changes stay on the flat real UI; "You can now..." | 10-20s per change; fast slides/zooms between changes, calm demos inside |
| `quick-tip` | One trick, 1-3 actions | 5-8s per action; cuts, no recap |

All four work in every mode; freeform direction ("calm like Apple support videos") refines them; `references/tones.md` has the full definitions.

## Sound

The voice leads: one narration clip per scene, and each clip sets its scene's length (`references/step-3-compose.md`, "Generate the narration first").
A music bed stays at least 20 dB below the voice (WCAG 1.4.7): ducked under every narration clip to the level `references/audio.md` measures, and never cut off abruptly.
Music is a bundled track, then an Incompetech track (CC BY), never generated (`references/audio.md`, Music).
SFX confirm visible actions in how-tos and score the hook, cards and outro in updates (`references/step-2-plan.md`, "Audio planning"); none masks a narrated word.

## 3. Build, check, render

Before building any chrome (title, cards, counters, caption plate, outro), read `references/design-floor.md` and follow it; it covers the chrome only, rebuilt screens keep the product's look, and a `--theme` preset overrides its Refuse list.
Build by `references/step-3-compose.md`: narration and caption timing, the composition brief, staging, the kit (rings and the cursor placed by element), baked rings for screenshot videos, `fromTo` tweens, overlays and the outro credit line.
Check and render by `references/step-4-deliver.md`, in this order:

1. `npx hyperframes check` in `composition/` passes with zero errors, contrast included.
2. `npx hyperframes snapshot` at every highlight, result and mid-transition; describe each still in one sentence before judging it.
3. `npx hyperframes preview`: give the user the URL and ask them to watch for wrong labels or order; render without waiting, and redo it if they find one.
   In `explainer` mode, write the preview stills first (the render command plus `--stills`) and wait for approval (`references/explainer.md`, "Stop 2: preview stills").
4. Write `captions.srt`, then render with the wrapper, never `npx hyperframes render` directly:
   `uv run --project <skill-dir>/scripts <skill-dir>/scripts/render.py composition <video-name>.mp4 --work work --plan showhow-plan.md [-- --docker]`.
5. Pull frames from every mp4 at each ring and result moment; snapshots alone don't prove the render:
   `uv run --project <skill-dir>/scripts <skill-dir>/scripts/frame_sheet.py <mp4> --overlays work/rings.overlays.json -o work/check.jpg`.

Keep creation and rendering local; publishing or uploading needs a separate explicit request.

## 4. Deliver

Deliver by `references/step-4-deliver.md`: the poster (the wrapper writes it), `captions.srt`, `chapters.txt`, the gates, `showhow.md`, `credits.txt`, `share-copy.md` and the report to the user.

- **Gates:** run both on every mp4 the wrapper wrote; fix any FAIL and re-render, never argue it, and quote every line in the report:
  `uv run --project <skill-dir>/scripts <skill-dir>/scripts/video_gates.py <mp4> --srt captions.srt` (G-blank, G-captions, G-end) and
  `uv run --project <skill-dir>/scripts <skill-dir>/scripts/plan_gates.py showhow-plan.md --chapters chapters.txt --video <mp4>` (P-render).
- **Offer a brand kit.**
  A howto or update run on a repo, with no `--brand` kit in play and no kit of that name in `~/.showhow/brands/`, ends by offering once to save the theme it read as a kit (`references/brand-kits.md`); one question, and a no is final for that run.
- **Learn from the feedback.** When the user asks for changes, fix them and record the lasting preferences by `references/house-style.md`, showing the added lines as a diff.
