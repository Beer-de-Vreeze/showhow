# Step 2: Script and storyboard

Write `<output-dir>/showhow-plan.md`.
This is the teaching contract for the whole video: the script, the steps, and what the viewer sees at every moment.

The plan specifies what the video must teach and show.
It does not prescribe Hyperframes implementation details; Hyperframes decides those from the brief in Step 3.

## Create the output directory

```bash
mkdir -p <output-dir>
```

## Write the script first

The narration sets the pace of an instructional video, so write it before the storyboard.

- **Second person, present tense.** "Open **Projects** and click **Add knowledge**."
- **Name controls by their exact label**, in bold in the plan so they are easy to check against the UI.
- **One sentence per action**, plus at most one sentence of why or what happens.
- **Short sentences.** 8-16 words. No nested clauses. TTS reads lists and parentheses badly.
- **Write for the ear.** Spell out symbols and abbreviations the way they should be said ("two point four", not "2.4.0" if the TTS stumbles on it).
- **No filler.** No "In this video we're going to...", no "simply", no "just", no "easily".
- Speaking rate: plan about 2.5 words per second (150 wpm). Every scene's duration is at least its narration length plus 0.5-1.0s of hold.

With `--no-voice`, the same script becomes the caption text; plan about 0.35s per word of reading time instead.

## Structure of showhow-plan.md

```markdown
# Showhow Plan: [Title]

## Mode
[howto / update / general] - [task, topic, or release and range]

## Goal
[howto and general: "After this video you can ..." (or "... you know how ..." for a topic) / update: "What's new in [version]: ..."]

## Audience
[who, what they already know]

## Before you start
[prerequisites, or "none"]

## Style
- Preset: [one of the 11 styles in tones.md]
- Theme: [frame preset name, or "product theme"]
- Voice: [Kokoro voice id, default `af_heart`]
- Direction: [freeform phrase, inferred or user-provided]
- Interpretation: [one sentence on pacing, voice and visual energy]

## Format: [landscape / vertical / square] - [width]x[height]
## Target duration: [seconds, from the script word count]

## Visual identity (from the project; general mode: from the preset)
- Background / surface / text / muted / accent / border: [exact values]
- Display font / body font: [names]
- Theme: [theme id, e.g. `light`] - background [value], accent [value] (brand/default theme, not a fixture's)

## Fictional data substitutions
- [real kind of data] -> [stand-in used on screen]

## Sources (outside steps and general mode only)
- [step or point] - [URL, user file or screenshot], read [date]
- Images: [file] - [author, license, URL]; attribution needed: [yes/no]

## Unverified
- [labels or facts you could not confirm, or "none"]

## Narration script
[Full script, one paragraph per scene, labels in **bold**.]

## Storyboard

### Scene 1 - [name] - [duration]s
Source: [code / outside]
Screen: [which real screen / component is shown, and its state]
Counter: [e.g. "Step 1 of 4", or none]
Highlight: [the exact element that gets the ring / spotlight / zoom, and when]
Action: [cursor click / typing "value" / select option / drag, or none]
Result: [what visibly changes after the action]
Narration: [the lines for this scene]
Caption: [same as narration, split into phrases of max ~7 words]
On-screen text: [title cards or labels, if any]
Audio: [click / typing / none; music level]
Transition: [cut / soft fade / slide / zoom-out] -> Scene 2

### Scene 2 - ...

## Chapters
00:00 [Intro]
00:05 [Step 1 - ...]
...

## Written companion (draft)
[Numbered steps in text form; becomes showhow.md in Step 4.]
```

## Scene structure per mode

### howto

| Scene | Purpose | Typical duration |
|---|---|---|
| Outcome | Title + one line: what you'll be able to do. Show the finished result briefly if it is visual. | 3-5s |
| Before you start | Prerequisites, only if any. | 3-5s |
| Step 1..N | One action each: point, act, show the result. | 6-15s each |
| Result | The end state, clearly visible, with where to find it later. | 3-6s |
| Recap | 3-5 word summary of the steps as a checklist, or the next thing to try. | 3-5s |

### update

| Scene | Purpose | Typical duration |
|---|---|---|
| Title | "What's new in [product] [version]" and the change list as a preview. | 3-5s |
| Change 1..N | What is new (one line) -> where it lives (navigate there) -> show it in 1-2 actions -> why it matters. | 10-20s each |
| How to get it | Update prompt, restart, or "it's already there". Plus where to learn more. | 3-5s |

## Showing the product

Every step must be shown on the real UI.
Options, in preferred order:

1. **Render the real components** from the project's source with fictional data, in the state each step needs. Most faithful, and scenes stay editable.
2. **Screenshot the running app** (dev server in a browser, with fictional data) per step and animate on top: highlight, cursor, zoom. Good when the components are hard to render in isolation.
3. **Rebuild the screen in HTML/CSS** from the project's own styles and exact copy. Use when neither of the above works.

Never use abstract diagrams, stock icons or generic mock-ups for a step that has a real screen.
A simple diagram is allowed only for a concept with no screen (e.g. "knowledge is shared with everyone in the project").

## Pointing and highlighting

For every step, plan the teaching sequence explicitly:

1. **Orient** - the screen is shown wide enough that the viewer knows where they are (sidebar, header visible).
2. **Point** - the target control gets a highlight (ring, spotlight dim, or a slow zoom toward it). The narration names the label at the same moment.
3. **Act** - the cursor moves to it and clicks, or the text types in. Cursor moves are smooth and take 0.5-0.8s.
4. **Result** - the change is visible; zoom back out if you zoomed in, so the viewer sees the context of the result.

Small controls (icons, menu items) need a zoom of 1.5-2.5x in landscape and more in vertical.
Never highlight more than one control at a time.

## Captions

Captions are on by default.
Place them in a fixed band (bottom in landscape, lower third in vertical) and move them to the top for a scene if the highlighted target sits in that band.
Max two lines, max ~42 characters per line.

## Duration check

Sum the scene durations.
Check against the mode limits in `SKILL.md`.
If over the hard limit: cut the least important step or change, or split the video.
If a step's narration needs more than ~15s, the step is too big; split it.

## Audio planning

- **Voice** leads. Everything else sits under it.
- **Music**: a quiet bed (see `audio.md` for levels) or none for `clean` how-tos where it would distract. `release` and the energy styles plan music like /brag: louder on the hook, bridges and outro, ducked under the voice, with strong cues picked for the hook, change cards and outro.
- **SFX (howto)**: mainly for visible actions - a soft click on each click, soft key ticks on typing, one gentle accent on the final result.
- **SFX (update)**: plan them like /brag around the demos - a soft hit on the hook reveal, card sounds as each change card arrives, a tick for each "New"/"Fixed" tag, a payoff on the outro (a bell is fine). Inside the UI demo, clicks and typing only.
- The full library is available (see `audio.md`); note the moment and intent in the plan, not the filename.

Do not pick exact SFX filenames in the plan; Hyperframes picks them after the animation exists.

## Transition vocabulary

| Style | Preferred transitions |
|---|---|
| `clean` | Cut, or soft fade (0.3s); zoom in/out within a screen |
| `friendly` | Soft fade, gentle slide |
| `release` | Slide or wipe between changes, cut within a change |
| `quick-tip` | Cut |
| Energy styles (`playful`, `polished`, `yc-parody`, `chaotic`, `deadpan`, `cinematic`, `app-store`) | The style's own **Transitions** line in tones.md between scenes; camera moves within a screen as always |

Transitions within one screen (same app view, different step) should be camera moves (zoom/pan), not fades: the viewer must see it is the same screen.
