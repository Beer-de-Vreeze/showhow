# Style reference

Four styles, usable in every mode (`--style <name>`, or freeform direction like "calm like Apple support videos" that refines the nearest one).
Defaults: `clean` for howto and general, `release` for update.

Rules for every style:

- **Length follows the mode.** Scene lengths come from the narration and the mode limits in `SKILL.md`; every step lasts its narration plus the 0.5-1.0s result hold.
- **The teaching laws win.** Exact labels, one action per step, the counter, verbatim captions, and every on-screen label settled for 1.5s, in every style.
- **The style owns the frame, the steps stay clear.** Hook, title cards, transitions, typography and outro take the style; step narration keeps the script rules in `SKILL.md`.
- **Accessibility holds in every style** (`SKILL.md`, Teaching laws).

---

## `clean`

**Default for:** `howto`.

**Feel:** Neutral, precise, product documentation. The viewer is busy; respect their time.

**Voice:** Second person, present tense, calm. No jokes.
```
Open Projects and select the project you want to add knowledge to.
```

**Typography:** The product's own fonts. Title in medium weight, sentence case. Step counter small and muted.

**Pacing:** 6-12s per step. Hold every result for 0.5-1.0s after the narration, and about 2s of silence at a subtask boundary.

**Highlight:** Thin accent ring plus a subtle dim of the rest of the screen. Zoom only for small controls.

**Music:** None by default; a very quiet bed with `--music`.

**Transitions:** Cuts between screens, camera moves within a screen.

**Outro:** "Now try it" with a concrete example, then the product name.

---

## `friendly`

**Default for:** onboarding and first-time users.

**Feel:** Warm, encouraging, patient. Assumes nothing.

**Voice:** Second person, relaxed, reassures at tricky moments. Explains why a step matters in half a sentence.
```
Click Add knowledge. Anything you add here, the assistant can use in every chat in this project.
```

**Typography:** Slightly larger captions and title. Rounded highlight shapes if the product uses rounded corners.

**Pacing:** 8-15s per step. Longer holds on results, about 2s of silence at a subtask boundary. Never more than 5 steps; split otherwise.

**Highlight:** Soft glow or spotlight, slow zoom toward the target.

**Music:** None by default; a quiet warm bed with `--music`.

**Transitions:** Soft fades (0.4s) between screens, gentle camera moves within a screen.

**Outro:** "You're all set", then "Now try it" with a concrete example of where to use it next.

---

## `release`

**Default for:** `update`.

**Feel:** A launch video that also teaches. Punchy hook, energetic change cards, confident music and sound, then a calm, clear demo of each change on the real UI. The changes are the stars, not the adjectives.

**Voice:** "You can now...", "We fixed...". One plain sentence on what is new, one on why it matters.
```
You can now restore an earlier version of any prompt. Open the prompt, click Versions, and pick the one you want back.
```

**Typography:** Bold title card with the version number. A change counter ("2 of 3") and a short title per change.

**Hook:** The first 2-3 seconds earn the rest: the most visual new thing is already moving, with "What's new in [version]" as on-screen text, so it reads muted. The version number can slam in after that, then the change list as a preview.
The version slam may be the video's one 3D moment (a WebGL block from `npx hyperframes catalog --query "3d title" --json`, built per `../hyperframes/references/types/3d.md`); the change itself always stays on the real, flat UI.

**Pacing:** 10-20s per change. Fast, beat-locked transitions and card reveals between changes; normal step pacing inside the demo.

**Highlight:** Accent ring plus zoom. A "New" or "Fixed" tag pops onto each change card.

**Change card:** Each change opens with a short card (tag + title + one-line why), revealed on a strong music cue with a card or impact sound, then moves into the real UI demo.
Every promise on a card is pictured in its demo: a card that says "faster search" shows a search finishing (from taste-skill's "every headline promise pictured").
Each change shows a different screen or crop; no two changes open on the same view.

**Before/after (optional, for a "Fixed" or redesigned screen):** the old screen turns into the new one in place, adapted from unslop's story video by @heydamir (CC BY 4.0).
- Rebuild the old screen from the previous release's code (`git show <old-tag>:<path>`), never from memory; it is the real product at that version.
- One screen whose CSS values tween from old to new (padding, colour, radius, size); nothing swapped as a whole picture. Changes run as a wave, each element a few dozen milliseconds after the one above or left of it.
- Optional red marks on what changed for the first beat, at most three, gone before the narration names the result.
- About 3-6s inside that change, cropped close on the part that changes most.
- Add `Before/after style: unslop by @heydamir, CC BY 4.0, https://github.com/heydamir/unslop` to `credits.txt` and `unslop by @heydamir` to the outro credit line.

**Music:** Upbeat bed (vol-1 or vol-9), up on the hook, bridges and outro, ducked under the voice. Beat-locked hook, cards and outro. Subtle audio-reactive glow on cards and title allowed.

**SFX:** Full accents around the demos (reveal hits, card slides, tag ticks, payoff, bells allowed), clicks and typing inside the demos. See `audio.md`.

**Transitions:** Slide, wipe or zoom between changes; camera moves within a change.

**Outro:** The change list lands as a checklist with a tick per item, then how to get the update, on a final strong cue.

---

## `quick-tip`

**Default for:** one small trick, shortcut or setting; 20-40s total.

**Feel:** Fast but followable. One task, 1-3 actions.

**Voice:** Minimal. The goal in one sentence, then the actions, then done.
```
Tip: press Ctrl K to jump to any chat.
```

**Typography:** "Tip" label on the title. No step counter.

**Pacing:** 5-8s per action. No "Before you start". No recap; end on the result.

**Highlight:** Zoom straight to the control.

**Music:** None by default; short, with `--music`.

**Transitions:** Cuts.

**Outro:** The result held for 1.5s, then the product name.

