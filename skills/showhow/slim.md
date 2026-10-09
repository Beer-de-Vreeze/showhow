---
name: showhow-slim
description: Turn a project into a narrated how-to video (one task) or a feature update video (what's new in a release), with captions, chapters and a written companion. One file - built entirely by the model with the tools already on the machine. Use when someone says "/showhow-slim", "make a how-to video", "what's new video", or wants to show users how something works. If the /showhow skill is also installed, let /showhow handle those phrases; it hands off here on Opus 5.5.
---

# /showhow-slim

Show people how it works, and what's new.
You make the whole video yourself - script, voice, visuals, captions, render - with whatever tools are on the machine.

Whatever the style, it should feel like a good product support video: calm, exact, and easy to follow the first time.

Usage: `/showhow-slim [task or release] [options]`. Options (flags or plain language):

| Option | Default |
|---|---|
| `--mode howto\|update\|general` | inferred: a task -> `howto`; a version, tag, PR, range or "what's new" -> `update`; a task this project's code can't show (a process, a third-party app, a physical task) -> `general` |
| `--style <name>` (alias `--tone`; 11 styles, see Styles) or freeform | `clean` for howto and general, `release` for update |
| `--format landscape\|vertical\|square` | landscape (1920x1080; vertical 1080x1920, square 1080x1080), 30fps |
| `--audience <who>` | inferred |
| `--theme <frame preset>` (`../hyperframes-creative/frame-presets/`) | product theme; general: picked per topic |
| `--voice <Kokoro id>` (`npx hyperframes tts --list`) | `af_heart` |
| `--no-voice`, `--no-captions`, `--no-music`, `--no-sfx` | all on |

Write the deliverables to `~/Downloads/showhow-<video-name>/` (Windows: `%USERPROFILE%\Downloads`), where `<video-name>` is a 2-5 word kebab-case slug of the video's title, e.g. `showhow-connect-confluence/`.
Name the video `<video-name>.mp4` and the poster `<video-name>.jpg`; the other files keep their fixed names.
If the folder already exists, append `-YYYY-MM-DD-HHmmss`.
Keep every intermediate file (screens, voice clips, frames, scripts) in a `work/` subfolder inside it.

## 1. Inspect

**howto:** trace the task through the code the way a user does it: the entry point (route, sidebar item, menu), every control they touch in order with its **exact on-screen label**, what visibly happens after each action, prerequisites (roles, settings, data), one mistake or limit worth mentioning, and where the result lives afterwards.
More than about 8 actions means two tasks: propose a split and make part 1.

**Outside steps (any mode) and general:** a step this code can't show (an API token made in Atlassian before connecting Confluence, a process, a physical task) is tagged `outside`; `general` is a video of only outside steps. Read `references/general.md` and follow it: facts from the user's material, then the vendor's official docs (search for them), then screenshots of the real pages in your browser (never sign in or commit a real change yourself; ask the user to sign in), then only well-established knowledge; never invent a label (describe it and list it as unverified); rebuild screens from those screenshots with fictional data instead of showing them as-is; topic images (the subject itself: trains, a device) from the user, then `media-use resolve --type image`, then freely licensed photos with license logged in `work/sources.md` and attribution lines in `credits.txt` and on the outro credit line (no separate credit scene); invented step cards or diagrams only where nothing real exists; a topic without steps uses the points shape (outcome -> 3-6 points with a "2 of 5" counter -> recap); in `general`, a frame preset instead of a product theme. Everything else here (shape, laws, sound, deliverables) works as for howto.

**update:** pin the release range (tags, version-bump commits, CHANGELOG; state the range you chose).
Read the team's own release notes first (CHANGELOG, release commit subjects, PR titles, features/status docs), then the commits in the range.
Keep only user-visible changes, rank them, keep 2-5, and trace each into the UI like a howto: what it is, where it lives, one or two actions that show it, why it matters to the viewer.

**Always:** read the styles (exact colors and fonts, (the product's brand or default theme (the one its `:root` defines, or that its theme picker marks as default), never whatever a test fixture or a dev build happens to load; write down the theme id and its background and accent values), the README and product docs (the product's own names for things), and the UI copy.

**Nothing secret or personal leaves this step.** No secrets, tokens, tenant or client IDs, internal hostnames, real customer, colleague or user names, emails, or commit authors in anything you produce.
Use plausible fictional stand-ins on screen and list them in the plan.

## 2. Script and plan

Write `showhow-plan.md`: mode, goal line, audience, prerequisites, style, format, visual identity, fictional data, the narration script, and a scene-by-scene storyboard (screen, counter, highlight, action, result, narration, caption, transition).

**Script first; the voice sets the pace.**
Second person, present tense, 8-16 words per sentence, one sentence per action plus at most one of why.
Name controls by their exact label.
No "in this video", "simply", "just", "seamless", "powerful".
Plan about 2.5 words per second.

**Shape (howto):** Outcome (3-5s) -> Before you start (only if needed) -> Steps, one action each (6-15s) -> Result (3-6s) -> Recap (3-5s). Target 45-120s; `quick-tip` 20-40s.

**Shape (update):** "What's new in [version]" (3-5s) -> each change: what / where / show / why (10-20s) -> how to get it (3-5s). Target 30-90s.

## Teaching laws

- **One job per video.** One task, or one release.
- **Outcome first.** Within 5 seconds the viewer knows what they'll be able to do, or what's new.
- **Show the real product.** Render the project's own components with fictional data, or screenshot the running app (dev server, fictional data, never production), or rebuild the screen from its styles and exact copy - in that order of preference. No abstract filler where a real screen exists. Reuse the product's own icons and logos (often inline SVG in shared components), never letter badges.
- **State carries forward.** What a step creates stays visible on later screens: the attached file in the sent message, the chosen model in the reply header.
- **Orient, point, act, result.** For every step: show enough of the screen to know where you are; highlight the one target (ring, spotlight or zoom) while the voice names its label; move the cursor and click or type; hold the result until the narration ends plus 0.5s.
- **Same screen, same camera.** Between steps on one screen, zoom and pan; fade or cut only when the screen changes.
- **Always oriented.** "Step 2 of 4" (howto) or "2 of 3" (update), same place every time.
- **Readable.** Anything the voice names is legible at the chosen zoom; on-screen labels hold 1.5s settled; camera moves take 0.6-1.0s.
- **Captions match the voice** verbatim, max 2 lines of ~42 characters, never over the highlight.
- **Every frame accurate.** A wrong label or wrong order is the worst bug a how-to can ship.
- **Grounded claims.** Anything the video says the product does, its names and its numbers, must appear in the project (for outside steps: in the user's material, the official docs or your screenshots). Fictional demo data (names, files, replies) is fine and listed in the plan; invented capabilities are not.

## Styles

| Style | Feel | Pacing / transitions |
|---|---|---|
| `clean` | Neutral, precise, product docs; little or no music | 6-12s per step; cuts between screens |
| `friendly` | Warm, patient, explains why in half a sentence | 8-15s per step, max 5 steps; soft fades |
| `release` | High energy around clear demos: punchy hook, change cards with "New"/"Fixed" tags, beat-locked reveals; "You can now..." | 10-20s per change; fast slides/zooms between changes, calm demos inside |
| `quick-tip` | One trick, 1-3 actions | 5-8s per action; cuts, no recap |
| `playful`, `polished`, `yc-parody`, `chaotic`, `deadpan`, `cinematic`, `app-store` | The energy tones at teaching length: their hook, typography, transitions and outro; steps keep the script rules | Rhythm from `references/tones.md`, length from the narration and the shapes above; `chaotic` (1-2s), `playful` and `app-store` (2-3s) also cut inside narration lines for topic points and steps without a UI; scored like `release` |

All eleven work in every mode; `references/tones.md` has the full definitions and shared rules.

## Sound

The voice leads.
Generate it per scene with `npx hyperframes tts "<text>" --voice <voice> --output work/voice/scene-NN.wav` (`<voice>` = `--voice`, default `af_heart`; or any local TTS if that's unavailable), measure each clip, and let the clips set the scene lengths.
Transcribe the clips to catch mispronounced product names; fix by respelling the TTS input only.
`npx hyperframes transcribe` overwrites `transcript.json` on every run: copy it to `work/tx/words-NN.json` after each clip.
Music is a quiet bed ducked under the voice (about 0.1 under narration, 0.3 without), never cut off abruptly.
Use a bundled track; for `cinematic`, `deadpan`, `chaotic` and `yc-parody`, or when the user asks, generate one with MusicGen in the style's mood (`references/audio.md`, Generated bed).
How-tos: SFX mainly confirm visible actions (a soft click per click, soft ticks on typing, one accent on the result).
Updates: score it with high energy around the demos (a soft reveal hit, card sounds, tag ticks, a payoff (bells allowed), music up and beat-locked on the hook, cards and outro), clicks and typing inside the demos.
The full sound effect library is fair game in both; never mask a narrated word.

## 3. Build, check, render

Build it with whatever works on this machine.
If you draw the video in a browser, make every frame a pure function of time and wait for fonts and images to load before capturing each one.

- **Place rings and the cursor by element, never by hand-computed pixels.** Give each target an `id` and measure its box once inside `document.fonts.ready`, before building the timeline (`offsetLeft`/`offsetTop` walked up to the root). No function-valued tweens: `check` flags them, and render workers disagree once layout animates. Add a known offset for targets below something that grows later. See the `R()`/`ring()`/`move()` helpers in `references/step-3-compose.md`.
- **Screenshot videos: bake rings into the stills.** DOM ring overlays on top of screenshots can vanish from the rendered mp4 while snapshots and plain Chrome show them. Record rings and screen changes, give them to `scripts/bake_highlights.py` in timeline mode, and fade in the ringed copies it lists in `rings.overlays.json`; the script does the span cutting, clamping and checks, so don't hand-write that. Image swaps render reliably.
- **Every tween is a `fromTo` with `immediateRender:false`, one element per highlight or ripple.** No pooled elements re-tweened with `tl.to`: seeks out of order leave them in the wrong state.
- **Starting states live in CSS.** A `tl.set` at time 0 does not show on frame 0.
- **Write big files with a file tool**, not a shell heredoc; long heredocs fail on Windows (`ENAMETOOLONG`).
- **Overlays open below the app header**, so the step counter stays visible.
- **Intentional overlaps and `hyperframes check`:** `data-layout-allow-overlap`/`-occlusion` on an overlay or wrapper don't clear `content_overlap`; `data-layout-allow-overlap` does work on the exact text element `check` names. Place dialogs off the control that opened them, hide cells under an opaque sheet while it's open, and use `data-layout-ignore` on floating callouts. `data-layout-allow-overflow` covers intentional ellipsis.

Before the full render, look at stills from every step at the highlight and at the result, and from mid-transition.
A plain crossfade between two busy layouts makes a muddy double exposure; stagger it (old content out, then new content in) or dip through the background.
Check: the ring sits exactly on the control the voice names (zoom in on a crop when unsure), its label is legible, captions, the cursor or a dragged item don't cover it, the counter is right and uncovered, no text is clipped inside a fixed-width pill or callout (`check` misses these), no bullet or icon shows before its text, a typing caret follows the typed text, contrast is fine.
SFX clips get `data-duration` equal to the file's real length, or `check` warns about the slot.
Then render `<video-name>.mp4` **without `--quiet`**, logging to `work/render.log`: a quiet render can exit non-zero with no message and no file.
It's done only when the mp4 exists; otherwise read the log, check free disk space, and retry once.
If the composition tweens layout (`height`, `width`, position, padding), add `--experimental-fast-capture=false`: fast `drawelement` capture drops those changes while snapshots still show them.
Then pull frames from the mp4 itself at every ring and result moment and look at them; snapshots alone don't prove the render:
`uv run --project <skill-dir>/scripts <skill-dir>/scripts/frame_sheet.py <video-name>.mp4 --overlays work/rings.overlays.json -o work/check.jpg` samples every baked ring; add `--at <t1,t2,...>` for other moments and `--crop x,y,w,h` to judge small rings.
A ring missing from the mp4 but present in snapshots is a render bug, not a timing bug: bake it into the still instead of re-rendering with other flags.
Keep creation and rendering local; publishing or uploading needs a separate explicit request.

## 4. Deliver

- **Poster:** the settled title card (or the finished result with the title) with no caption on it; when the voice talks over the title, snapshot a caption-hidden copy of the composition (step 4), to `<video-name>.jpg`, baked in as frame 0 of `<video-name>.mp4` by replacing that frame, so duration and audio sync stay the same.
- **`captions.srt`:** the script phrases with their absolute times, even when captions are burned in.
- **`chapters.txt`:** `00:00 Title` style, one line per step or change, from the real scene start times.
- **`showhow.md`:** the written companion. howto: "How to [task]", prerequisites, numbered steps with labels in bold, result, tip. update: "What's new in [version]", one short section per change with where to find it, then how to get it.
- **`credits.txt`:** only when a bundled music track is used (line format in `references/audio.md`) or an image license asks for attribution (title, author, license, URL, one line each). The same credits also appear in the video as the outro credit line (`references/step-3-compose.md`).
- **`share-copy.md`:** a business post to send with the video ("Post", 3-8 short lines: what it is, what it helps the reader do in their work, the prerequisites or 2-4 changes, one concrete action) and a "One-liner". If `~/VOICE.md` exists, write as its owner following its business sections; otherwise direct and plain. Audience's language, no hype or invented claims, no em dashes, `[link]` for anything you don't have (`references/step-4-deliver.md`).
- **Tell the user** where everything is, the share post ready to paste, the goal line and the step or change list (so they can spot a wrong step without watching), the fictional substitutions, any label you couldn't verify in the code, and offer to redo a scene, change the voice, or make a vertical or quick-tip cut.
