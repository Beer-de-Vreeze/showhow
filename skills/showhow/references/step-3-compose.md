# Step 3: Narration, brief, and Hyperframes

## Generate the narration first (unless `--no-voice`)

The voice sets the timing, so generate it before building scenes.
Generate **one clip per scene**, so each scene's length comes from its own audio and a rewrite of one line doesn't shift the rest:

```bash
mkdir -p <output-dir>/composition/assets/voice
npx hyperframes tts "<scene 1 narration>" --voice <voice> --output <output-dir>/composition/assets/voice/scene-01.wav
npx hyperframes tts "<scene 2 narration>" --voice <voice> --output <output-dir>/composition/assets/voice/scene-02.wav
# ...one per scene with narration
```

`<voice>` is the plan's voice (`--voice`, default `af_heart`; `npx hyperframes tts --list` shows them all); use the same voice for every scene.
See `media-use` for current TTS options.

Then measure each clip:

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 <output-dir>/composition/assets/voice/scene-01.wav
```

Set each scene's duration to `clip length + 0.5-1.0s` (longer after a step's result, shorter in `quick-tip`), and `clip length + about 2s` for a scene that ends a subtask (marked in the plan).
Start each clip about 0.3s after its scene starts, so the voice doesn't collide with the transition.
Update the scene durations in `showhow-plan.md` to the measured values.

**Listen for mispronunciations** of product names and labels: transcribe the clips (see `media-use` / `npx hyperframes transcribe`) and compare with the script.
`npx hyperframes transcribe` writes `transcript.json` and overwrites it on every run, so copy it right after each clip:

```bash
mkdir -p <output-dir>/work/tx
for n in 01 02 03; do
  npx hyperframes transcribe <output-dir>/composition/assets/voice/scene-$n.wav && cp transcript.json <output-dir>/work/tx/words-$n.json
done
```
Fix by respelling in the TTS input only (e.g. "Azure" -> "Azhure"); captions keep the correct spelling.
Kokoro IPA markup (`[word](/ipa/)`) is not passed through by `npx hyperframes tts`, so respelling is the only fix.

## Caption timing

Captions show the script text, not the transcription.
Get word timings by transcribing each narration clip (`npx hyperframes transcribe`, see `media-use`) and align the script's phrases to them.
If transcription is unavailable, spread each scene's phrases evenly across its clip duration.
Split phrases so each cue has lines of at most 37 characters, 2 lines (3 on vertical), and stays on screen at least 0.3s per word; Step 4's G-captions gate checks it.
Kokoro speaks about 3 words a second, faster than 0.3s per word, so one-line cues that follow the voice phrase by phrase come out too short: put two phrases in one two-line cue, and let a scene's last cue run on into the hold.
Keep the phrase list with timings; Step 4 writes it to `captions.srt`.

With `--no-voice`, time the captions by reading speed (about 0.35s per word, min 1.5s per phrase) and let that set scene durations.

## Create the composition brief

Write `<output-dir>/composition-brief.md` before creating the composition.

```markdown
# Hyperframes Composition Brief: [Title]

