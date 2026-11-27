# showhow

**Turn your project into a narrated how-to or what's-new video, straight from the code.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agent skill](https://img.shields.io/badge/agent-skill-black.svg)](https://skills.sh)
[![Built with Hyperframes](https://img.shields.io/badge/built%20with-Hyperframes-ff5a36.svg)](https://github.com/heygen-com/hyperframes)

`/showhow` is an agent skill for Claude Code, Codex, OpenCode and other agents that load `SKILL.md` skills.
It reads your code, docs and git history, writes a script and storyboard, rebuilds the real UI, and renders an MP4 with voice-over, captions, music and sound effects.
No screen recording, no live URL, no video editor.

https://github.com/user-attachments/assets/185ce832-b266-4fd0-8f93-ffb733b11a3a

*How showhow works, made with showhow (45s).*

```text
/showhow how to export a report
/showhow what's new in 2.4.0
/showhow --mode general how to share a calendar in Outlook
/showhow --mode explainer how a gear train trades speed for force
```

## Contents

- [What you get](#what-you-get)
- [Install](#install)
- [Usage](#usage)
- [Modes](#modes)
- [Explainer mode](#explainer-mode)
- [Styles, themes and voices](#styles-themes-and-voices)
- [Options](#options)
- [How it works](#how-it-works)
- [Privacy](#privacy)
- [Credits](#credits)
- [License](#license)

## What you get

Every run writes a folder to `~/Downloads/showhow-<video-name>/`:

| File | What it is |
|---|---|
| `<video-name>.mp4` | The rendered video |
| `<video-name>.jpg` | Poster frame, also baked into frame 0 |
| `captions.srt` | Captions that match the narration word for word |
| `chapters.txt` | Chapter timestamps for YouTube, Vimeo or an LMS |
| `showhow.md` | A written companion with the same steps |
| `share-copy.md` | A short post to share the video, and a title and description for where you upload it |
| `composition/` | The Hyperframes project, so you can edit and re-render |

## Install

### 1. Add the skill

With the [skills CLI](https://skills.sh), for any supported agent:

```bash
npx skills add Beer-de-Vreeze/showhow
```

Or as a Claude Code plugin:

```text
/plugin marketplace add Beer-de-Vreeze/showhow
/plugin install showhow@showhow
```

### 2. Add Hyperframes

showhow builds its videos with the [Hyperframes](https://github.com/heygen-com/hyperframes) skills, so install them next to it:

```bash
npx skills add heygen-com/hyperframes
```

### 3. Install the tools

On Windows, let the skill do it:

```text
/showhow install
```

This installs Node.js LTS, ffmpeg, Python 3.12, uv, whisper-cpp (checked against a SHA256), a Python venv for Kokoro voices, the helper scripts' Python packages, and the Hyperframes browser, all at pinned versions.
Docker Desktop is optional: run `install.ps1 -Docker` for reproducible `render --docker` renders (it asks for admin).
It also tries to install [earshot](https://github.com/Leonxlnx/earshot) for an optional audio check of the finished video; if that fails, showhow works without it.
Restart your agent app afterwards so it picks up the new `PATH` and `HYPERFRAMES_PYTHON`.

On macOS and Linux, install these yourself:

| Tool | Used for |
|---|---|
| Node.js 20+ | `npx hyperframes` |
| ffmpeg | Rendering and audio |
| Python 3.12 + [uv](https://docs.astral.sh/uv/) | Helper scripts |
| A venv with `kokoro-onnx==0.6.1 soundfile==0.14.0 numpy==2.5.3`, exported as `HYPERFRAMES_PYTHON` | Voice-over |
| [whisper.cpp](https://github.com/ggml-org/whisper.cpp) (`whisper-cli` on `PATH`) | Caption timing |
| Optional: [earshot](https://github.com/Leonxlnx/earshot) v0.2.0 (`earshot` on `PATH`) | Listening to the finished video |

Then run `npx hyperframes@0.9.85 browser ensure` and `uv sync --project skills/showhow/scripts --all-groups`.

## Usage

Open your project in your agent and describe the video:

```text
/showhow how to add knowledge to a project
/showhow --mode update 2.4.0
/showhow what's new since v2.3.0 --style release
/showhow how to restore a prompt version --format vertical --music
/showhow --mode general how a train gets its power --voice am_michael
/showhow options
```

`/showhow options` lists every mode, style, explainer visual type, theme and voice on your machine.

## Modes

| Mode | Use it for | The viewer can afterwards |
|---|---|---|
| `howto` | One task in your product | Do the task without the video |
| `update` | A release, tag, PR or commit range | Say what changed, where to find it and why it matters |
| `general` | A process, a third-party app, a physical task or a topic, no codebase needed | Do the task, or explain the topic |
| `explainer` | An idea, a mechanism, a place or a piece of history, from a topic or your own script | Explain how it works |

The mode is inferred from your request.
Steps that happen outside your product, like creating an API token in a vendor portal before connecting it, work in every mode.
showhow researches them from official docs and rebuilds the screens with fictional data.

## Explainer mode

An explainer is a narrated video about an idea, a mechanism, a place or a piece of history, where every spoken sentence gets one picture drawn in code.
Ask for one with `--mode explainer`, or just ask how something works or paste a script:

```text
/showhow --mode explainer how a gear train trades speed for force
```

- **Your script or a drafted one.**
  A pasted script is narrated word for word.
  Give a topic instead and showhow drafts the script, ties every fact to a source, and stops for your approval before it builds anything.
  A fact it cannot source shows up as `[NEED: what is missing]`, and the plan check refuses to render until you fill it in.
- **Preview before render.**
  After the build, showhow writes one still per scene in every format and waits for your approval, so a wrong picture costs you a minute, not a render.
- **Shape.**
  What you'll understand, the parts by name, one scene per sentence grouped into chapters, then a recap; no step counter.
  60 to 120 seconds, 180 at most.
- **Visual types**, one per sentence:
  - `flow` (boxes and arrows that build in order), `chart` (bars from zero, axes first), `map` (a labelled locator), `photo` (a licensed photo), `card` (one number, name or quote).
  - Five 2D motion styles: `stroke-reveal` (lines draw themselves), `kinetic-type` (whole words rise out of a mask), `data-anim` (a number ticks while a bar grows), `morph` (one shape becomes another, also for match cuts) and `flat-scene` (flat or isometric shapes, things travelling along a path); `parallax` for the intro only.
  - `scene3d`, one 3D stage per video with a `kind`: `machine` (gears, shafts and springs built from the script's numbers, moving in ratio, with a cutaway, an exploded view, slow motion and airflow), `globe` (a highlighted country, great-circle routes, a zoom that cuts to a flat map) or `hero-number` (one key figure as 3D type).
    Your own glTF model can stand in when no kind fits.
  - Every number in a 3D scene's parameters must be spoken, so the model never contradicts the voice.
- **Three formats in one run.**
  16:9, 9:16 and 1:1 by default, each laid out for its own frame, named `<video-name>-landscape.mp4`, `-vertical.mp4` and `-square.mp4`, sharing one `captions.srt` and `chapters.txt`.
  `--format landscape` renders just one.
- **The `showhow` theme.**
  Warm paper, ink line drawings and one teal accent, with EB Garamond titles and Inter labels; the explainer default, and available in any mode with `--theme showhow`.
- **Brand kits.**
  `--brand <name>` uses a local kit in `~/.showhow/brands/<name>/` (colours, fonts, logo) instead; 3D scenes and the 2D styles take their colours from it too.
  `/showhow brand <name> <repo or URL>` creates one.
- **Music on by default**, a bundled track kept 20 dB under the voice; `--no-music` turns it off.
- **Written companion.**
  `showhow.md` is the script as a short article with a numbered sources list.

## Styles, themes and voices

Four styles, in every mode:

| Style | Feel |
|---|---|
| `clean` | Neutral, precise, product docs (default for how-tos) |
| `friendly` | Warm and encouraging, for first-time users |
| `release` | Punchy and beat-locked (default for updates) |
| `quick-tip` | One small trick in 20 to 40 seconds |

Presets are a starting point: add freeform direction such as `--style "calm, like Apple support videos"`.

- **Themes:** `--theme <preset>` applies a frame preset to title cards, captions and step cards: `showhow` (the house theme) or any Hyperframes preset.
  Rebuilt product screens keep their own look.
- **Brand kits:** `--brand <name>` applies a local kit from `~/.showhow/brands/<name>/` (never committed); `/showhow brand <name> <repo or URL>` creates one.
- **Design floor:** every video's own chrome (title, cards, counters, captions, outro) follows a short design floor adapted from impeccable: contrast and type checks, and a list of generated-design defaults it refuses, such as eyebrow labels and blurred gradient backgrounds. A `--theme` preset keeps its deliberate choices.
- **House style:** showhow remembers how you like your videos.
It reads `~/.showhow/verdicts.md` (your defaults and always/never rules) and `~/.showhow/edits.md` (before/after lessons) at the start of every run.
When you ask for changes, it keeps the lasting ones there and shows you the diff; `/showhow learn <output-dir>` does the same for a past video.
- **Voices:** `--voice <id>` picks any [Kokoro](https://github.com/thewh1teagle/kokoro-onnx) voice. The default is `af_heart`. Narration is English.

## Options

| Option | Values | Default |
|---|---|---|
| `--mode` | `howto`, `update`, `general`, `explainer` | Inferred |
| `--style` (alias `--tone`) | A preset or a freeform description | `clean`; `release` for updates; `friendly` for explainers |
| `--format` | `landscape`, `vertical`, `square`, `all`, or a comma list | `landscape`; all three for explainers |
| `--duration` | Seconds | Set by the narration |
| `--audience` | Freeform, for example "new users" | Inferred |
| `--theme` | A frame preset name, `showhow` first | The product's theme; `showhow` for explainers |
| `--brand` | A local brand kit name (`~/.showhow/brands/<name>/`, never committed) | None |
| `--voice` | A Kokoro voice id | `af_heart` |
| `--title` | Text | Inferred |
| `--no-voice` | Flag | Narration on |
| `--no-captions` | Flag | Captions on |
| `--music` | Flag | Music off for `clean`, `friendly` and `quick-tip`; on for `release` and explainers |
| `--no-music` | Flag | Forces music off in any style |
| `--no-sfx` | Flag | Sound effects on |

Length limits keep videos watchable: how-tos run 45 to 120 seconds (3 minutes at most, longer topics are split), updates cover 2 to 5 changes in 30 to 90 seconds, and explainers run 60 to 120 seconds (3 minutes at most).

## How it works

1. **Inspect.** Reads the code, docs and styles for the real flow, or git history and release notes for an update.
2. **Plan.** Writes `showhow-plan.md` with the goal, audience, narration script and a scene-by-scene storyboard, and checks it against the teaching rules (`plan_gates.py`): one action per step, steps long enough to follow, a "Now try it" ending, within the length limit.
3. **Compose.** Generates the voice-over and builds a Hyperframes composition that rebuilds your UI from its own components, styles and copy.
4. **Deliver.** Checks, renders, normalises the loudness to -16 LUFS, measures the mp4 for blank frames, a dragging ending and steps shorter than planned, and writes the captions, chapters, companion doc and share post.

Every video follows the same teaching rules: say the outcome first, highlight a target before acting on it, one action per step, hold each result until the narration finishes, and keep a step counter on screen.

## Privacy

Rendering, voice-over and captions run on your machine.
Two things can be downloaded per video: a music track from [Incompetech](https://incompetech.com) when no bundled track fits, and a sound effect from Openverse (through Hyperframes media-use) when the bundled library has none; only the search terms are sent.
`general` mode and outside steps go online to read official docs and capture public pages.
Tooling also reaches the network: `npx hyperframes` fetches the Hyperframes package from npm when it isn't cached, and `uv` downloads the helper scripts' Python packages the first time; neither sends anything about your project.
showhow skips `.env` files, keys and credentials while it reads your project, and replaces names, emails, hostnames, IDs and tokens with fictional values before anything reaches the video.
It never signs in to a site or types a password for you.

## Credits

- Built on [Hyperframes](https://github.com/heygen-com/hyperframes) by HeyGen.
- Started as a fork of [brag](https://github.com/latent-spaces/brag) by Shunit Haviv Hakimi (MIT); parts of the audio pipeline still come from it, and its launch-reel styles live on there.
- The design floor for the video's chrome (`references/design-floor.md`) is adapted from [impeccable](https://github.com/pbakaus/impeccable), [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0), rewritten for video.
- The house-style files, the video gates (`scripts/video_gates.py`), the review step and the motion values come from [motionmaxxing](https://github.com/Tejashmakwana/motionmaxxing), [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0), rewritten in our own words.
- Design-floor rules and the optional before/after change come from [unslop](https://github.com/heydamir/unslop) by Damir Sokolovsky ([@heydamir](https://x.com/heydamir)), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); a video that uses the before/after credits it on the outro.
- The pictured-promise and one-view-per-point rules come from [taste-skill](https://github.com/Leonxlnx/taste-skill), [MIT](https://opensource.org/licenses/MIT).
- Music: "Happy Beats / Business Moves" by Sascha Ende ([ende.app](https://ende.app/en)), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Videos that use a bundled track get the credit line in `credits.txt`.
- Extra music: Kevin MacLeod ([incompetech.com](https://incompetech.com)), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), downloaded per video when no bundled track fits.
- Every CC BY track, sound effect or photo a video uses gets a line in `credits.txt` and on the outro.
- Sound effects: [Kenney](https://kenney.nl) and [unicae_games](https://opengameart.org/content/keyboard-soundpack-1-typing-and-single-keystrokes), CC0.

## License

[MIT](LICENSE) for the skill.
Bundled and downloaded music, sound effects and photos keep their own licenses, listed above.
