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

Set each scene's duration to `clip length + 0.5-1.0s` (longer after a step's result, shorter in `quick-tip`).
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

## Caption timing

Captions show the script text, not the transcription.
Get word timings by transcribing each narration clip (`npx hyperframes transcribe`, see `media-use`) and align the script's phrases to them.
If transcription is unavailable, spread each scene's phrases evenly across its clip duration.
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

## Storyboard
Use the storyboard in `<output-dir>/showhow-plan.md` as the contract.

Scene summary:
1. [Scene] - [duration]s - [screen, highlight, action, result]
2. [...]

## Teaching elements
- Step counter: [position, format "Step 2 of 4" / "2 of 3"], same place in every step scene
- Highlight: [ring / spotlight / zoom], accent color [value], one target at a time
- Cursor: [system-like arrow], smooth 0.5-0.8s moves, visible click feedback
- Captions: [band position], max 2 lines x ~42 chars, high contrast plate, never over the highlight
- Title and outro cards: [text]

## Audio
- Narration: `assets/voice/scene-NN.wav`, track per scene, volume 1.0, start ~0.3s into each scene
- Music: [filename or none], level per `audio.md` (ducked under the voice)
- SFX: soft click on each simulated click, soft key ticks on typing, one gentle accent on the final result; Hyperframes picks exact files
- Audio files: copy everything used into `<output-dir>/composition/assets/`

## Hyperframes Instructions
Load `hyperframes-core`, `hyperframes-animation`, `hyperframes-creative`, `hyperframes-keyframes`, `hyperframes-cli`, and `media-use` for voice and captions.
/showhow is its own workflow: do not enter the `hyperframes` entry-point intent interview and do not route into its promo, explainer or launch-video workflows.
Prefer native Hyperframes conventions over anything in `/showhow`.

