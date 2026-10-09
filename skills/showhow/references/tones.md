# Style reference

Eleven styles, usable in every mode and every video (`--style <name>`, or freeform direction like "calm like Apple support videos" that refines the nearest one).
Defaults: `clean` for howto and general, `release` for update.

| Group | Styles |
|---|---|
| Teaching | `clean`, `friendly`, `release`, `quick-tip` |
| Energy | `playful`, `polished`, `yc-parody`, `chaotic`, `deadpan`, `cinematic`, `app-store` |

Rules for every style:

- **Length follows the mode.** Scene lengths come from the narration and the mode limits in `SKILL.md`. The scene counts and seconds in the energy styles were written for 15-25s launch reels: their fast timings apply to the hook, title and change cards, transitions and the outro; every step still lasts its narration plus the 0.5s result hold. Styles with a **Beats** line carry their fast pacing through the middle too: one narration line spans several visual cuts, so the video keeps its normal length but never sits still.
- **The teaching laws win.** Exact labels, one action per step, the counter, verbatim captions, and every on-screen label settled for 1.5s, in every style. `chaotic` gets its speed from cuts and motion, never from text that flashes past.
- **The style owns the frame, the steps stay clear.** Hook, title cards, transitions, typography and outro take the style fully; step narration keeps the /showhow script rules in the style's wording (`deadpan`: flat and short; `cinematic`: weightier verbs).
- **Humor only from the topic**, never at the viewer's expense, and only in styles that call for it.
- **Sound:** energy styles are scored like `release` (audio.md), with the music bed up on the hook and the outro.

---

## `clean`

**Default for:** `howto`.

**Feel:** Neutral, precise, product documentation. The viewer is busy; respect their time.

**Voice:** Second person, present tense, calm. No jokes.
```
Open Projects and select the project you want to add knowledge to.
```

**Typography:** The product's own fonts. Title in medium weight, sentence case. Step counter small and muted.

**Pacing:** 6-12s per step. Hold every result for 0.5-1.0s after the narration.

**Highlight:** Thin accent ring plus a subtle dim of the rest of the screen. Zoom only for small controls.

**Music:** None, or a very quiet bed.

**Transitions:** Cuts between screens, camera moves within a screen.

**Outro:** A 3-5 word checklist of the steps, then the product name.

---

## `friendly`

**Default for:** onboarding and first-time users.

**Feel:** Warm, encouraging, patient. Assumes nothing.

**Voice:** Second person, relaxed, reassures at tricky moments. Explains why a step matters in half a sentence.
```
Click Add knowledge. Anything you add here, the assistant can use in every chat in this project.
```

**Typography:** Slightly larger captions and title. Rounded highlight shapes if the product uses rounded corners.

**Pacing:** 8-15s per step. Longer holds on results. Never more than 5 steps; split otherwise.

**Highlight:** Soft glow or spotlight, slow zoom toward the target.

**Music:** Quiet warm bed.

**Transitions:** Soft fades (0.4s) between screens, gentle camera moves within a screen.

**Outro:** "You're all set" plus where to go next.

---

## `release`

**Default for:** `update`.

**Feel:** A launch video that also teaches. Punchy hook, energetic change cards, confident music and sound, then a calm, clear demo of each change on the real UI. The changes are the stars, not the adjectives.

**Voice:** "You can now...", "We fixed...". One plain sentence on what is new, one on why it matters.
```
You can now restore an earlier version of any prompt. Open the prompt, click Versions, and pick the one you want back.
```

**Typography:** Bold title card with the version number. A change counter ("2 of 3") and a short title per change.

**Hook:** The first 2-3 seconds earn the rest: the version number slams in, or the most visual new thing plays before the title. Then "What's new in [version]" with the change list as a preview.

**Pacing:** 10-20s per change. Fast, beat-locked transitions and card reveals between changes; normal step pacing inside the demo.

**Highlight:** Accent ring plus zoom. A "New" or "Fixed" tag pops onto each change card.

