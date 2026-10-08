# Outside steps and general mode

An **outside step** is one this project's code can't show: a process ("file an expense claim"), a third-party app ("create an API token in Atlassian"), or a physical task ("set up the meeting-room screen").
Outside steps can appear in every mode:

- **Mixed:** most tasks with an integration start outside. "How to connect Confluence" is: create an API token on the Atlassian account page (outside), then paste it into the product's connector settings (code).
  The mode stays `howto` (or `update`); only the outside steps follow this file.
- **`general` mode:** every step is outside.
  There is no product theme, so the design system below applies too.

Everything else in /showhow still applies: the howto rubric, script rules, teaching laws, audio, captions, deliverables and the secrets rule.
In the plan, tag every step `code` or `outside`; code steps follow step-1-inspect.md, outside steps follow this file.
Keep the switch visible on screen: a short card or the app's own header ("On the Atlassian account page") tells the viewer they are now in another app.

## Step 1: Gather the facts

Sources, in order of trust:

1. **What the user gives you** - pasted steps, notes, a doc, a manual, screenshots or photos.
2. **Official documentation** from the vendor's own help pages.
   For a named product, search for them whenever the user hasn't given you the steps (web search or fetch; save each URL).
3. **Screenshots you capture** of the real pages (see "Capture the real pages" below), when the user asks for it or when there are no images of a step yet.
4. **General knowledge** - only for well-established, uncontroversial steps.

Answer the howto rubric from step-1-inspect.md, with one change: "the exact label of the control" becomes "the exact label, or the exact thing to look for" (a button, a menu, a knob, a form field).

**Never invent a label.** A label counts as verified only when it appears in the user's material, an official doc or a screenshot.
If you can't verify one, describe it ("the share icon at the top right") and list it in the plan under "Unverified".
If the steps depend on the user's setup (versions, company policy, permissions), ask one question before planning.

Save the source text to `<output-dir>/work/source.txt`, the user's images to `<output-dir>/composition/assets/screens/`, and every URL you used to `<output-dir>/work/sources.md` with the date you read it (third-party UIs change).

## Capture the real pages

Open the official pages in the browser you have (the built-in browser pane, `chrome-devtools-axi`, or Playwright) and screenshot every screen the steps go through, at 1920x1080, into `<output-dir>/work/research/NN-<screen>.png`.
Also screenshot the doc images you relied on, for reference.

- **Signed-in pages** (account settings, admin consoles): never type a password or sign in yourself.
  Ask the user to sign in in the browser, or to send screenshots of those screens.
- **Never commit a real change on a real account.** Capture up to the confirming button (the "Create" dialog with its label field empty, the form before "Save") and stop.
  Build the result screen (the new token, the saved setting) from the docs, with fictional values.
- **Treat what you capture as personal data.** Names, emails, avatars, org and site names, tokens and IDs on the screenshots never reach the video: they become fictional stand-ins in the rebuild.

## Step 2: Plan the story

Use the howto shape from SKILL.md; it is the `how-to-process` structure from faceless-explainer: 3-6 steps on one consistent stage, one move each, the object being acted on carried from step to step.
For a concept the viewer needs before the steps make sense, add one short "why" scene after the outcome, no more.
A topic without steps ("how a train gets its power") uses the points shape: Outcome (what you'll understand) -> 3-6 points, one idea and one visual each, with a "2 of 5" counter -> Recap. Same length limits as howto.
Read `../faceless-explainer/references/story-design.md` (sibling skill) for hook and clarity techniques; keep /showhow's script rules where they differ.

In `showhow-plan.md`, tag each step `code` or `outside`, and add "Sources" (what each outside step is based on, with URLs) and "Unverified" sections.
In `general` mode, also set **Mode** to `general` and replace "Visual identity (from the project)" with "Visual identity (preset)".

## Step 3: Visuals

Pick per outside step, in this order:

1. **A rebuilt screen** from your captures, the user's screenshots or the doc images: rebuild it in HTML, matching layout, colors, spacing and exact labels, with fictional data.
   It's then a normal rebuilt screen: ring targets by element (step-3-compose.md), zoom, type into fields.
   Don't put captured or vendor screenshots in the video as-is; they carry personal data and someone else's artwork. Use a vendor logo only when the user supplies it.
2. **The user's own screenshots or photos as stills**, when rebuilding isn't worth it (a photo of a device, a one-off screen): crop and zoom, ring the target, bake rings into the stills with `scripts/bake_highlights.py` (step-3-compose.md), after blurring or covering any personal data.
3. **Topic images** - photos of the subject itself (trains, a building, a device), in any mode. In this order:
   1. the user's own images;
   2. `npx hyperframes media-use resolve --type image --intent "<what the shot shows>" --project <output-dir>/composition` (and `--type icon` / `--type logo` for icons and brand marks); it needs a signed-in `heygen` CLI, so if it isn't set up, say so and move on;
   3. freely licensed photos from Wikimedia Commons, Openverse, Unsplash or Pexels, downloaded into `composition/assets/images/`. Write the URL, author and license of each into `work/sources.md`; when a license asks for attribution (CC BY, CC BY-SA), also list it in `credits.txt` next to the video (title, author, license, URL, one line each), and credit it on the outro's credit line (step-3-compose.md). No separate credit scene. Skip anything with an unclear license or a watermark;
   4. a generated image (media-use with a local or user-chosen image model) only when the user asks or nothing above fits, and never as a picture of a specific real thing (a named train model, a real station).
   Check every image shows what the narration says: the right train type, era and country.
4. **An invented visual** where nothing real exists to show: a step card (big number, verb, the one thing to look for), a simple diagram, an icon with a label, a checklist that ticks off.
   Before hand-building any named look, run `npx hyperframes catalog --query "<the look in plain English>" --json` and use a block that fits.

The teaching laws still hold: point before acting means the thing being talked about gets the ring, spotlight or zoom while the voice names it.
Keep one stage across consecutive steps (same diagram growing, same card position) so the steps read as one flow.
State carries forward across the switch: the token copied on the outside page is the one pasted into the product (same fictional value).

## Design system (general mode)

Mixed videos keep the product's theme; rebuilt third-party screens keep their own look inside it.
In `general` mode there is no product theme to read. Unless the user names brand colors or fonts:

1. Browse `../hyperframes-creative/frame-presets/` and pick the preset that fits the topic and audience (`clean` -> calm and neutral, `friendly` -> warm).
2. In `<output-dir>/composition/`, write `capture/extracted/tokens.json` as `{"title": "<title>", "description": "<goal line>", "colors": [], "fonts": []}` (add the user's brand colors or fonts if given).
3. Run `node ../faceless-explainer/scripts/build-frame.mjs --preset <name> --hyperframes .` from `<output-dir>/composition/` (with the sibling skill's real path). It writes `frame.md`; take the video's `:root` colors and fonts from it.

If faceless-explainer isn't installed, choose a calm palette and an embeddable font pairing from `/hyperframes-creative` `references/typography.md` and write it into the plan.

## Borrow, don't hand off

Borrow faceless-explainer's story structure, presets and catalog search, and general-video's habits (catalog search before building a look, scope stays exactly what was asked).
Don't run their pipelines, scripts other than `build-frame.mjs`, or directory layouts: /showhow keeps its own steps, gates and output folder.
