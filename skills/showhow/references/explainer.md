# Explainer mode

An explainer is a narrated video about an idea, a mechanism, a place or a piece of history.
Every voiced sentence gets one visual, so the picture always follows the words.
It is the closest cousin of `general` mode: read `references/general.md` and reuse its rules by reference, not by copy.

Reused from `general.md` as they are:
- Sources, in order of trust, and "Never invent a label" (Step 1: Gather the facts).
- Topic image order and licensing, credits, and the "Shown as of" note for rebuilt third-party screens.
- Schematics for mechanisms, the 3D rule (never for UI, screens or charts), and honest charts in motion.
- The design system: pick a frame preset that fits the topic and copy its `FRAME.md` into `composition/frame.md`.

What this file replaces: the step shape, the counters and the "Now try it" ending.

## Script input

There are two inputs.

- **A pasted script** is narrated word for word.
  The only change allowed is respelling a word in the TTS input; captions, plan and companion keep the user's text.
  There is no approval stop for it: write `## Script source` as `pasted` and go on to the plan.
- **A topic** gets a drafted script under the script rules in `references/step-2-plan.md`, every fact tied to a source in `work/sources.md`.
  Write `## Script source` as `drafted`, show the script, and **stop 1**: wait for the user's approval before building anything.

A fact you can't source is written `[NEED: <what is missing>]` in the script, never guessed.
`plan_gates.py` fails P-need while any `[NEED` is left, so the video can't render with a hole in it; ask the user to fill each one.

## Shape

Outcome -> Name the parts -> one scene per voiced sentence, grouped into sections -> Recap.

| Scene | Purpose | Typical duration |
|---|---|---|
| Outcome | Title and one line: what you'll understand. Reads with the sound off. | 3-5s |
| Name the parts | One short scene: the 2-4 parts the explanation uses, each labelled on one picture with what it does in a few words (pre-training, `general.md` points shape). | 5-8s |
| Sentence scenes | One voiced sentence, one visual, as long as the narration plus 0.5-1.0s of hold. No step minimum. | 3-10s each |
| Recap | The main idea again in one picture and one or two sentences. | 4-8s |

- No step counter anywhere ("2 of 5" turns an explainer into a checklist).
- Group the sentence scenes into 2-4 sections; each section is a chapter in `chapters.txt`, named for what it explains.
- Target 60-120s, hard limit 180s.
  Over 120s is a warning; over 180s fails P-time: cut sentences or split the video.
- Style `friendly` unless the user names another.
  Music is on by default, bundled and ducked under the voice (`references/audio.md`); `--no-music` wins.
- Readability, one-picture-per-point and "works muted" from the teaching laws still apply.

## Visual menu

Each voiced scene carries `Visual: <type>`, exactly one value from this table, and optionally `Params: {json}` for types that need numbers or names.
Parallax or other decorative motion is for the intro only; it never competes with an explanation.

| Type | Use it for | How it plays |
|---|---|---|
| `flow` | A process or sequence | Boxes and arrows that build line by line, in the order the voice says them |
| `chart` | Numbers and comparisons | Bars or lines from zero; axes first, then values (honest charts, `general.md`) |
| `map` | Where something is | Static map with a labelled locator for each place named |
| `photo` | The real thing | A licensed photo (`general.md`), cropped or slowly zoomed to the part being discussed |
| `card` | One number, name or quote | Big text, one idea, held until the sentence ends |
| `stroke-reveal` | A diagram or route built line by line | DrawSVG on paths, constant speed, connector before label (`motion-2d.md`) |
| `kinetic-type` | A definition, rule or phrase to remember | SplitText whole words out of a mask, 5 frames apart (`motion-2d.md`) |
| `data-anim` | A quantity changing | Counter tween with `onUpdate`/`textContent`, bars grown from their baseline (`motion-2d.md`) |
| `morph` | "A becomes B", or a match cut between scenes | MorphSVG between two paths, same position and size either side (`motion-2d.md`) |
| `flat-scene` | An abstract process as a concrete picture | Flat or isometric SVG from primitives, timeline stagger, MotionPath for travellers (`motion-2d.md`) |
| `parallax` | The intro scene only | Layers pushed at depth-scaled speeds (`motion-2d.md`); the gate rejects it anywhere but scene 1 |

The 2D motion rows have a recipe each in `references/motion-2d.md`.
Later releases add rows here (cutaway, globe, hero number); `VISUALS` in `scripts/plan_gates.py` is the single list the gate checks against, so a new type is one row here and one entry there.
A scene with no voice (a title, a hold) needs no `Visual:`.
Every fact shown in a visual is also spoken in that scene (P-described).

## Plan template additions

On top of `references/step-2-plan.md`:

- `## Mode` is `explainer`.
- `## Script source` is `pasted` or `drafted`.
- `## Formats` lists the formats to render; the default is all three (`landscape, vertical, square`); one name renders only that format.
- Each storyboard scene has `Visual:` and, when the type takes numbers or names, `Params:`; `Counter:` is `none`.
- `## Sources` and `## Unverified` stay, as in `general` mode.

## Gates

`uv run --project <skill-dir>/scripts <skill-dir>/scripts/plan_gates.py showhow-plan.md` runs after the plan and again with `--chapters` and `--video` after the render:

- **P-need:** no `[NEED` marker in the narration.
- **P-visual:** every voiced scene has exactly one known `Visual:`; an unknown type is named in the failure.
- **P-time:** under 180s; a total outside 60-120s passes with a warning.
- **P-end:** the last scene before the outro is a recap.
- **P-described:** as in every mode.
- There is no P-steps or P-action: explainers have no counters.

## Deliverables

As in other modes, with one change: `showhow.md` is the script as a short article, one heading per section with the section's narration as paragraphs, then a numbered **Sources** list (the URLs and user files from `work/sources.md`).
`chapters.txt` has one line per section.