Requirements:
- Every step is shown on the real product UI (rendered components, screenshots of the running app, or a faithful rebuild from the project's styles and copy).
- For every step: orient -> point (highlight + narration names the label) -> act (cursor/typing) -> result held until the narration ends.
- Within one screen, move between steps with camera moves (zoom/pan), not fades.
- Captions match the script verbatim and are timed to the voice.
- Keep all text readable in the final render; UI text that the narration names must be legible at the chosen zoom.
- Music never competes with the voice.
- Update videos: hook, change cards, tags and outro get /brag-style motion, SFX accents and beat locks; the UI demos inside each change stay calm and follow the teaching sequence.
- Run `hyperframes check` before render.
- Keep creation and rendering local. Remote or publishing workflows require a separate explicit user request.
```

The brief is the boundary: teaching content, steps, labels and audio levels belong to `/showhow`; composition implementation belongs to Hyperframes.

---

## Building the screens

If you render the project's own components or screenshot the running app:

- Use fictional data everywhere (see the secrets rule in step 1). Seed it through the app's own fixtures, mocks, or a local-only test account on a dev server; never sign into production with real data to capture screens.
- Capture at the video's resolution or 2x, so zooms stay sharp.
- Hide dev-only chrome (devtools, debug banners, browser UI) unless showing the browser is the point.
- Keep one screenshot per step state, named `step-NN-<state>.png` in `composition/assets/screens/`.

Put the video's own chrome colors (backgrounds, title and card fills, tags, counters, rings, ripples, fades) in one `:root` block of CSS variables taken from the product theme, and use only `var(--...)` below it, so a retheme is one edit.
Pass the same accent to `bake_highlights.py` as `color`.

For a desktop app whose frontend is a web SPA, render the frontend in a browser with its API calls mocked.
If the app needs a backend you cannot run, rebuild the screens from its components and styles instead.

## Place highlights and the cursor by element, not by pixels

Hand-computed ring and cursor coordinates drift once fonts load and layouts settle, and put rings in the wrong place.
Give every highlight or click target an `id`, and measure it once inside `document.fonts.ready`, while building the timeline:

```js
// Layout box of an element in root pixels, ignoring transforms. Call after fonts load.
function R(sel, p = 6) {
  let el = document.querySelector(sel);
  const w = el.offsetWidth, h = el.offsetHeight;
  let x = 0, y = 0;
  while (el && el.id !== "root") { x += el.offsetLeft; y += el.offsetTop; el = el.offsetParent; }
  return [x - p, y - p, w + 2 * p, h + 2 * p];
}
// dy: known growth of content above the target by time t (it isn't laid out yet when you measure).
const ring = (t, sel, d, p = 6, dy = 0) => {
  const [x, y, width, height] = R(sel, p);
  tl.set("#ring", { x, y: y + dy, width, height, opacity: 0 }, t);
  tl.to("#ring", { opacity: 1, duration: 0.25 }, t);
  tl.to("#ring", { opacity: 0, duration: 0.15 }, t + d);
};
// Cursor tip onto the centre of the target (adjust the offset to your arrow's tip).
const move = (t, sel, d = 0.6, dy = 0) => {
  const r = R(sel, 0);
  tl.to("#cur", { x: r[0] + r[2] / 2 - 8, y: r[1] + r[3] / 2 - 5 + dy, duration: d, ease: "power2.inOut" }, t);
};
```

- Measure eagerly, once, inside `document.fonts.ready` before building the timeline - never with function values (`x: () => ...`). `check` flags those as `gsap_function_value_hazard`: each render worker initializes tweens on its own and gets a different answer once layout animates.
- Measurement sees the layout at build time. When something above a target grows later (a file chip row opening above the text box), add the known growth as a `y` offset for targets below it.
- Put every element's starting state (hidden, offset, unselected) in CSS. A `tl.set` at time 0 does not show on frame 0.
- `offsetLeft`/`offsetTop` ignore GSAP transforms, so an element's entrance slide doesn't shift its ring. If the element's container is still moving at ring time, ring after it settles.
- Give targets explicit sizes where their box would otherwise stretch (a full-width row when you mean the button in it).

## Screenshot videos: bake rings into the stills

When the screens are screenshots, don't animate DOM ring divs over them.
Hyperframes has dropped such overlays from the rendered mp4 deterministically (any worker count, software GPU, static dedup off) while `snapshot` and plain Chrome showed them correctly.
Image swaps always rendered, so draw the ring into a copy of the still and fade that copy in over the clean one:

1. Record each ring as `{ t, d, screen, x, y, w, h, pad, zoom }` instead of emitting tweens, and each screen change as `{ t, name, fade }`; `zoom` is the camera's on-screen scale at `t`, so the stroke looks the same at any zoom.
2. Write them as a timeline spec (`rings` + `shows`, format in the script's docstring) and run `uv run --project <skill-dir>/scripts <skill-dir>/scripts/bake_highlights.py work/rings.json`.
   The script cuts each screen's time at every ring start and end, bakes one still per span (overlapping rings share a still), clamps a ring that outlives its screen to that cut, compares times in whole centiseconds, and fails on a ring that lands in no span, a ring on the wrong screen, or an id that isn't a CSS-safe selector.
   Don't re-implement this in the build script: float noise in hand-written span code dropped a ring before.
3. Read `work/rings.overlays.json` and put one `<img id="img-<id>">` per entry above the clean screens in `#world`.
   Fade it in at `in` over `in_dur` and out at `out` over `out_dur`.
4. Copy the ringed stills (`src` in each entry, relative to the spec) into the composition's assets.

Cursor and click ripples can stay DOM elements; give each ripple its own element.

## Every tween is a `fromTo`

Write every tween as `tl.fromTo(sel, from, { ..., immediateRender: false }, t)` and give every highlight or ripple its own element.
A pooled element re-tweened with `tl.to` picks up whatever state the last seek left, and render workers seek out of order.

## Overlays keep the viewer oriented

Dialogs, sheets and menus open **below the app header**, so the step counter stays visible in every frame.
Dim only the content area under a sheet, not the header.

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

For update videos (`release` style), sync the non-demo moments like /brag does.
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
- [ ] No real personal data, hostnames, IDs or secrets appear anywhere.
- [ ] Total duration is within the mode limits.
- [ ] `hyperframes check` passes, or any blocker is documented for the user.
