---
name: showhow
description: Turn the current project into a narrated instructional video (how to do one task) or a feature update video (what's new in a release) using Hyperframes, or a general video for any process, third-party app, physical task or topic without a codebase (`--mode general`, researching official docs, screenshots and topic images). Steps outside the code (a vendor portal before a connector) work in any mode. 11 styles (teaching and energy), frame-preset themes, Kokoro voices, and a business share post; `/showhow options` lists them. Use when someone says "/showhow", "make a how-to video", "make a tutorial for X", "make a what's new video", "feature update video", "release video for 2.4", "make a video about X", "explain how X works in a video", or wants to show users how something works. Reads the project code, docs and git history directly - no live URL or screen recording needed.
---

# /showhow

Show people how it works, and what's new.

## Invocation dispatch (must happen first)

**Install.** If the input is exactly `install`, don't make a video.
On Windows, run `powershell -NoProfile -ExecutionPolicy Bypass -File <skill-dir>/scripts/install.ps1`, report the result, and stop.
Tell the user to restart their agent app afterwards: a running session keeps the PATH and environment it started with, so `ffmpeg`, `whisper-cli` and `HYPERFRAMES_PYTHON` stay invisible to it.
Elsewhere, say the installer is Windows-only, list what it installs (Node.js LTS, ffmpeg, Python 3.12, uv, Docker Desktop (for `render --docker`), a Python venv for Kokoro voice and MusicGen music (`kokoro-onnx soundfile transformers torch numpy`, pointed to by `HYPERFRAMES_PYTHON`, with the `facebook/musicgen-small` model pre-downloaded), whisper-cpp (`whisper-cli` on PATH), the Hyperframes skills via `npx skills add heygen-com/hyperframes`, then `npx hyperframes browser ensure`), and stop.

**Options.** If the input is exactly `options`, don't make a video: list the 11 styles (one line each, from the Style system tables), the themes (the folder names in `../hyperframes-creative/frame-presets/` next to this skill), and the voices (`npx hyperframes tts --list`), each with the flag that picks it, and stop.

**Model check.** If you are Claude Opus 5.5 and the invocation doesn't ask for the full workflow (`--full`, "use the full showhow"), switch to showhow-slim: read `<skill-dir>/slim.md` (bundled here) and follow it for the rest of this run instead of this file.
Pass along the user's input and pass any other options (`--mode`, `--no-voice`, ...) as plain-language direction.
Tell the user in one line first, e.g. "You're on Opus 5.5, so I'm using /showhow-slim: I build the whole video myself. Say 'use the full showhow' to switch back."
If you are any other model, or can't tell which model you are, skip this check.

Before inspecting the project, parse the complete `/showhow` invocation and decide the mode (see below).

## What this skill does

1. Decides the mode: a **how-to** for one task, a **feature update** for a release, or a **general** video for a task or topic outside the code.
2. Reads the project code, docs and (for updates) git history to find the real flow.
3. Writes a narration script and a step-by-step storyboard.
4. Hands a focused composition brief to Hyperframes.
5. Validates, renders, and writes captions, chapters, a written companion and a share post.

## Modes

| Mode | Use when | The viewer should afterwards |
|---|---|---|
| `howto` | The user names a task or feature: "how to add project knowledge", "tutorial for prompt versions" | Be able to do the task themselves, without the video |
| `update` | The user names a version, release, tag, PR, commit range, or says "what's new" | Know what changed, where to find it, and why it matters to them |
| `general` | The task isn't in this project's code: a process, a third-party app, a physical task ("how to share a calendar in Outlook"), or a topic without steps ("how a train gets its power") | Be able to do the task themselves, without the video, or explain the topic |

Infer the mode from the input.
`general` follows `howto` everywhere (rubric, pattern, length limits, styles) except where [references/general.md](references/general.md) says otherwise; read it before Step 1.
Any mode can mix in **outside steps** that this code can't show, like creating an API token in Atlassian before connecting Confluence: tag them `outside` and gather, capture and rebuild them with general.md (official docs, screenshots of the real pages, fictional data).
If the input names a task and a version ("how to use the new project knowledge in 2.4"), use `howto` for that task and mention the version in the intro.
If it is still unclear, ask one question.

## Parsing the invocation

```
/showhow how to add knowledge to a project
/showhow --mode update 2.4.0
/showhow what's new since v2.3.0 --style release
/showhow how to restore a prompt version --format vertical --no-music
/showhow --mode general how to book a meeting room (steps pasted below)
/showhow --mode general how a train gets its power --style cinematic --theme bold-poster --voice am_michael
/showhow install
/showhow options
```

| Option | Values | Default |
|---|---|---|
| `--mode` | `howto`, `update`, `general` | inferred |
| `--style` (alias `--tone`) | preset or freeform description | `clean` for howto and general, `release` for update |
| `--format` | `landscape`, `vertical`, `square` | `landscape` |
| `--duration` | seconds | set by the narration (see limits below) |
| `--audience` | freeform, e.g. "new users", "admins" | inferred from the feature |
| `--no-voice` | flag | narration on |
| `--no-captions` | flag | burned-in captions on |
| `--no-music` | flag | quiet music bed on |
| `--no-sfx` | flag | click and typing sounds on |
| `--title` | string | inferred |
| `--theme` | a frame preset name | product theme; general: picked per topic |
| `--voice` | a Kokoro voice id | `af_heart` |

Narration is **on by default** because an instructional video without a voice or captions does not teach.
With `--no-voice`, burned-in step captions carry the whole explanation and every step holds longer.
Voice uses Kokoro via `npx hyperframes tts` (single provider, English).
If the user asks for another language, check `npx hyperframes tts --list` for a matching voice; if there is none, say so and offer English narration with captions in the requested language.

---

## Output directory

Output goes to the user's Downloads folder (`~/Downloads`; on Windows `%USERPROFILE%\Downloads`), in a folder named after the skill and the video:

```
~/Downloads/showhow-connect-confluence/
  connect-confluence.mp4
  connect-confluence.jpg
```

- `<video-name>`: a short kebab-case slug of the video's title, 2-5 words (`connect-confluence`, `whats-new-2-4-0`).
- `<output-dir>` = `~/Downloads/<skill-name>-<video-name>/`, where `<skill-name>` is this skill's name (`showhow`).
- The video is `<video-name>.mp4` and its poster `<video-name>.jpg`; the other files keep their fixed names.
- If the folder already exists, append the run's timestamp: `showhow-connect-confluence-2026-05-04-143022/`.

Decide the video name after the plan (Step 2) and use it for every output path in that run.

## Windows: tools missing after install

If a command can't find `ffmpeg`, `uv` or `whisper-cli`, or `HYPERFRAMES_PYTHON` is empty, the session started before the installer ran.
Don't reinstall: prefix Git Bash commands with the user-level values the installer set:

```bash
export PATH="$(cygpath "$LOCALAPPDATA")/Microsoft/WinGet/Links:$HOME/.local/whisper-cpp/Release:$HOME/.local/bin:$PATH"
export HYPERFRAMES_PYTHON="$(powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('HYPERFRAMES_PYTHON','User')" | tr -d '
')"
```

## Skill directory

`<skill-dir>` is the directory containing this `SKILL.md`.
Claude Code prints it as "Base directory for this skill" when the skill loads; for other agents it's wherever the skill was installed.
Bundled assets are under `<skill-dir>/assets/` and scripts under `<skill-dir>/scripts/`.
Don't guess an install path.

---

## Step 1: Inspect the project

**Read:** [references/step-1-inspect.md](references/step-1-inspect.md)

Find the real flow in the code and docs (howto), or the real changes in git history and release notes (update).
For outside steps, and every step in `general` mode, gather the facts from the user's material, official docs and screenshots of the real pages instead: [references/general.md](references/general.md).

**Gate:** You can answer every question in the rubric for your mode.

---

## Step 2: Script and storyboard

**Read:** [references/step-2-plan.md](references/step-2-plan.md)

Write `<output-dir>/showhow-plan.md`: the goal, the audience, the narration script, and a scene-by-scene storyboard with on-screen actions, highlights, captions and timing.

**Gate:** `<output-dir>/showhow-plan.md` exists with a full script and storyboard.
Every step names the exact UI element the viewer acts on.
The duration fits the mode limits.

---

## Step 3: Hand off to Hyperframes

**Read:** The Hyperframes domain skills - `hyperframes-core`, `hyperframes-animation`, `hyperframes-creative`, `hyperframes-keyframes`, `hyperframes-cli`, and `media-use` for TTS and captions.
/showhow is its own workflow: do not enter the `hyperframes` entry-point intent interview or route into its generic promo, explainer or launch-video workflows.
**Read:** [references/step-3-compose.md](references/step-3-compose.md)
**Read:** [references/audio.md](references/audio.md)

Generate the narration, write the composition brief, and use Hyperframes to build the video in `<output-dir>/composition/`.

`/showhow` owns the teaching content: mode, audience, steps, script, what to highlight, captions, style and audio levels.
Hyperframes owns the composition structure, animation mechanics, runtime choices, linting and render workflow.

**Gate:** `npx hyperframes check` passes with zero errors inside `<output-dir>/composition/`.

---

## Step 4: Validate, render, and deliver

**Read:** [references/step-4-deliver.md](references/step-4-deliver.md)

Render `<output-dir>/<video-name>.mp4`, bake a poster into frame 0 (`<video-name>.jpg`), and write `captions.srt`, `chapters.txt`, `showhow.md` (the written companion) and `share-copy.md` (a business post to share the video, in the user's voice when `~/VOICE.md` exists).

**Gate:** `<video-name>.mp4`, `<video-name>.jpg`, `captions.srt`, `chapters.txt`, `showhow.md` and `share-copy.md` exist.

---

## Style system

Eleven styles, usable in every mode.
Each changes narration wording, pacing, typography and transitions; length always follows the mode limits below.
Presets are defaults, not limits; freeform direction ("calm like Apple support videos") refines them.

Full definitions and the rules every style follows: [references/tones.md](references/tones.md)

| Style | Feel | Best for |
|---|---|---|
| `clean` | Neutral, precise, product-docs | Most how-tos; admins and power users |
| `friendly` | Warm, encouraging, first-time-user | Onboarding, non-technical audiences |
| `release` | High energy around clear demos: punchy hook, beat-locked change cards, full SFX palette | Feature updates and release videos |
| `quick-tip` | One task, as fast as it can still be followed | Single small tricks, shortcuts, 20-40s |
| `playful`, `polished`, `yc-parody`, `chaotic`, `deadpan`, `cinematic`, `app-store` | The energy tones, at teaching length | When a video should have more personality |

**Themes.** `--theme <preset>` dresses any video in one of the frame presets from `../hyperframes-creative/frame-presets/` (title cards, captions, step cards, counter); rebuilt product screens keep their own look.
Default: the product's theme (howto, update), or a preset picked for the topic (general, see general.md).

**Voices.** `--voice <id>` picks any Kokoro voice from `npx hyperframes tts --list` (default `af_heart`); use it for every scene.

---

## Teaching laws

These apply to every video regardless of mode or style.

**One job per video.** A how-to teaches one task. An update covers one release. If the input covers more, split it and say so.

**Say the outcome first.** Within the first 5 seconds the viewer knows what they will be able to do (howto) or what is new (update).

**Show the real product.** Every step is shown on the actual UI, rebuilt from the project's own components, styles and copy. No abstract diagrams where a real screen exists.
Outside steps (and `general` mode) show screens rebuilt from real screenshots, the user's photos, and invented step visuals only where nothing real exists (references/general.md).

**Point before acting.** Before every click or keystroke, the target is visible and highlighted (ring, spotlight or zoom), and the narration names it by its on-screen label. Then the action happens, then the result is visible.

**One action per step.** A step is one click, one typed value, or one choice. The screen label in the narration matches the UI text exactly, including capitalization.

**Hold the result.** After each step, the result stays on screen until the narration for it has finished plus about 0.5s. Never cut away mid-explanation.

**Always oriented.** Show a step counter ("Step 2 of 4") in howto mode, or a change counter ("2 of 3") in update mode, and keep it in the same place.

**Captions match the voice.** Burned-in captions show the narration verbatim, one short phrase at a time, never covering the highlighted target.

**Plain words.** No marketing language ("seamless", "streamline", "powerful") and no invented claims. Use the product's own labels and the release's real changes.

**Readable.** Every on-screen label holds at least 1.5s settled; a sentence about 0.35s per word. Zooms and pans are slow enough to follow (0.6-1.0s).

**Pattern (howto):**
```
Outcome (3-5s) -> Before you start (0-5s) -> Steps 1..N (6-15s each) -> Result (3-6s) -> Recap (3-5s)
```

**Pattern (update):**
```
Title: what's new in <version> (3-5s) -> Change 1..N: what / where / show / why (10-20s each) -> How to get it (3-5s)
```

**Length limits:**

| Mode / style | Target | Hard limit |
|---|---|---|
| `howto` | 45-120s | 180s; split into parts beyond that |
| `howto` + `quick-tip` | 20-40s | 60s |
| `update` | 30-90s, 2-5 changes | 120s; pick the top 5 user-visible changes |

Adapt the patterns.
Skip "Before you start" when there are no prerequisites.
