# House style and feedback loop

The user's own taste, kept across runs so the next video does not repeat the last video's mistakes.
Pattern adapted from [motionmaxxing](https://github.com/Tejashmakwana/motionmaxxing) (Apache-2.0), which keeps `taste/verdicts.md` and `taste/edits.md` for the same job.

## The two files

Both live in `~/.showhow/` (Windows: `%USERPROFILE%\.showhow\`), outside the skill, so updates to the skill never overwrite them.

- **`verdicts.md`** - standing preferences, one line each, grouped under `## Defaults`, `## Always` and `## Never`.
  `## Defaults` holds option defaults written as flags (`--style friendly`, `--voice am_michael`, `--music`).
  The other two hold rules in plain words, each ending with the run it came from: `- Captions at least 40px at 1080p (connect-confluence, 2026-11-23)`.
- **`edits.md`** - before/after lessons, newest first, one block each:

```markdown
## 2026-11-23 connect-confluence
- Before: step cards slid in from the left with a bounce.
- After: cards rise 24px and settle with expo.out, no bounce.
- Why: "the bounce looks cheap" (the user's words).
```

If a file does not exist, carry on with the skill's defaults; create it the first time there is something to write.

## Read at the start of every run

Right after parsing the invocation, read both files if they exist.
- Flags typed in this invocation win over `## Defaults`; `## Defaults` wins over the skill's defaults.
- `## Always` and `## Never` are extra laws for this run; the teaching laws, accessibility rules and "Show the real product" still win over them. If a rule conflicts with one of those, follow the law and tell the user which rule you skipped and why.
- Copy the rules that apply into the plan under "House style", and the banned ones into the composition brief's BANNED line, so they reach the build.
- Skim `edits.md` for lessons that touch this video's style and mode.

## Learn after every round of feedback

When the user asks for changes after seeing the preview or the render, sort each request before fixing it:

| Kind | Example | Where it goes |
|---|---|---|
| **One-off** | "Step 3 should say Save, not Submit" | Fix it in this video only |
| **Lasting** | "The captions are too small", "don't use that whoosh", "slower zooms" | Fix it, then write it to `verdicts.md` (a rule) and `edits.md` (the before/after) |

Asked in the user's words as a general preference ("always", "never", "I hate when"), or the same correction a second time, is lasting.
When unsure, ask in one line: "Keep that for every video, or just this one?"

After the fixes, show the lines you added or changed in both files as a diff, so the user can strike one.
Never write a rule the user did not express, and never record their preferences anywhere else.

## `/showhow learn <output-dir>`

Learns from a past run without making a video.
Read `<output-dir>/showhow-plan.md` (and `composition-brief.md` if it exists) for what the video did, and ask the user what they changed or disliked in that video.
Sort their answers with the table above, write the lasting ones, show the diff, and stop.
