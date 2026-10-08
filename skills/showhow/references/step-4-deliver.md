# Step 4: Validate, render, and deliver

## Validate

```bash
cd <output-dir>/composition
npx hyperframes check   # the single pre-render gate - fix every error it reports
```

Fix all errors, including WCAG contrast failures (they gate as errors).
Each contrast finding carries a suggested compliant color; apply it or adjust within the palette and re-run `check`.
The only bypass is `check --no-contrast`, which skips the whole WCAG pass; don't use it for real text.
For thresholds, follow the current hyperframes-cli `check` guidance.
Contrast warnings on a caption at the exact moment it fades in are expected; errors are not.

### Intentional overlaps (dialogs, sheets, menus, callouts)

`check` reports `content_overlap` when a dialog or sheet sits over text, even though that's the point.
The `data-layout-allow-overlap` and `data-layout-allow-occlusion` attributes on an overlay or wrapper did **not** clear `content_overlap` (hyperframes 0.8.82).
`data-layout-allow-overlap` does work on the exact text element `check` names, e.g. the `<span>` under an open menu.
What works, in this order:

1. **Don't cover the control that opened it.** Place the dialog below or beside the button the viewer just clicked; it also keeps the click target readable.
2. **Hide what's under an opaque overlay.** While a sheet is fully open, set the covered cells to `opacity: 0` just after it slides in and back to 1 just before it leaves; the viewer can't see them anyway.
   Set opacity on the parent (`.badge`, `.switch`) so the children's own states survive.
3. **`data-layout-ignore`** on small floating annotations (callouts, "not this one" marks) that deliberately overlap the dimmed page.

Other escape hatches that exist: `data-layout-allow-overflow` (intentional ellipsis or clipping), `data-layout-allow-caption-zone`, `data-layout-bleed`.
Don't search the npx cache for them; it takes minutes.

Then capture key frames and look at them:

```bash
npx hyperframes snapshot   # PNG key frames
```

Snapshot every ring moment and every result, in one call, into `work/snap/`:

```bash
npx hyperframes snapshot --no-end --describe false -o ../work/snap --at 4.5,16.5,21.5,24
```

Read the contact sheets it writes, then check every frame:
- **The ring sits on the control the narration names**, fully around it, not offset or half off. Crop and zoom any ring you can't judge at contact-sheet size (`ffmpeg -i frame.png -vf crop=w:h:x:y,scale=iw*2:-1 tile.png`).
- The cursor tip is on the target at each click.
- Its label is legible at this zoom.
- Captions, the cursor and any dragged item don't cover it (a dragged file must not sit on the "Drop files to attach" label the voice reads).
- The step counter is visible and correct; no dialog or sheet covers it.
- **No clipped text** in fixed-width pills, callouts, badges or inputs: `check` does not catch text clipped inside a box with `overflow: hidden` or a fixed width. Let labels size to their text (`padding` instead of `width`) where you can.
- **Nothing shows ahead of its content**: `::before` bullets, list dots, icons or borders of a line whose words are still hidden. Hide the whole line, not only its words.
- **A typing caret follows the typed text.** Per-character spans hidden with `opacity` still take up width, so move the caret to the last shown character instead of leaving it inline after the full text.
- **What a step creates stays visible later**: an attached file appears in the sent message, a chosen model in the reply header, a picked workspace in the header.

Fix, re-run `check`, and re-snapshot only the frames you changed.

## Preview

```bash
npx hyperframes preview
```

Tell the user the preview is running and give them the localhost URL.
Ask them to watch it once for accuracy: wrong labels or wrong order are the most expensive mistakes to ship in a how-to.

If the user approves or asks to render:

## Render

Render without `--quiet` and keep the log: with `--quiet` a failed render can exit non-zero (seen: exit 4) with no error message and no file.

```bash
npx hyperframes render --output ../<video-name>.mp4 > ../work/render.log 2>&1; echo "exit $?"
ls -la ../<video-name>.mp4 && tail -5 ../work/render.log
```

The render is done only when the mp4 exists and the log ends with "Render complete".
When `docker info` succeeds, prefer `--docker` for the final render: the same pinned Chrome and ffmpeg every time, so a re-render matches the one that was checked.
The first Docker render builds the image (a few minutes); if it fails, render locally and say so.
If not: read `work/render.log` for the cause, check free disk space (`df -h .`; a render needs a few GB of scratch), and retry once.
If it fails twice, report the log lines to the user instead of retrying further.

Add `--quality draft` for faster iteration, `--quality high` for final delivery.

