# Audio reference

All SFX are CC0 (Kenney.nl, public domain).

In an instructional video the **voice leads**.
Music and SFX support it and must never compete with it.
Use a quiet music bed and action-matched SFX by default, unless the user passes `--no-music` / `--no-sfx`, the assets are missing, or the style says none (`clean` may go without music).

Levels with narration:

| Layer | Volume | Notes |
|---|---|---|
| Narration | 1.0 | One clip per scene, own track |
| Music under voice | 0.08-0.14 | Duck to this whenever a narration clip plays |
| Music with no voice (title, outro, `--no-voice`) | 0.25-0.35 | `release` goes to 0.35-0.4 on the hook, change-to-change bridges and outro |
| SFX (clicks, typing) | 0.35-0.55 | Soft; they confirm an action, they don't announce it |
| SFX accents in `release` (reveals, change cards, payoffs) | 0.55-0.8 | Between narration lines, or at most 0.5 under the voice |
| Final result accent | 0.5-0.65 | One per video |

---

## Audio-reactive visuals

Off by default for how-tos: nothing should move except what the viewer needs to look at.
`release` style uses it like /brag does: a subtle audio-reactive treatment on the hook, the change cards and the outro, never on the UI while a step is being shown. This does not mean beat detection. It means Hyperframes can pre-extract per-frame audio data and use RMS/frequency-band energy to modulate existing visual elements.

Good uses:
- Hero glow or sky warmth breathes slightly with RMS
- Product card, phone, or metric panel gains subtle presence on bass
- Title, quote, or logo gets a soft treble glow on stronger musical moments
- Background depth, vignette, or light layer gently swells with the bed

Avoid:
- Waveform displays, equalizer bars, musical notes, or generic visualizer graphics
- Strobing, heavy pulsing, or text scaling that hurts readability
- Treating audio-reactivity as a substitute for good scene timing
- Claiming exact beat/BPM sync unless a real beat detector is available

Suggested plan notation:
```
Audio-reactive treatment: subtle; use music RMS/bass to make the hero glow and product card presence breathe. No waveform/equalizer visuals.
```

Hyperframes implementation note: follow the audio-reactive guidance owned by the `hyperframes-creative` skill (let that skill locate its own files), to extract per-frame audio data and sample it synchronously inside the composition timeline. The extraction helper ships with that skill - `/showhow` does not provide it, so don't hardcode a path to it.

---

## Asset paths

All paths below are relative to `<skill-dir>`, this skill's own directory (see "Skill directory" in `SKILL.md`). It differs by install method, so resolve it rather than assuming `~/.claude/skills/showhow/`.

SFX live under `<skill-dir>/assets/sfx/{casino,impact,interface,ui}/`, and the individual keypress set under `<skill-dir>/assets/sfx/keyboard/`.

Music lives at `<skill-dir>/assets/music/`.

Bundled music cue presets live beside the music:

```text
<skill-dir>/assets/music/cues/<track-stem>.music-cues.md
<skill-dir>/assets/music/cues/<track-stem>.music-cues.json
```

SFX analysis lives beside the SFX library:

```text
<skill-dir>/assets/sfx/sfx-analysis.md
<skill-dir>/assets/sfx/sfx-analysis.json
```

**Critical: copy audio files into the composition project before rendering.** Hyperframes validates and serves assets from the composition directory. Always copy the files you need into `<output-dir>/composition/assets/` first:

```bash
# Create local asset dirs
mkdir -p <output-dir>/composition/assets/sfx/interface <output-dir>/composition/assets/sfx/impact <output-dir>/composition/assets/sfx/casino <output-dir>/composition/assets/sfx/ui
mkdir -p <output-dir>/composition/assets/music

# Copy only the files you plan to use (not the entire library)
cp <skill-dir>/assets/sfx/interface/drop_001.ogg <output-dir>/composition/assets/sfx/interface/
cp <skill-dir>/assets/sfx/impact/impactSoft_medium_000.ogg <output-dir>/composition/assets/sfx/impact/
cp <skill-dir>/assets/music/happy-beats-business-moves-vol-1-by-ende-dot-app.mp3 <output-dir>/composition/assets/music/
```