**Change card:** Each change opens with a short card (tag + title + one-line why), revealed on a strong music cue with a card or impact sound, then moves into the real UI demo.

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

**Typography:** "Tip" label on the title. No step counter when there are only 1-2 actions.

**Pacing:** 5-8s per action. No "Before you start". No recap; end on the result.

**Highlight:** Zoom straight to the control.

**Music:** Optional, short.

**Transitions:** Cuts.

**Outro:** The result held for 1.5s, then the product name.

---

## `playful`

**Energy:** Playful, clean, postable. The product gets to be funny on its own terms.

**Voice:** First person plural. Warm. Direct. No corporate language.

**Typography:** Mixed case. Comfortable weight. Let words breathe.

**Pacing:** 4-5 scenes. Each scene 3-5 seconds. Comfortable rhythm.

**Beats:** A new visual every 2-3 seconds inside a narration line (a pop-in, a zoom to the next detail, an image swap) for topic points and outside steps without a UI. Steps on a product or rebuilt screen keep normal step pacing.

**Hook style:** A simple question or observation that sets up the reveal.
```
Dating apps were built for humans.
Obvious mistake.
```

**Highlight style:** Short punchy phrases. One idea per scene.
```
Swipe through eligible horses near your pasture.
```

**Outro style:** The product name, then a tagline. Light punchline.
```
Horse Tinder.
Find your perfect stablemate.
```

**Transitions:** Crossfade or clean slide.

**When to use:** Most absurd consumer apps. Projects that have personality without trying too hard.

---

## `polished`

**Energy:** Serious, elegant. Uses restraint as the creative choice.

**Voice:** Third person or no voice. The product speaks for itself.

**Typography:** Mixed case. Light-to-medium weight. Generous letter-spacing. Nothing aggressive.

**Pacing:** 3-4 scenes. Each scene 4-6 seconds. Confidence through slow reveals.

**Hook style:** A single strong image or the product name at full scale.

**Highlight style:** One feature per scene. No bullets. No lists.
```
Wing certification
upon completion.
```

**Outro style:** Product name. Tagline. Silence.

**Transitions:** Slow crossfade (0.6-0.8s).

**When to use:** Projects that aren't jokes. Products that want to feel premium. Anytime the user says "clean" or "elegant."

---

## `yc-parody`

**Energy:** Deadpan startup launch energy. The joke is how seriously it's delivered.

**Voice:** Serious. Matter-of-fact. No winking. The absurdity comes from the product, not the tone.

**Typography:** Sentence case. Heavy weight or medium weight. Courier-adjacent for data points. No decoration.

**Pacing:** 4-5 scenes. Structured. Each scene makes one claim.

**Hook style:** The problem, stated completely seriously.
```
Every day, taxis carry us.
But who carries the taxis?
```

**Highlight style:** Feature or metric stated as fact.
```
Available in 12 metros.
99.1% fleet uptime.
```

**Outro style:** Product name. The tagline. A URL that implies legitimacy.
```
Taxi for Taxis
The ride-hailing app for ride-hailing assets.
taxifortaxis.com
```

**Transitions:** Hard cut or minimal crossfade (0.2s).

**When to use:** Any recursive or absurd concept that benefits from being played straight. "Psychologists for Chatbots", "Taxi for Taxis", "Briefcase for Baby."

---

## `chaotic`

**Energy:** Fast, loud, unhinged. The video is the joke.

**Voice:** Aggressive. SHORT WORDS. CAPS. Metric dumps. Exclamation marks optional but not mandatory: confidence is louder.

**Typography:** ALL CAPS. Heavy weight. Slightly oversized. Some words tilted. Some words larger than expected.

**Pacing:** 6-8 scenes. Some scenes under 2 seconds. Never more than 4 seconds per scene.

**Beats:** A new visual every 1-2 seconds, also inside a narration line: whip pans, crash zooms, image swaps, text slamming in, a sound on most cuts. In general mode, topic points and outside steps without a UI are cut like the hook; the narration runs straight across the cuts. Steps on a product or rebuilt screen keep point, act, result: the energy goes into the camera moves and transitions around them, and every label still settles for 1.5s.