**Layout changes need screenshot capture.** Fast `drawelement` capture (the render log's summary says which capture ran) drops tweens of layout properties such as `height` and `width`: a row that grows to show an attached file stays closed, a slider fill stays put.
Snapshots use screenshot capture, so they look right while the mp4 is wrong.
When the composition tweens `height`, `width`, `top`/`left` or padding, render with `--experimental-fast-capture=false`.

**Check the mp4, not only the snapshots.** Pull frames from the rendered file at every ring and result moment into one sheet and look at it:

```bash
uv run --project <skill-dir>/scripts <skill-dir>/scripts/frame_sheet.py ../<video-name>.mp4 --overlays ../work/rings.overlays.json --at 5.5,88 -o ../work/check.jpg
```

Add `--crop x,y,w,h` (video pixels) to zoom every frame on one region when a ring is small.
A ring that shows in snapshots but not in the mp4 is a renderer problem: bake it into the still (step-3-compose.md, "Screenshot videos") rather than trying render flags.
`HF_STATIC_DEDUP=0` disables static-frame dedup if you suspect frozen frames.

## Pick the poster frame

The poster is the still shown before the video plays.
For instructional videos the best poster is the **title card** (how-to: the goal line; update: "What's new in [version]"), or the finished result with the title over it.
Pick a settled moment: text fully in, not mid-transition, and no caption on screen (half a sentence under the title looks broken as a thumbnail).
From `<output-dir>/composition`:

```bash
# use the timestamp of the settled title or result frame, e.g. 2.4s
ffmpeg -ss 2.4 -i ../<video-name>.mp4 -frames:v 1 -q:v 2 ../<video-name>.jpg
```

If the frame lands on a transition, nudge the timestamp a few tenths of a second and re-extract.

When the voice talks over the title, no frame of the mp4 is caption-free.
Snapshot a copy of the composition with the captions hidden instead (from `<output-dir>`):

```bash
cp -r composition work/poster
# add `.cap { display: none !important; }` (your caption selector) to work/poster/index.html's <style>
npx hyperframes snapshot work/poster --at 5.5 --no-end -o work/poster-snap --describe false
ffmpeg -y -i work/poster-snap/frame-00-at-5.5s.png -q:v 2 <video-name>.jpg
```

### Bake the poster as frame 0

Most players and platforms (Teams, SharePoint, Slack, YouTube previews) grab frame 0 as the idle thumbnail.
Replace only the first frame's pixels with the poster; duration, frame count and audio stay the same.
From `<output-dir>`:

```bash
ffmpeg -y -i <video-name>.mp4 -i <video-name>.jpg \
  -filter_complex "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]" \
  -map "[v]" -map "0:a?" -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p \
  -c:a copy -movflags +faststart work/poster.mp4 \
  && mv -f work/poster.mp4 <video-name>.mp4
```

Keep `<video-name>.jpg` alongside as the upload thumbnail.

## Write captions.srt

Write the caption phrases and timings from Step 3 to `<output-dir>/captions.srt`, even though captions are burned in: players that support subtitles (Stream, SharePoint, YouTube) use it for search and accessibility.
Times are absolute in the final video (scene start + phrase offset).

```
1
00:00:00,300 --> 00:00:02,100
After this video you can add knowledge

2
00:00:02,100 --> 00:00:03,900
to any project in AI Workbench.
```

With `--no-captions`, still write `captions.srt` (it only skips the burned-in version).

## Write chapters.txt

One line per scene group, starting at `00:00`, in the YouTube chapter format (also works as a table of contents in a description):

```
00:00 What you'll learn
00:06 Step 1 - Open the project
00:18 Step 2 - Add a file
00:34 Step 3 - Check the knowledge list
00:47 Recap
```

Use the measured scene start times from the render.

## Write showhow.md

The written companion: the same content as the video, for people who prefer to read or need to copy a value.
Paste-ready for a help page, release note, Teams post or wiki.

### howto

```markdown
# How to [task]

[One sentence: what you'll be able to do.]

**Before you start:** [prerequisites, or omit]

1. Open **[Label]**.
2. Click **[Label]**.
3. [...]

**Result:** [what you see when it worked, and where to find it later.]

**Tip:** [the one mistake or limit, if any]
```

### update

```markdown
# What's new in [product] [version]

## [Change 1 title]
[What it is, one or two sentences.]
Where: **[Screen]** > **[Label]**.

## [Change 2 title]
[...]

**How to get it:** [update / restart / nothing to do]
```

Use the product's own labels in bold, the same as the narration.
No marketing language, no "excited to announce".

## Write share-copy.md

The message that goes out with the video: what a colleague or customer reads in Teams, email or on the intranet before deciding to watch.
Write it for business readers: what it helps them do in their own work, not how it's built.

**Voice.** If `~/VOICE.md` exists, read it and write as its owner, following its business sections (Teams, customer, announcements) and its language rules.
Otherwise: direct, plain, the point first, no corporate warmth.
Either way: plain hyphens, no em dashes, no "excited to announce", "seamless", "game-changer" or invented claims; only say what the video shows.
Write in the audience's language (ask if unclear); labels stay as they appear on screen.

Two versions, in this order:

```markdown
## Post

[What it is, in one line: the task this video teaches, or the release it covers.]
[What it helps the reader do, with a familiar task or example.]

[howto: prerequisites or the one limit worth knowing. update: 2-4 changes, one line each, each with its work benefit.]

[One concrete action: watch the video, try it on a real task, reply here when you get stuck.]

## One-liner

[One sentence for a caption, a chat or an email subject.]
```

Keep the post to 3-8 short lines.
Emojis only in a channel or client announcement: at most one by the opening line and one per list item; none in colleague chat or email.
Leave out dates, links and names you don't have; write `[link]` for the user to fill in.

## Final output structure

After this step, `<output-dir>/` should contain:

```
~/Downloads/<skill-name>-<video-name>/
  showhow-plan.md
  composition-brief.md
  composition/
  work/
  <video-name>.mp4
  <video-name>.jpg
  captions.srt
  chapters.txt
  showhow.md
  share-copy.md
  credits.txt          (only when a bundled music track is used or an image license asks for attribution)
```

## Tell the user

- Where the video and files are, and the share post itself, ready to paste.
- The goal line and the step (or change) list, so they can spot a wrong step without watching.
- Any fictional data substitutions, any label you could not verify, and the sources used for outside steps.
- Offer to re-record one scene, change the voice, or make the `vertical` or `quick-tip` cut.