## Objective
[howto: Teach [audience] how to [task] in [product]. / update: Show [audience] what's new in [product] [version].]

## Output
- Composition directory: `<output-dir>/composition/`
- Rendered video: `<output-dir>/<video-name>.mp4`
- Format: [landscape / vertical / square] - [width]x[height], 30fps
- Several formats: one timeline; the root carries `data-format`, rewritten per format by the wrapper (see "Several formats")
- Duration: [sum of measured scene durations]

## Source Material
- Project root: [path]
- Files the screens come from: [components, routes, style files]
- Product name and version: [...]
- Exact UI labels used in the steps: [list]
- Fictional data to show: [list from the plan]

## Teaching Direction
- Mode: [howto / update]
- Style preset and direction: [...]
- Goal line: [...]
- Step or change list: [numbered, one line each]
- Avoid:
  - Marketing language and invented claims
  - Abstract filler visuals where a real screen exists
  - Any real personal data, hostnames, IDs or secrets

## Visual Identity
- Colors: [exact values]
- Fonts: [display / body]
- Theme: [theme id] - background [value], accent [value]
- LOOK: [ground value] ground, [ink value] text, [accent value] accent; [display face + weight] / [body face + weight]; [where the ground comes from: product surface, preset, subject's world]
- BANNED: [the design-floor.md Refuse items this video must avoid, minus any the theme preset uses on purpose, plus anything the product's look rules out, plus the house style's `## Never` rules]
- Design floor: `references/design-floor.md` applies to the chrome only; rebuilt screens keep the product's look

## Storyboard
Use the storyboard in `<output-dir>/showhow-plan.md` as the contract.

Scene summary:
1. [Scene] - [duration]s - [screen, highlight, action, result]
2. [...]

## Teaching elements
- Step counter: [position, format "Step 2 of 4" / "2 of 3"], same place in every step scene
- Highlight: [ring / spotlight / zoom], accent color [value], one target at a time
- Cursor: [system-like arrow], smooth 0.5-0.8s moves, rests 0.2-0.3s on the target before it clicks, a quick press (the kit's `ripple`: a 2-frame squash, a 3-frame spring back), and the target answers (pressed state, menu opening) a frame after the press
- Captions: [band position], max 2 lines (3 on vertical) x 37 chars, 0.3s per word, high contrast plate, never over the highlight
- Title and outro cards: [text]
- Credit line: [the short credits from `credits.txt`, or none]

## Audio
- Narration: `assets/voice/scene-NN.wav`, track per scene, volume 1.0, start ~0.3s into each scene
- Music: [filename or none], level per `audio.md` (ducked under the voice)
- SFX: soft click on each simulated click, soft key ticks on typing, one gentle accent on the final result; Hyperframes picks exact files
- Audio files: copy everything used into `<output-dir>/composition/assets/`

## Hyperframes Instructions
Load `hyperframes` (the contract, `references/motion.md`, `references/format.md`, `references/captions.md`), `hyperframes-cli`, and `media-use` for voice and captions.
/showhow is its own workflow: skip the `hyperframes` storylines, `SPEC.md` and type files; this brief replaces them.
Prefer native Hyperframes conventions over anything in `/showhow`.

Requirements:
- Every step is shown on the real product UI (rendered components, screenshots of the running app, or a faithful rebuild from the project's styles and copy).
- For every step: orient -> point (highlight + narration names the label) -> act (cursor/typing) -> result held until the narration ends.
- Within one screen, move between steps with camera moves (zoom/pan), not fades.
- Captions match the script verbatim and are timed to the voice.
- Keep all text readable in the final render; UI text that the narration names must be legible at the chosen zoom.
- Music never competes with the voice.
- No more than three flashes in any one second: no white or black flash frames, no strobing (WCAG 2.3.1).
- The first 3 seconds and every title or change card read with the sound off.
- Update videos: hook, change cards, tags and outro get high-energy motion, SFX accents and beat locks; the UI demos inside each change stay calm and follow the teaching sequence.
- Run `hyperframes check` before render.
- Keep creation and rendering local. Remote or publishing workflows require a separate explicit user request.
```

The brief is the boundary: teaching content, steps, labels and audio levels belong to `/showhow`; composition implementation belongs to Hyperframes.

---

## Several formats

One composition and one timeline serve every format; captions and chapters are shared.
The formats are the plan's `## Formats` (or its `## Format:` line); the wrapper reads them from `--plan`.
Author the root at landscape: `data-width="1920" data-height="1080"` (the wrapper needs both) and `data-format="landscape"`.
For each format the render wrapper copies the composition to `work/formats/<format>/` and sets the copy's root `data-format`; every composition element sized like the root (the root, sub-composition hosts, and the roots in `compositions/*.html`) gets the format's `data-width` and `data-height`, and one at another size (an inset) keeps its own.
Your composition is never edited.
Lay each format out for its frame with per-format CSS (`[data-format="vertical"] .stage { ... }`), not by cropping; use JS that reads the root's `data-format` only if CSS can't do it.
To snapshot one format yourself, snapshot its copy in `work/formats/<format>/` (`render.py ... --stills` writes the copies and the preview stills).
A 3D canvas is sized in pixels, so size it from its container at build time (`clientWidth`, `clientHeight`) and pass those to `createStage`; widen `viewHeight` on narrow frames so the object fits (`references/3d-scenes.md`).
Vertical: keep captions clear of the right-hand app rail (`check` warns `outside_safe_zone`): a caption box inset more on the right than the left, about 38px type.

## Building the screens

If you render the project's own components or screenshot the running app:

- Use fictional data everywhere (see the secrets rule in step 1). Seed it through the app's own fixtures, mocks, or a local-only test account on a dev server; never sign into production with real data to capture screens.
- Capture at the video's resolution or 2x, so zooms stay sharp.
- Hide dev-only chrome (devtools, debug banners, browser UI) unless showing the browser is the point.
- Keep one screenshot per step state, named `step-NN-<state>.png` in `composition/assets/screens/`.

Stage the composition before building it, and again after any theme change:

`uv run --project <skill-dir>/scripts python <skill-dir>/scripts/stage.py composition (--theme <name or folder> | --brand <name>)`

It copies every asset the composition may use (the kit, `scene3d` with its data, GSAP and its plugins, three.js and the hero-number typeface, the theme's fonts), writes `assets/theme.css` with `@font-face` and one `:root` token set (`--paper`, `--ink`, `--accent`, `--muted`, `--font-display`, `--font-body`) from the theme's `FRAME.md`, and puts the three.js import map and the theme link in `index.html`'s head.
Everything is local at render time and every version pin lives in `stage.py`; never copy these by hand or load them from a CDN.
For the product's own theme (howto, update), write a `FRAME.md` with those colours and a `title` and `label` font family, and the font files as `fonts/<Family>-<weight>.woff2`, into `work/theme/`, and pass `--theme work/theme`.
Use only `var(--...)` for the chrome colors and fonts (backgrounds, title and card fills, tags, counters, rings, ripples, fades), so a retheme is one re-run.
`bake_highlights.py` takes the ring colour from the same file: pass `--theme composition/assets/theme.css`.

For a desktop app whose frontend is a web SPA, render the frontend in a browser with its API calls mocked.
If the app needs a backend you cannot run, rebuild the screens from its components and styles instead.

## Place highlights and the cursor by element, not by pixels

Hand-computed ring and cursor coordinates drift once fonts load and layouts settle, and put rings in the wrong place.
Use the showhow kit for rings, the cursor, click ripples and the step counter: it measures each target by element and writes every tween as a `fromTo`.

1. `stage.py` (above) has put the kit in `composition/assets/kit/`.
2. In each scene that uses it, inside `<template>`: `<link rel="stylesheet" href="assets/kit/showhow-kit.css" />` and `<script src="assets/kit/showhow-kit.js"></script>` before the scene's own script.
3. Rings and ripples take `--accent` from the staged theme (optional overrides: `--sh-ring-width`, `--sh-ring-radius`, `--sh-ripple-size`, `--sh-ripple-fill`).
4. Write every kit element in the HTML with a stable id, as direct children of the scene root (or of a `#world` camera layer at 0,0): one `.sh-ring` per ring, one `.sh-ripple` per click, one `.sh-cursor`, and a `.sh-counter` with one span per step.
   Give rings, ripples and the cursor `data-layout-ignore`.
   Ids must be unique across the whole video, so with more than one scene prefix them per scene (`#s2-cursor`, `#s2-count-1`) and pass `cursor: "#s2-cursor"` and `countPrefix: "#s2-count-"` to `showhowKit`.
   Keep the counter inside the 80% title-safe box.
5. Call the kit after fonts load, then register the timeline:

```html
<div class="sh-counter"><span id="sh-count-1">Step 1 of 2</span><span id="sh-count-2">Step 2 of 2</span></div>
<div id="ring-01" class="sh-ring" data-layout-ignore></div>
<div id="ripple-01" class="sh-ripple" data-layout-ignore></div>
<svg id="sh-cursor" class="sh-cursor" data-layout-ignore>…</svg>
<script>
  const tl = gsap.timeline({ paused: true });
  document.fonts.ready.then(() => {
    // defaults: cursor "#sh-cursor", countPrefix "#sh-count-", cursorStart [0, 0], tip [8, 5] (arrow tip offset)
    const kit = showhowKit(tl, { root: "#root", cursorStart: [960, 900] });
    kit.move(0.8, "#btn-new");                    // arrives at 1.4s; call moves in time order
    kit.ring(1.4, "#btn-new", "#ring-01", 1.4);   // { pad, dy, fadeIn, fadeOut }
    kit.ripple(1.65, "#btn-new", "#ripple-01");   // rests 0.25s first; { dy, duration, press: true }: press = 2-frame squash, 3-frame spring back
    kit.counter(3.0, 2);                          // span 1 out, span 2 in
    window.__timelines["<scene-id>"] = tl;
  });
</script>
```

`kit.R(sel, pad)` returns a target's `[x, y, w, h]` in root pixels for anything else you place by element; `move` takes `{ tip: [x, y] }` for the arrow tip's offset.
`scripts/fixtures/kit-demo/` is a working example; render it after changing the kit or upgrading HyperFrames.

- Measure eagerly, once, inside `document.fonts.ready` before building the timeline - never with function values (`x: () => ...`). `check` flags those as `gsap_function_value_hazard`: each render worker initializes tweens on its own and gets a different answer once layout animates.
  The kit measures when you call it, so call it there.
- Measurement sees the layout at build time. When something above a target grows later (a file chip row opening above the text box), pass the known growth as `dy` for targets below it.
- Put every element's starting state (hidden, offset, unselected) in CSS. A `tl.set` at time 0 does not show on frame 0.
- `offsetLeft`/`offsetTop` ignore GSAP transforms, so an element's entrance slide doesn't shift its ring. If the element's container is still moving at ring time, ring after it settles.
- Give targets explicit sizes where their box would otherwise stretch (a full-width row when you mean the button in it).

## Screenshot videos: bake rings into the stills

When the screens are screenshots, don't animate DOM ring divs over them.
Hyperframes has dropped such overlays from the rendered mp4 deterministically (any worker count, software GPU, static dedup off) while `snapshot` and plain Chrome showed them correctly.
Image swaps always rendered, so draw the ring into a copy of the still and fade that copy in over the clean one:

1. Record each ring as `{ t, d, screen, x, y, w, h, pad, zoom }` instead of emitting tweens, and each screen change as `{ t, name, fade }`; `zoom` is the camera's on-screen scale at `t`, so the stroke looks the same at any zoom.
2. Write them as a timeline spec (`rings` + `shows`, format in the script's docstring) and run `uv run --project <skill-dir>/scripts <skill-dir>/scripts/bake_highlights.py work/rings.json --theme composition/assets/theme.css`.
   The script cuts each screen's time at every ring start and end, bakes one still per span (overlapping rings share a still), clamps a ring that outlives its screen to that cut, compares times in whole centiseconds, and fails on a ring that lands in no span, a ring on the wrong screen, or an id that isn't a CSS-safe selector.
   Don't re-implement the span cutting in the build script.
3. Read `work/rings.overlays.json` and put one `<img id="img-<id>">` per entry above the clean screens in `#world`.
   Fade it in at `in` over `in_dur` and out at `out` over `out_dur`.
4. Copy the ringed stills (`src` in each entry, relative to the spec) into the composition's assets.

Cursor and click ripples can stay DOM elements from the kit; give each ripple its own element.

## Every tween is a `fromTo`

Write every tween as `tl.fromTo(sel, from, { ..., immediateRender: false }, t)` and give every highlight or ripple its own element.
A pooled element re-tweened with `tl.to` picks up whatever state the last seek left, and render workers seek out of order.

## Overlays keep the viewer oriented

Dialogs, sheets and menus open **below the app header**, so the step counter stays visible in every frame.
Dim only the content area under a sheet, not the header.

## Credit line

When `credits.txt` has lines (bundled or Incompetech music, CC BY images or sounds, the trademark line for a rebuilt third-party app from general.md), show them in the video too, so the credit travels with the file wherever it is shared.
- Short form, one line per source: `Music: Sascha Ende (ende.app), CC BY 4.0`, `Photo: <author>, <license>`. Two lines at most; join more with ` · `.
- On the outro, from the moment it settles to the last frame, at least 2.5s.
- Bottom edge inside the safe area, centered or aligned with the outro text, in the theme's secondary text color at 28px on a 1080px short side (`check`'s type floor; smaller text warns `text_below_floor`), no plate.
- No caption on screen at the same time; end the last caption before the credit line appears.
- It fades in with the outro and gets no motion or sound of its own.

---

## Audio asset preparation

Read [audio.md](audio.md).
Copy the chosen music (if any) into `<output-dir>/composition/assets/music/`:

```bash
mkdir -p <output-dir>/composition/assets/music
cp <skill-dir>/assets/music/<track>.mp3 <output-dir>/composition/assets/music/
```

Hyperframes copies any SFX it selects into the same `assets/` tree after choosing exact files.

---

## Beat sync

For how-tos, don't sync to the music: the voice sets the timing.

For update videos (`release` style), sync the non-demo moments to the music.
Get a cue source (see `audio.md` -> "Beat and cue sources": bundled preset, `analyze_music_cues.py`, or `npx hyperframes beats`), then:

- **Strong cues** (`strongCues`, or the highest-`strength` beats): lock the hook reveal, each change-card entrance and the outro within ±0.15s. Mark them `// beat-locked: 12.40s`.
- **Beat grid**: snap sequential tags, counters and the preview list on the title card within ±0.10s. For readable text, every other beat or reveal-then-hold. Mark them `// beat-grid: ...`.
- **Narrated demos** follow the voice, not the beat. Shift a demo's start by up to 0.15s to land its card on a cue, but never stretch or cut narration to fit.

If no cue source is available, continue without sync and note it in the brief.

---

## Self-review checklist

Before moving to delivery, verify:

- [ ] `<output-dir>/composition-brief.md` exists.
- [ ] Narration clips exist per scene (or `--no-voice` was set), and scene durations match the measured clips.
- [ ] Every step shows the real UI with the named control highlighted before it is used.
- [ ] Every label spoken or captioned matches the UI text exactly.
- [ ] Every claim about what the product does, its names and numbers, appears in the project; fictional demo data is listed in the plan.
- [ ] The step or change counter is present and consistent.
- [ ] Captions are timed and never cover the highlighted target.
- [ ] Design floor, judged on `npx hyperframes snapshot` frames of the title, one step and the outro: no BANNED item in the chrome, contrast passes on every card and caption plate, at most two type families with tracking no tighter than -0.04em, nested radii are concentric, and every card enters and leaves with the same motion.
- [ ] When `credits.txt` has lines, the outro shows the credit line for at least 2.5s with no caption over it.
- [ ] No real personal data, hostnames, IDs or secrets appear anywhere.
- [ ] The narration names every result that matters; nothing important is only visible.
- [ ] Mute test: with the sound off, the first 3 seconds and every title or change card still say what the video is about.
- [ ] No flash frames or strobing; nothing flashes more than three times in any second.
- [ ] Total duration is within the mode limits.
- [ ] `hyperframes check` passes with zero errors.