Then in the composition HTML, paths are **relative to the `composition/` directory**:
```
assets/sfx/interface/drop_001.ogg
assets/sfx/impact/impactSoft_medium_000.ogg
assets/music/happy-beats-business-moves-vol-1-by-ende-dot-app.mp3
```

Never use absolute paths (starting with `/Users/...`) - they will silently fail in the renderer.

---

## SFX library - approved files

The family SFX (casino, impact, interface, ui) live directly under `sfx/`; the individual keypress set lives in `sfx/keyboard/`.

Read `sfx-analysis.md` before choosing files - it lists safer picks by use case and flags files with high-frequency risk. Prefer low/medium HF risk for polished and repeated moments; reserve high-risk files for tiny isolated accents or chaotic tones.

### `keyboard/` - Individual keypress sounds

32 CC0 single keypress WAV files (`keypress-001.wav` through `keypress-032.wav`). Each is a distinct key sound at a slightly different velocity and character. Use these for per-character typing animations - randomize across the set so repeated characters don't sound robotic.

**Source:** [Keyboard Soundpack #1](https://opengameart.org/content/keyboard-soundpack-1-typing-and-single-keystrokes) by unicae_games - CC0

### `interface/` - UI sounds

| Files | Character | Use for |
|---|---|---|
| `click_001–005.ogg` | Sharp, precise | Button tap, CTA, any tap action |
| `glitch_002.ogg`, `glitch_004.ogg` | Digital distortion | Tech/AI moment, chaotic accent |
| `error_005–006.ogg` | Negative buzz | Comedic fail, wrong answer |
| `switch_001–002.ogg`, `switch_004–007.ogg` | Toggle switch | Feature switching on, binary state |
| `drop_001–003.ogg` | Soft drop | Element landing, gentle placement |
| `bong_001.ogg` | Deep bell | Success, logo payoff, a hero moment |
| `select_008.ogg` | Selection click | Navigation, item focus |

### `impact/` - Impact sounds

More physical and cinematic. Excellent for big moments and transitions.

| Files | Character | Use for |
|---|---|---|
| `impactSoft_medium_000–004.ogg` | Medium soft thud | Major reveal, hard transition - safest family |
| `impactSoft_heavy_000–004.ogg` | Heavy soft thud | Comedic bonk, weight, silly moment |
| `impactBell_heavy_000.ogg`, `_003.ogg`, `_004.ogg` | Deep resonant bell | Cinematic reveal, logo slam, dramatic moment, success |
| `impactPunch_heavy_000–004.ogg` | Heavy punch | Aggressive beat, chaotic tone |
| `impactPunch_medium_000–004.ogg` | Medium punch | Impact emphasis |
| `impactWood_light_000–004.ogg` | Light wood knock | Warm, organic tap |
| `impactWood_medium_000–004.ogg` | Wood knock | Warmer accent |
| `impactWood_heavy_000–004.ogg` | Heavy wood hit | Cinematic weight |
| `impactPlank_medium_000–004.ogg` | Plank slap | Comic physical moment |
| `impactPlate_heavy_000–004.ogg` | Metal plate slam | Big hit, aggressive |
| `impactPlate_light_000–004.ogg` | Light metal plate | Notification, crisp accent |
| `impactPlate_medium_000–004.ogg` | Medium plate | Mid-weight accent |
| `impactTin_medium_000–004.ogg` | Tin can hit | Quirky, lo-fi moment |
| `impactGeneric_light_000–004.ogg` | Generic light hit | Versatile small accent |
| `impactMetal_medium_000–004.ogg` | Metal tap | Medium accent |
| `impactMetal_heavy_000.ogg`, `_002.ogg`, `_004.ogg` | Heavy metal clang | Aggressive hit |
| `impactMetal_light_002–003.ogg` | Light metal ping | Small notification |
| `impactGlass_light_001–003.ogg` | Light glass clink | Sparkle, delicate achievement |
| `impactGlass_medium_000.ogg`, `_002.ogg`, `_004.ogg` | Glass tap | Mid-weight accent |
| `impactGlass_heavy_002.ogg` | Glass shatter | Chaotic hit |
| `impactMining_001.ogg` | Mining strike | Industrial, heavy |
| `footstep_carpet_*`, `footstep_concrete_*`, `footstep_grass_*`, `footstep_snow_*`, `footstep_wood_*` (000-004) | Footsteps on that surface | Walking to a device, a room or a station in physical how-tos and topic videos; match the surface on screen |

### `casino/` - Card and chip sounds

Specific but great for swipe/deal/stack moments.

| Files | Character | Use for |
|---|---|---|
| `card-slide-1–8.ogg` | Card sliding | Swipe action, content sliding in |
| `card-place-1–4.ogg` | Card placement | Item landing, card appearing |
| `card-fan-1–2.ogg` | Cards fanning | Multiple items appearing in sequence |
| `card-shove-1–4.ogg` | Card shoved | Forceful card motion |
| `card-shuffle.ogg` | Shuffle | Transition with motion |
| `chip-lay-1–3.ogg` | Chip placed | Metric placed/confirmed |
| `chips-stack-1–6.ogg` | Chips stacking | Counter incrementing, stacking animation |
| `chips-collide-1–4.ogg` | Chips clinking | Celebratory, success with weight |
| `chips-handle-1–4.ogg`, `chips-handle-6.ogg` | Chips handled | Casual chip movement |
| `dice-shake-1–3.ogg` | Dice shaking | Build-up, anticipation |
| `dice-grab-1–2.ogg` | Dice grabbed | Pick up, quick action |
| `dice-throw-1–3.ogg` | Dice thrown | Chaotic/random moment |
| `die-throw-1–4.ogg` | Single die thrown | Lighter random accent |
| `cards-pack-open-1–2.ogg` | Pack opening | Reveal, product launch moment |

### `ui/` - Clicks and switches

| Files | Character | Use for |
|---|---|---|
| `click1–5.ogg` | Various click tones | Button tap, cleaner than interface clicks |
| `mouseclick1.ogg` | Mouse click | Simulated cursor interaction |
| `rollover1–2.ogg`, `rollover4–5.ogg` | Hover/rollover | Subtle hover feedback, very soft accent |
| `switch1–38.ogg` (most variants) | Switch variants | Toggle, mode change - pick by character |

---

## Style → SFX approach

| Style | Approach |
|---|---|
| `clean` | `ui/mouseclick1` or `ui/click*` on each simulated click, sparse `keyboard/` ticks on typing, one `interface/drop_001` on the final result. Nothing else. |
| `friendly` | As `clean`, plus `interface/drop_*` when a new panel or dialog opens. |
| `release` | Brag energy around the demos: a soft reveal hit on the hook (`impactSoft_medium_*`), card sounds (`casino/card-slide-*`, `card-place-*`, `card-fan-*`) as change cards arrive, `interface/drop_*` or `chips-stack-*` for "New"/"Fixed" tags and counters, a light payoff (`chips-collide-*` or `interface/drop_*`) on the outro. Inside a change's UI demo, back to `clean`: clicks and typing. |
| `quick-tip` | Clicks and typing only. |
| `playful` | 3-5 accents: `interface/drop_*` or `click_*` for pop-ins, `impactBell_heavy_000` for success, `impactSoft_medium_*` for reveals. |
| `polished` | 2-3 very subtle accents: `interface/drop_001` for a gentle reveal. Nothing aggressive. |
| `yc-parody` | 2-3 restrained cues: one dry reveal hit (`impactSoft_medium_*`), one card accent, one payoff. |
| `chaotic` | Dense, on the beat: `impactPunch_heavy_*`, `interface/glitch_*`, `casino/dice-throw-*`, `impactMetal_heavy_*`. Stacked and loud hits go between narration lines; a cut inside a line (tones.md, Beats) gets one short, light cue at 0.5-0.6 so every word stays clear. |
| `deadpan` | Very sparse: a quiet bed plus 1-2 dry cues. |
| `cinematic` | 2-3 big ones: `impactBell_heavy_000` or `_004` for the hero moment, `impactSoft_medium_*` for the reveal, `impactBell_heavy_003` for the outro. |
| `app-store` | A consistent light layer: `interface/drop_*` or `click_*` per card, `impactBell_heavy_000` on the outro, all at 0.65-0.75. |

In every energy style, steps inside a UI demo go back to `clean` (clicks and typing).

The whole library is available in every style; the table is the default posture, not a ban list.
Use louder or odder sounds (`impactPunch_*`, `glitch_*`, `dice-*`, `error_*`) when a moment calls for it: `glitch_*` for an AI or tech moment in an update, `error_*` softly when a step shows a validation error or a fixed bug's old behavior, `dice-*` for a playful shuffle between changes.
Two rules hold everywhere: never mask a narrated word, and keep one coherent sonic palette per video.

---

## Moment → sound heuristics

Use these as examples for Hyperframes, not a fixed recipe. Sound should reinforce the edit, not call attention to itself.

| Moment type | Good sound families | Notes |
|---|---|---|
| Sequential cards/items opening | `casino/card-slide-*`, `casino/card-place-*`, `casino/card-fan-*`, `interface/drop_*` | Match the gesture. A card stack uses card sounds; a soft product grid can use drop sounds. For dense sequences, accent the first, last, or rhythmically important items only. |
| Big reveal / payoff | `impact/impactBell_heavy_000`, `_003`, or `_004`, `impact/impactSoft_medium_*`, `interface/bong_001`, `interface/drop_*` | One short announcement-style cue when the reveal lands. Keep it brief. |
| Text popping / typed copy | `keyboard/keypress-*.wav` (randomized), `interface/drop_*` | For per-character typing animations, pick a random file from `keyboard/` for each character. For soft label pop-ins, use `drop_001` or `drop_002`. Thin out or skip when copy is dense. |
| Simulated user action | `interface/click_*`, `interface/select_008`, `interface/switch_*`, `ui/mouseclick1`, `ui/switch*` | Use interaction sounds when the video shows a cursor, tap, button, toggle, swipe, or selection. Match the visible action. |
| Success / completion | `impact/impactBell_heavy_000`, `_003`, or `_004`, `casino/chips-collide-*`, `interface/drop_*` | Positive accent for approvals, matches, metrics, completed flows, or final CTAs. |
| Chaotic or comedic beat | `interface/glitch_002`, `interface/glitch_004`, `interface/error_005–006`, `impact/impactPunch_heavy_*`, `casino/dice-throw-*` | Update videos, sparingly: a fixed bug's "before", an AI moment, a playful bridge. Never loud under narration; `chaotic` cuts inside a line use one short, light cue. |

When in doubt, pick fewer cues with better timing. Prefer a coherent sonic palette for the whole video over a grab bag of cute sounds.

---

## Timing rules

These rules apply when Hyperframes is implementing the composition and the motion timings are known:

- Align SFX to the **start** of the animation, not the end
- Entry pop: 0.0–0.1s before the element's first visible frame
- Transition: at the transition start time
- Success ding: at the moment the final result is fully visible
- Click: at the frame the cursor presses, not when it arrives
- Typing: tick on every 1-2 characters, never louder than the voice
- For staggered elements: usually accent the first, final, or strongest beat; only score every item when that rhythm is intentional and still feels clean

Composition notation:
```
Scene 3 - Step 2: Add a file - 9.4s
  Narration scene-03.wav at 0.3s     ->  music ducks to 0.1 at 0.1s
  Ring on "Add knowledge" at 1.2s    ->  (no SFX, the voice names it)
  Cursor presses at 2.6s             ->  SFX: ui/mouseclick1 at 2.6s
  File dialog slides in at 2.8s      ->  SFX: interface/drop_001 at 2.8s, volume 0.4
  Filename types in 3.4-4.2s         ->  SFX: keyboard/keypress-* on every 2nd character, volume 0.35
```

---

## Music

### Available tracks

All tracks are "Happy Beats / Business Moves" by ende.app. Upbeat, clean, corporate-adjacent. Keep them quiet under narration.

| Filename | Duration | Character | Best for |
|---|---|---|---|
| `happy-beats-business-moves-vol-1-by-ende-dot-app.mp3` | 2:44 | Full upbeat track, most energetic | `release` (long updates) |
| `happy-beats-business-moves-vol-9-by-ende-dot-app.mp3` | 1:54 | Mid-energy, slightly more laid-back | `friendly`, `release` |
| `happy-beats-business-moves-vol-10-by-ende-dot-app.mp3` | 1:00 | Compact loop, punchy | `quick-tip` |
| `happy-beats-business-moves-vol-11-by-ende-dot-app.mp3` | 1:28 | Warm and business-y | `friendly` |
| `happy-beats-business-moves-vol-12-by-ende-dot-app.mp3` | 1:58 | Steady and clean | `clean`, long how-tos |

The bundled tracks are by Sascha Ende ([ende.app](https://ende.app/en)), licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
When a video uses one, add a line to `credits.txt`: `Music: "Happy Beats / Business Moves Vol. <n>" by Sascha Ende (ende.app), CC BY 4.0, https://creativecommons.org/licenses/by/4.0/`.
Also credit it in the video itself, so the credit travels with the file: the short line `Music: Sascha Ende (ende.app), CC BY 4.0` on the outro (step-3-compose.md, Credit line).

The bundled tracks are all upbeat business music: they suit the teaching styles, `playful`, `polished` and `app-store`.
For `cinematic`, `deadpan`, `chaotic` or `yc-parody`, generate a bed with MusicGen (Generated bed, below) in the style's mood; if generation fails, use the closest bundled track and say so.

### Generated bed (MusicGen)

Use it for `cinematic`, `deadpan`, `chaotic` and `yc-parody`, and whenever the user asks for generated or original music; every other style uses a bundled track. It runs locally with the media-use audio engine (MusicGen via `HYPERFRAMES_PYTHON`; nothing leaves the machine).
From `<output-dir>/composition`:

```bash
cat > ../work/bgm_request.json <<'EOF'
{"lines": [], "bgm": {"mode": "generate", "prompt": "uplifting corporate tech, bright modern piano with synth pads, 108 bpm"}}
EOF
node <media-use-dir>/audio/scripts/audio.mjs --request ../work/bgm_request.json --hyperframes . --out ../work/bgm_meta.json --only bgm
node <media-use-dir>/audio/scripts/wait-bgm.mjs --audio-meta ../work/bgm_meta.json --hyperframes . --timeout-ms 600000 --out ../work/bgm_status.json
```

`<media-use-dir>` is the installed `media-use` skill (`~/.claude/skills/media-use`).
Run both commands in one shell call: the generator runs detached, and some agent shells kill leftover processes when a call ends.
It writes `assets/bgm/track.wav`: a 30s clip, about 5 minutes on a laptop CPU.
Continue only when `bgm_status.json` says `"status": "ready"`.
If it failed within seconds with an empty log, run both commands once more (seen once on Windows, cause unknown); if it fails again, fall back to a bundled track and tell the user.
Put the mood in the prompt (MusicGen ignores BPM and scale settings), listen to it before using it, and loop it like any short track (below).
Then run the beat analysis on it like a custom track.

If the video is longer than the track, loop it with a crossfade at a phrase boundary or fade it out under the last narration; never let it cut off abruptly.

### In a composition

After copying files (see Asset paths above), reference them with relative paths from `composition/`:

```html
<audio id="bg-music" data-start="0" data-duration="[total]" data-track-index="10" data-volume="0.35" src="assets/music/happy-beats-business-moves-vol-1-by-ende-dot-app.mp3"></audio>
```

Volumes: see the levels table at the top of this file. Never above 0.4 for music in an instructional video.

### Ducking under the voice

Keep the music at its bed level and duck it to 0.08-0.14 for each narration clip (0.2s ramp down just before the clip, 0.4s ramp up after), using the best Hyperframes-supported way to automate volume.
If ducking isn't possible, keep the music at 0.08-0.12 for the whole video.

If the music file doesn't exist, skip it and notify the user after rendering.

### Beat and cue sources

Beat sync needs a cue source. Three are available - use the richest one the environment supports. Beat sync now works on **any** track, not just bundled ones. The two any-track methods (2 and 3) have orthogonal requirements - option 2 needs Python, option 3 needs a recent Hyperframes - so when one is unavailable the other usually covers it.

1. **Bundled track → precomputed preset (richest, instant, no deps).** The bundled tracks ship with cue metadata. Read the matching markdown summary, and pass the JSON path in `composition-brief.md`:

```text
<skill-dir>/assets/music/cues/<track-stem>.music-cues.md
<skill-dir>/assets/music/cues/<track-stem>.music-cues.json
```

2. **Any track → extended analysis (richest for custom tracks; needs Python, any Hyperframes version).** For a custom track - or to refresh a bundled one - run `analyze_music_cues.py` on the audio file. It produces the same rich cue JSON/Markdown for any track. Run it via `uv`, which auto-provisions the deps (`librosa`, `numpy`, `scipy`, `soundfile`) from `<skill-dir>/scripts/pyproject.toml` - no manual `pip install` needed:

```bash
uv run --project <skill-dir>/scripts \
  python <skill-dir>/scripts/analyze_music_cues.py <track>.mp3 \
  --output-json <output-dir>/composition/assets/music/cues/<stem>.music-cues.json \
  --output-md  <output-dir>/composition/assets/music/cues/<stem>.music-cues.md
```

This is the fallback when `hyperframes beats` (option 3) is unavailable - e.g. an older pinned Hyperframes. If neither `uv` nor the Python deps are available, use option 3 instead.

3. **Any track → `hyperframes beats` (simple, no Python; needs Hyperframes ≥ 0.6.99).** After the music is wired into the composition, run:

```bash
npx hyperframes beats <output-dir>/composition
```

It writes a per-track beat file: a beat grid with per-beat timing and a normalized `strength` (0-1), but no separate `strongCues` array - so derive "strong" beats by taking the highest-`strength` ones. (See the current hyperframes-cli `beats` guidance for the exact output path.) `beats` was added in Hyperframes 0.6.99; on an older pinned install it won't exist - fall back to option 2 (the script), or to the `unavailable` note below.

The preset and `analyze_music_cues.py` share the rich schema:

- `duration`, `tempo`
- `beats`: beat-grid points with `time` and normalized `intensity`
- `strongCues`: highest-value landing moments with `time`, `intensity`, and `kind` (`strong_beat` / `onset_peak`)
- `scoring`: feature and normalization metadata

`hyperframes beats` is the simpler floor: a plain beat grid with a per-beat strength, no strong-cue array.

Planning rules (apply to whichever source you have):

- Use cue metadata to bias timing, not control it.
- Major reveals may move toward strong cues within about `±0.15s`.
- Smaller entrances may align to nearby beat points within about `±0.10s`.
- `release` style uses cues like /brag: lock the hook, each change-card reveal and the outro to strong cues (±0.15s), and snap sequential tags/counters to the beat grid (±0.10s). How-tos use cues only for the title and outro, if at all.
- Narrated demo scenes follow the voice, never the beat.
- Ignore cues when they harm copy readability, scene pacing, or the product story.

Cue/beat metadata is not a substitute for Hyperframes audio-reactive visuals: it helps with beat/swell timing; audio-reactive data helps subtle visual properties breathe with the music.

If no source is available (no preset, no Python deps, and `hyperframes beats` not run), write:

```text
Music cue guidance: unavailable; continue without beat/cue sync.
```

### Adding SFX elements

Put narration on low tracks (e.g. 1-9, alternating per scene), the music bed at 10, and give each overlapping SFX its own ascending track-index from 11 up. Never share a track-index between overlapping audio.

```html
<audio id="sfx-1" data-start="0.2" data-duration="1" data-track-index="11" data-volume="0.80" src="assets/sfx/interface/drop_001.ogg"></audio>
```

Set each SFX clip's `data-duration` to the file's real length (`ffprobe -v error -show_entries format=duration -of csv=p=0 <file>`); a longer slot makes `check` warn.

Wire each `<audio>` clip per the current hyperframes Data Attributes + Video/Audio contract (`data-track-index`, `data-volume`, `data-start`, `data-duration`). `/showhow` owns only the volume policy above and the track-allocation convention; Hyperframes owns the clip schema.
