# Brand kits

A brand kit is a company's look as a local folder, so a run can use it without it living in this repo.
Kits live in `~/.showhow/brands/<name>/` (Windows: `%USERPROFILE%\.showhow\brands\<name>\`).
Kits are never committed to the showhow repo; keep them out of any checkout.

## What a kit holds

Nothing but these.

- `FRAME.md`: the same shape as `assets/frame-presets/showhow/FRAME.md` (frontmatter with `colors`, `typography`, then the prose sections).
  The `colors` block must have `paper`, `ink`, `accent` and `muted`, and `typography` a `fontFamily` for `title` and `label`.
  The frontmatter adds `logo: <file>` and a `fonts:` list of the font files it uses, named `fonts/<Family without spaces>-<weight>.woff2` (`- fonts/BrandSans-400.woff2`) so `stage.py` can declare them, and may add `voice: <Kokoro id>`, `music: <file in the kit>` and `outro: "<line>"` (for example `"ASAPCLOUD - asapcloud.nl"`).
- The font files, in `fonts/`, with their licences.
- The logo, SVG or PNG.

A fixture kit to copy the shape from: `scripts/fixtures/brand-kit/`.

## Using a kit

Order of precedence is the "Theme lookup order" in `SKILL.md`; it is not repeated here.
Pick a kit with `--brand <name>`, or `brand: <name>` under `## Defaults` in `~/.showhow/verdicts.md`.

1. Stage the composition with it: `stage.py composition --brand <name>` (`step-3-compose.md`).
   It runs the check below first; a failing kit stops the run: tell the user which lines failed and do not fall back to another theme.
   It writes the kit's colours and fonts as the one token set the kit, scene3d and `bake_highlights.py` read, so no hex goes into scene code.
2. Use the logo on the title and outro cards, `outro` as the outro line, `voice` as the voice and `music` as the music bed unless the user typed their own flags.

A kit works in every mode, and it styles the video's own chrome: title, cards, counters, caption plate, outro, 2D visuals and scene3d.
In howto and update, rebuilt product and third-party screens keep their own look (`design-floor.md`); never repaint a product's UI in the kit's colours.

## Checking a kit

`uv run --project <skill-dir>/scripts python <skill-dir>/scripts/brand_kit.py check <kit-dir>`

It prints `PASS`, or one `FAIL` line per problem and exits 1: `FRAME.md` missing, a required colour missing or not a CSS colour, a font file or the logo or the music file missing.
The colour check is deliberately small: hex, `rgb()`/`hsl()` and a short list of colour names.
If a real brand value is rejected, write it as hex.

## Creating a kit

`/showhow brand <name> <repo path or URL>`.
Make no video.

**From a repo.**
Follow `references/step-1-inspect.md`, "Always read" (styles, and icon and logo components), and its "What to skip" rule: the `:root` colours and fonts of the default theme, logos from shared components.
Do not copy those rules here.

**From a website.**
Open the page in the browser and read the computed CSS (custom properties on `:root`, the heading and body font families) and the logo (inline SVG or the header image).
Never sign in, never enter credentials, never follow a login wall.
Fonts: use a font only if its licence is open (OFL, Apache); otherwise name the nearest OFL font and flag it.

**Then, for both.**
1. Write the kit to `~/.showhow/brands/<name>/`, with the fonts copied in and the logo saved.
2. Flag every value you could not verify in `FRAME.md`, in a `## Unverified` section: one line each, saying what it is and why (a guessed accent, a substituted font, a logo traced from a screenshot).
3. Run the check.
4. Render one sample still with the kit (the title card, using the logo, the accent and both fonts), keep it in a temp folder, not in the kit (a kit holds nothing else), and show it to the user.
5. Ask the user to confirm the still; change what they point at and re-snapshot.

## The end-of-run offer

After a howto or update run on a repo with no kit in play, offer once to save the theme the run already read (`work/inspect.md` has its id, background and accent) as a kit.
If they say yes, create it from that repo as above, without re-reading anything the run already has.
