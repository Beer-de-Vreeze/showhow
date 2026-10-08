# Step 1: Inspect the project

Find what the viewer needs to see and do.
The source differs per mode; the secrets rule at the end applies to both.

## Always read

1. **Styles** - `:root` custom properties, theme tokens, font declarations. These become the video's visual identity so the rebuilt UI looks like the real product.
2. **README and product docs** - `README.md`, `docs/`, a features or roadmap file, onboarding or help pages. Note the product's own names for things.
3. **`package.json` / manifests** - product name, current version.
4. **UI copy** - labels, button text, menu names, empty states, toasts. The narration must use these exactly.
5. **`public/` or `assets/`** - logo, icons, images.
6. **Icon and logo components** - the product's own marks for things it shows (provider or model logos, file-type icons, app icons), often inline SVG in shared components rather than files. Reuse them; don't stand in letter badges or generic shapes where the real mark exists.

## Mode: howto

Trace the task end to end through the code, the way a user would do it.

1. **Entry point** - where does the user start? Route, sidebar item, menu, settings page. Find the exact label they click first.
2. **Each action** - follow the component tree: which button, field, dialog, dropdown. Record the exact on-screen text of every control the user touches, in order.
3. **What happens after each action** - loading states, toasts, new rows, changed views. These are the "result" beats that prove a step worked.
4. **Prerequisites** - permissions, roles, settings, feature flags, connected accounts, existing data. Look for guards, disabled states and error messages.
5. **Common mistakes** - validation errors, disabled buttons and their tooltips, limits (file size, count). Pick at most one worth mentioning.
6. **Where the result lives** - how does the user find what they made later?

If a demo, fixture or seed folder exists, use its sample data as the model for on-screen content.

When a step happens outside this product (creating an API token in a vendor's portal before connecting it, an admin consent in another app), the code won't show it: trace it with [general.md](general.md) and tag it `outside` in the plan.
Connectors and integrations almost always have one: look for help text, placeholders or docs links next to the token or URL fields.

### Howto rubric

Answer all of these before Step 2.

```
1. What will the viewer be able to do after watching? (one sentence, starts with a verb)
2. Who is the viewer? (new user / regular user / admin) What do they already know?
3. What must be true before they start? (role, setting, data) - or "nothing"
4. Where do they start? (exact screen and label)
5. The steps: one action each, with the exact label of the control, and the visible result.
6. What does success look like on screen?
7. One mistake or limit worth mentioning - or "none".
8. Where do they find the result later?
9. Which style fits? (`clean` by default; any of the 11 in tones.md, or the user's direction)
```

If the steps list has more than about 8 actions, the task is probably two tasks.
Propose a split (part 1 / part 2) and make part 1 unless the user said otherwise.

## Mode: update

Find the real, user-visible changes in the release.

1. **Pin the range.** A version (`2.4.0`), tag, PR, or "since X". Find the previous release: tags (`git tag --sort=-creatordate`), version-bump commits (`git log --oneline -- Cargo.toml package.json`), or a CHANGELOG. If the range is ambiguous, state the range you picked in the plan.
2. **Read the release notes the team already wrote.** CHANGELOG entries, release commit subjects, PR titles and descriptions, a features/status doc. These are the source of truth for what the team considers the headline.
3. **Read the commits and diff** in the range (`git log --no-merges <from>..<to>`, `git diff --stat <from>..<to>`). Group commits into user-visible changes. Drop refactors, tests, CI, dependency bumps and internal fixes nobody can see.
4. **For each kept change, trace it into the UI** exactly like a howto: where it lives, the label, one or two actions that show it, the visible result.
5. **Rank** by how much it changes a user's day. Keep 2-5.

### Update rubric

```
1. Which release or range is this? (version, from..to)
2. Who is the viewer? (all users / admins / a specific team)
3. The changes, ranked, max 5. For each:
   a. What is new or fixed, in one plain sentence
   b. Where to find it (exact screen and label)
   c. One or two actions that show it, with the visible result
   d. Why it matters to the viewer (their words, not ours)
4. Anything the viewer must do to get it? (update the app, restart, ask an admin) - or "nothing"
5. Which style fits? (`release` by default; any of the 11 in tones.md)
```

## Color and font extraction

Look for custom properties in `:root` or theme files, and font declarations in `body`, `:root`, `<link>` tags or `@import`.
Write down: background, surface/card, primary text, muted text, accent, border, display font, body font.
If the product has several themes, use the product's brand or default theme (the one its `:root` defines, or that its theme picker marks as default), never whatever a test fixture or a dev build happens to load; write down the theme id and its background and accent values.
Captures must set that theme explicitly (for example `data-theme` on `<html>`), so a fixture's default can't slip in.

## What to skip

Don't read:
- Build output (`dist/`, `.next/`, `build/`, `target/`)
- Lock files
- `.git/` internals (use `git log`/`git diff` instead)
- Environment and secret files (`.env`, `.env.*`)
- Credential and key material (`.pem`, `.key`, `id_rsa`, service-account JSON, anything under `secrets/` or `credentials/`)
- Local config that commonly holds tokens
- Any file the project's `.gitignore` excludes for the reasons above

## Rule: nothing secret or personal leaves this step

Instructional and release videos get shared internally and with customers.
Never carry secrets, API keys, tokens, tenant or client IDs, internal hostnames or URLs, real customer, colleague or user names, email addresses, or any personal data into the plan, brief, composition, captions, companion doc or render.
Commit authors are personal data too; don't credit people by name unless the user asks.
If a real screen would contain such data, use plausible fictional stand-ins (e.g. "Acme Legal", "Sam Jansen", `sam@example.com`) and list the substitutions in the plan.
