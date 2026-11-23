# Design floor

Adapted from [impeccable](https://github.com/pbakaus/impeccable) (Apache-2.0), with rules from [unslop](https://github.com/heydamir/unslop) by Damir Sokolovsky (@heydamir, CC BY 4.0), [motionmaxxing](https://github.com/Tejashmakwana/motionmaxxing) (Apache-2.0) and [taste-skill](https://github.com/Leonxlnx/taste-skill) (MIT), rewritten for video.

Read this before building any chrome: title and outro cards, step and change cards, counters, tags, caption plates, credit line.
It covers the video's own chrome only.
Rebuilt product screens and third-party screens keep their own look, even where it breaks a rule here: the teaching law "Show the real product" wins.

**Precedence.** A preset picked with `--theme`, or the user's own brand, overrides the Refuse list: `blockframe` keeps its label pills and hard shadows.
A style's own entry in tones.md overrides the motion values and the Refuse list where it names something on purpose: `release` tags pop and its version slams in.
The contrast, type, depth and radii checks apply to every video.

**Energy.** In `clean`, `friendly` and `quick-tip`, ambition shows as precision: one accent, quiet cards, nothing that competes with the steps.
Bold treatments belong to `release`.

## Verify

Check these on snapshot frames of the title, one step and the outro, together in one look.

- **Contrast:** text at least 4.5:1 on its background, large text (title, card heading) at least 3:1, captions on their plate. Secondary text on a coloured surface is tinted from that surface, not grey.
- **Type:** at most two families. Clear scale and weight steps between title, card heading and body. Tracking no tighter than -0.04em (-0.02 to -0.03em usually reads best). Headings balanced, no orphan word on a second line.
- **Depth:** a shadow has an offset and a soft blur, sized for video (a web 6% shadow vanishes). Use either a border or a shadow per card, not both.
- **Radii:** nested corners are concentric: outer radius = inner radius + the padding between them. Card radii 12-16px at 1080p; pills only for small tags.
- **Motion:** one motion signature for the whole video (one entrance, one exit, one easing), not a different effect per card. Entrances ease out (`power3.out`, `expo.out`).
- **Motion values** (measured on professional films by [motionmaxxing](https://github.com/Tejashmakwana/motionmaxxing), Apache-2.0):
  - An entrance does most of its travel in the first 4-8 frames, then a long settle.
    A typical card or label move takes about 0.33s (10 frames at 30fps); camera moves on product screens keep their 0.6-1.0s.
  - No bounce or overshoot on chrome; at most one visible spring in the whole video.
  - Nothing scales up from zero.
    Things arrive by moving a short way (16-40px), by unmasking, or by settling down from slightly oversize (about 1.05-1.1x).
  - Exits ease in and are shorter than entrances (about 0.2s).
  - Words arrive as whole words, 4-6 frames apart in a title, never letter by letter.
    Letter-by-letter typing is only for the product's own input fields.
  - The cursor rests 0.2-0.3s on its target, presses (the kit's `ripple`: a 2-frame squash, a 3-frame spring back), and the target answers a frame later (step-3-compose.md).
- **Copy:** curly quotes, a real ellipsis (…), a non-breaking space between a number and its unit, sentence case unless the style says otherwise.
  No exclamation marks on cards or titles; titles and labels end without a period.
- **Rhythm:** paddings, gaps and offsets on a 4px grid.
  The same kind of card has the same padding and size every time it appears, and space inside a group is smaller than space between groups.
- **Numbers on cards:** one format across the video (`1,240` and `$48,210`, not `1.2k` next to `$124,860.40`), with `font-variant-numeric: tabular-nums` on counters and anything that ticks.
  A change says what it compares to (`12% faster than 3.3`).
  Numbers on rebuilt product screens stay exactly as the product shows them.

## Refuse

These are where generated video design lands when nobody decides.
Seeing one in a frame means rewrite the element, not soften it.

- **An eyebrow or kicker label above the title** ("How to", "New feature" in small accent caps). The title carries itself; put the mode in the title or the narration.
- **Gradient text.** Emphasis comes from weight or size.
- **Tracked all-caps labels** (`NEW FEATURE`, `STEP ONE` with wide letter spacing).
  Sentence case; the step counter keeps normal tracking.
- **Emoji badges and sparkle tags** (`New ✨`, `Beta 🚀`).
  The release tags "New" and "Fixed" are quiet text on a small tag, no emoji.
- **Coloured glows, coloured shadows and neon borders** on cards and titles.
  The one exception is `release`'s subtle audio-reactive glow on cards and the title (tones.md, audio.md).
- **Blurred colour blobs or a full-frame gradient as the background.** It reads as filler and bands under H.264. Use a solid ground, the product's own surface, or a texture from the subject's world.
- **Glass and blur as decoration.** Use them only where they show something (a sheet over the app).
- **Same-size icon-plus-heading cards as the structure** of a title or recap. Use the product's real screen, a list, or one strong statement.
- **Emoji or Unicode glyphs as icons.** Use the product's own icons or one drawn SVG set in one stroke weight.
- **Monospace as a costume** for "technical". Mono is for code, values and keys.
- **Hard offset shadows** (`4px 4px 0`) outside a neobrutalist preset.
- **A coloured border on one side only** (thicker than 1px) on cards, callouts or captions.
- **Sparklines, progress rings and decorative charts** that show no real data.
- **Page chrome nobody asked for** (motionmaxxing's top tell of an undecided video): a brand or film name parked in a corner, timecodes, progress bars, corner brackets, scene labels like "01 - THE WAIT".
  The step or change counter is not chrome: it is a teaching law, so it stays in howto and update.
  In a `release` hook and title, before the first change, leave the counter out too.

## Video facts

- Full-frame linear gradients on dark grounds band under H.264; use a radial gradient, a solid fill, or a solid plus one local glow.
- An accent at 5% opacity disappears in compression: 15-25% for atmosphere, full saturation for the focal element.
- 1px borders and faint shadows from a web page vanish at video scale; scale them up for the chrome, keep them as they are on rebuilt product screens.
- Text that the narration names must be legible at 1080p on a phone: about 28px minimum at 1920x1080 for chrome text.