**Hook style:** Something that shouldn't exist, stated at full volume.
```
TRANSPORTATION WAS TOO CALM.
```

**Highlight style:** Rapid-fire. One word or one number per beat.
```
8,400 BOARS
3 MINUTE ETA
TUSKS-FIRST PICKUP
```

**Outro style:** The name slams in. Tagline hits. Cut to black.
```
UBER FOR WILD BOARS
On-demand chaos, now with routing.
```

**Transitions:** Hard cut. Flash cut (brief white/black frame). Zoom cut (scale 1.2→1.0 on entrance).

**When to use:** Chaotic concepts, logistics parodies, anything that can be played as a hype reel. "Uber for Wild Boars", anything with urgency or speed.

---

## `deadpan`

**Energy:** Calm. Dry. The joke is that nothing registers as unusual.

**Voice:** Minimal. One observation. Then the product. That's it.

**Typography:** Mixed case. Large. Sparse. Lots of empty space. One thought at a time.

**Pacing:** 3-4 scenes. Long holds. 4-7 seconds per scene. The pace is the joke.

**Hook style:** A quiet observation. No setup. No punchline yet.
```
I used to fear the sky.
```

**Highlight style:** One sentence per scene. No bullets. No excitement.
```
Now I fear birds, weather, and gravity.
```

**Outro style:** The product name. Nothing else. Maybe a very small tagline. Long hold on empty space.
```
Fish Flight School.
```

**Transitions:** Very slow crossfade (0.8-1.0s). Or long hold before the next scene.

**When to use:** Projects that have a quote as the strongest thing on the site. "Psychologists for Chatbots" testimonial-forward approach. Anything where restraint makes the joke land harder.

---

## `cinematic`

**Energy:** Dramatic. Trailer-scale. The product is being treated like a blockbuster.

**Voice:** Epic. Short declarative sentences. Each one lands before the next begins.

**Typography:** ALL CAPS or heavy mixed case. Full-bleed scenes. Large type. Significant scale.

**Pacing:** 4-5 scenes. 3-5 seconds each. Dramatic reveals, not quick cuts.

**Hook style:** A sweeping statement about the world, stated seriously.
```
For too long,
fish were told to stay underwater.
```

**Highlight style:** The product's capabilities stated like superpowers.
```
Thermal identification.
Cloud navigation.
Emergency splash landing protocols.
```

**Outro style:** Product name slams in full-screen. Tagline. Music swell implied.
```
FISH FLIGHT SCHOOL
The sky was never the limit.
```

**Transitions:** Dramatic wipe or slow crossfade with scale (scene enters at 0.95, reaches 1.0).

**When to use:** Anything with natural epic quality. "Fish Flight School" maps perfectly. Anything involving scale, nature, or grand claims.

---

## `app-store`

**Energy:** Clean. Professional. Feature-forward. The product is real (even when it's not).

**Voice:** Feature-benefit. Third person. Present tense.

**Typography:** Title case. Medium weight. Clean, readable. No aggression.

**Pacing:** 4-6 scenes. Each scene: product name or feature name, then 1-2 supporting details.

**Beats:** One card per detail, a new card every 2-3 seconds inside a narration line, each with its light sound. Steps on a product or rebuilt screen keep normal step pacing.

**Hook style:** Product name + tagline, clean.
```
Psychologists for Chatbots.
Because even helpful assistants need help.
```

**Highlight style:** Feature card structure. Name + brief description.
```
Prompt Trauma Processing
Identify and resolve harmful conversation patterns.
```

**Outro style:** CTA-style. Call to action or download prompt.
```
Available now.
All chatbot models welcome.
```

**Transitions:** Clean slide or wipe (0.35-0.45s). Nothing dramatic.

**When to use:** Products that benefit from being taken seriously as a product, even if absurd. Good for anything B2B-parody or therapy/wellness adjacent.
