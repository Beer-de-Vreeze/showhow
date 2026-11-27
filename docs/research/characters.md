# Characters in showhow videos

Research date: 2026-11-27.
Marks: [P] = primary source (paper, official license page, legislation, tool docs).
[S] = secondary (blog, vendor summary, law-firm note, search-engine summary); verify before relying on it.
[G] = general knowledge, not checked against a source in this pass.

## Summary

- Characters help most when the learner must practise or recognise interpersonal behaviour (feedback, incident reporting, difficult conversations). Behaviour modelling with mixed good and bad models has the strongest evidence [P1].
- A talking head or mascot that only decorates does not help. Voice and purposeful gesture matter; a static speaker image does not [P3, S4].
- v1 recommendation: 2D SVG characters built from Open Peeps (CC0) parts, a small rig in GSAP, mouth swaps from Rhubarb JSON, one Kokoro voice per character, speaker-coloured captions.
- 3D (Quaternius CC0 or Mixamo animations on glTF) is feasible and deterministic via `AnimationMixer.setTime`, but costs more effort and has more asset-licence traps. Realistic AI avatars (HeyGen, Synthesia) cost money, need consent handling and, in the EU, disclosure under Art. 50.
- Do not use Ready Player Me (closed 2026-01-31) or any real person's likeness. For harassment content keep characters stylised, varied and never graphic.

## 1. When characters help learning, and when they hurt

### Behaviour modelling (the strongest case for scenario videos)

- Taylor, Russ-Eft and Chan (2005) meta-analysed 117 studies of behaviour modelling training (BMT) [P1].
- Effects were largest for learning, smaller for job behaviour, smaller again for results. Interpersonal knowledge and skill effects were a little over 1 SD in controlled studies [P1].
- Declarative knowledge decayed over time; skills and job behaviour stayed stable or grew [P1].
- Transfer to the job was greatest when: models were mixed (positive and negative), trainees practised with their own scenarios, trainees set goals, supervisors were trained too, and rewards or sanctions backed the behaviour at work [P1].
- Skill gain was greatest with learning points shown as rule codes and with longer training time [P1].
- Implication for showhow: a video can show the model and the rule codes ("Name the behaviour, state the impact, ask for their view"). It cannot supply practice, goal setting or supervisor follow-up. Say so in the written companion and end with a "try it with your own situation" prompt.
- Abstract-level access only; the full text is paywalled (APA). Effect-size detail beyond the abstract is [S].

### Pedagogical agents, image and embodiment

- Schroeder, Adesope and Gilbert (2013) meta-analysed 43 studies (3,088 participants): agents give a small but significant learning effect, moderated by context [P2].
- Moderators reported: larger benefit for K-12 than post-secondary learners; agents using on-screen text beat agents using narration; no significant moderating effect of agent appearance [S: secondary summary of the paper; check the full text]. A later paper cites d = 0.66; the original abstract says "small but significant", so do not quote 0.66 [S].
- Mayer's image principle: showing the speaker's image does not reliably improve deep learning. 2014 handbook chapter reviewed 14 tests, half negative or negligible, median d = 0.20 [S via search summary of P3].
- Mayer's embodiment principle: on-screen agents that gesture, move, make eye contact and show expression help. 11 of 11 comparisons favoured high embodiment, median d = 0.36 (2014); a newer summary gives 16 of 17, median 0.58 [S via P3].
- Boundary: embodiment benefit is weaker with negative social cues such as a robotic voice [S]. Kokoro is a neural voice, but flat delivery of emotional lines will read as a negative cue.
- Practical rule for showhow: a character earns its screen time only if it does something the narration cannot: shows a behaviour, a reaction, a spatial relationship, or points at the relevant element. A character who stands in the corner reading the script is the image-principle failure case.
- Related principles worth keeping in the script rules [G]: coherence (cut decorative detail), signalling, segmenting, and worked examples (show the full solved case first, then fade the support). Verify against Mayer 2021 before citing numbers.

### Positive vs negative examples

- Mixed models beat positive-only for transfer [P1].
- Show the negative example briefly, then the corrected version, then the rule. Do not leave the viewer with the bad version as the last image [G].
- Dobbin and Kalev found negative framing (legal threat, settlement stories) in mandatory diversity training tends to provoke resistance, and mandatory control-style programmes backfired on manager diversity [P6]. Frame scenarios around what to do, not what happens to you.

### Uncanny valley and realistic avatars

- Mathur and Reichling (2016) found an uncanny-valley pattern for real robot faces in likability and a trust game [P7].
- Evidence for virtual faces is weaker: Katsyri et al. (2019) found only a weak effect [S via search]. Eeriness rises when expression, voice and mouth movement are less human-like than the face [S].
- I found no study of learning outcomes with realistic virtual instructors. Treat "realistic avatar hurts learning" as unproven, but "mismatched lip sync on a realistic face looks wrong" as likely.
- Stylised 2D characters sidestep the problem: no one expects human-level facial motion from a flat illustration.

### Representation and stereotypes

- Kaiser et al. (2022, Current Directions in Psychological Science) report that a narrow female-victim prototype shapes what people recognise as harassment; targets who do not fit it are less likely to be believed [S via search summary; paper at P8].
- Tinkler (via search summary) warns that trainings can reinforce stereotypes: men as powerful and predatory, women as vulnerable [S].
- Guidance that follows: vary who the harasser, target, bystander and manager are across scenarios; avoid mapping a trait (race, gender, accent, disability) to the wrong-doer; let the behaviour, not the person's identity, be the problem.

### Sensitive topics (harassment, incidents)

- EEOC Select Task Force co-chairs' report (2016): training should be tailored, part of a wider culture with leadership buy-in, and include civility and bystander intervention. The report is by the co-chairs, not a consensus of all members [P5].
- Law-firm summary says training should be frequent, live and interactive [S]. A showhow video is a supplement, not the training. Say that in the companion text.
- Avoid depicting assault or explicit conduct. Use the "moment before" or "the aftermath conversation". Stylised animation removes the discomfort of watching real people while keeping the point [S, vendor claim].
- Balance impact and paralysis: scenes should end on an available action, with who to contact [S].
- Include a short content note at the start for anything about harassment or violence, and a route to support [G].

## 2. How HR and scenario training videos are made today

| Style | Vendors | Typical look | Strength | Typical failure |
|---|---|---|---|---|
| Animated characters in scenes | Vyond, Powtoon, Animaker | Stock office people, prop library, SCORM export (Vyond premium) [S] | Cheap to localise and edit; safe for sensitive topics | Generic stock faces, exaggerated villains, box-ticking tone |
| Talking-head AI avatar | Synthesia, HeyGen | Realistic presenter reading script | Fast; many languages | Stiff delivery, uncanny lip sync, no scene-level behaviour modelling |
| Interactive branching | Easygenerator and similar authoring tools | Slides plus choice points | Practice and feedback, closest to BMT | Authoring effort; needs an LMS |
| Live-action | Specialist studios | Actors | Credible emotion | Cost; actor likeness rights; ages fast |

- Vendor positioning: Vyond for polished, brand-consistent compliance at scale; Powtoon for quick template explainers (slide-based, less fluid character animation); Animaker for more styles at lower price, with a character builder [S].
- Powtoon's own advice: be sensitive to gender, age, appearance and ethnicity of characters; use realistic settings; show gray areas where people are unsure what counts; keep clips bite-sized [S].
- Why it feels cringe (my synthesis, [G], no source found): obvious bad guy and obvious good guy, scripted "that is not okay!" dialogue, identical stock faces, and a narrator who explains what the scene already showed. Counter with ambiguity, realistic dialogue, a reaction shot, and one clear rule at the end.
- I found no neutral research on which vendor style performs better. Everything above on vendors is from vendor or affiliate sites.

## 3. Building characters in code

### 3.1 2D SVG characters

Rig shape (works in GSAP, pure function of time):

- One `<g>` per character, children as groups: `torso`, `head`, `armL`/`armR` (upper arm and forearm nested, pivot at shoulder and elbow via `transform-origin`), `legs`, `face` (eyes, brows, `mouth`).
- Poses are named sets of rotations and swaps; expressions are swaps of an eyes/brows/mouth group (`display` or `opacity` toggled by timeline `set`).
- Gestures are small timeline segments (arm raise, nod, head tilt, breath scale 1.00 to 1.02). Walk cycle: two-leg rotation plus torso bob, looped by modulo of time, not by repeating tweens.
- Determinism: build one paused `gsap.timeline()` per character and register it into the composition's master timeline. No `Math.random`, no real-time loops.
- Open Peeps is built as separable parts (bodies, heads, faces, poses incl. standing and sitting) so it suits this rig; sitting and standing poses are swaps rather than limb tweens, which is simpler and looks fine in a calm style [P9].

Licences (all checked 2026-11-27):

| Library | Licence | Video and commercial use | Notes |
|---|---|---|---|
| Open Peeps (Pablo Stanley) | CC0 | Yes, no attribution [P9] | Full-body, poses, faces, hair; hand-drawn look |
| Humaaans (Pablo Stanley) | CC0 | Yes [P10] | Flat mix-and-match people; more generic |
| Blush (platform) | Blush licence: use, modify, commercial and client work, no attribution; no resale, no merchandising [P11] | Yes | Free-tier export limits (PNG vs SVG) differ by source [S]; check plan |
| DiceBear styles | Per style: 44 CC0 (incl. Open Peeps, Lorelei, Notionists), 14 CC BY 4.0 (Adventurer, Micah, Personas and others), Avataaars and Bottts under artist terms "free for personal and commercial use"; library code MIT [P12] | CC0 and artist-terms styles fine; CC BY styles need credit | Head-and-shoulders avatars only, no body, so weak for scenes |
| Avataaars | Artist terms, free for personal and commercial use (per DiceBear page) [P12] | Yes | Not a standard licence; keep a copy of the wording |
| Lottie files (LottieFiles) | Lottie Simple License: commercial use and modification allowed; attribution not required; premium files carry their own licence [P13] | Yes for free files | Needs a Lottie player; frame seeking via `goToAndStop` is possible but the character is baked, so little control |
| Rive | Runtimes MIT; editor plans, free exports show a splash screen; Enterprise required above $10M revenue (per Rive ToS summary) [P14] | Runtime yes | Needs the editor to author; not agent-buildable from code; splash screen risk |

Recommendation: Open Peeps or Lorelei via DiceBear for faces, Open Peeps for bodies.
Download the SVG once, commit it with its licence text in the video's `work/` folder; never hot-link.
Avoid CC BY styles unless you add credits to the end card.

### 3.2 Lip sync from audio

- Rhubarb Lip Sync (MIT; output data belongs to you) turns a WAV into timed mouth cues [P15].
- Mouth shapes: 6 basic (A to F) plus optional G, H, X. A = closed (P, B, M), B = clenched teeth, C = open, D = wide open, E = rounded, F = puckered, G = teeth on lip (F, V), H = long L, X = idle [P15].
- JSON output: `mouthCues: [{start, end, value}]` in seconds [P15].
- Recognisers: `pocketSphinx` for English, `phonetic` for non-English (less precise). A `--dialogFile` with the script text improves accuracy [P15].
- Drive deterministically: run Rhubarb once per rendered line, save `mouth-<character>-<line>.json`, commit it. In the composition, for each cue add `tl.set(mouthEl, {attr: {href: '#mouth-' + v}}, cue.start + lineOffset)` (or toggle a group's `display`). A frame at time t then always shows the same mouth. Collapse cues shorter than 1 frame (33 ms at 30 fps) into the neighbour.
- Use the 6 basic shapes plus X for flat 2D styles; G and H rarely read at 1080p [G].
- Kokoro: the open-source pipeline returns text chunks, phoneme strings and audio per chunk, not per-phoneme timings [P16, README]. So phoneme-to-viseme from Kokoro alone gives only chunk-level timing. Use Rhubarb on the WAV, or force-align with whisper word times (already in showhow for captions) plus a vowel heuristic as a fallback [G].
- Cheap fallback with no tool: toggle between closed and one open mouth on audio energy over 30 fps windows, computed offline into a JSON. Less accurate but language-independent.
- Rhubarb is a binary download. This research did not install it; installation is a separate decision.

### 3.3 3D rigged glTF in three.js

- Determinism: `AnimationMixer.setTime(t)` zeroes mixer and action times, then calls `update(t)`, so each frame can be set to an exact time [P17, source of `AnimationMixer.js`, three.js dev branch]. Call it once per render frame with the composition time.
- Morph-target lip sync: set `mesh.morphTargetInfluences[mesh.morphTargetDictionary.viseme_aa]` on every face mesh that has the target; build an `AnimationClip` of `NumberKeyframeTrack`s from Rhubarb or viseme cues, and leave those targets out of any code that also writes them [S, paprika3d guide].
- VRM models expose `aa`, `ih`, `ou`, `ee`, `oh` via `three-vrm`'s expression manager; legacy VRM 0.x uses A/I/U/E/O names [S].
- Sources and licences:

| Source | Licence and terms | Notes |
|---|---|---|
| Quaternius (Universal Base Characters, Universal Animation Library) | CC0, commercial use fine [P18, S] | 6 rigged base characters, 120+ animations on a shared humanoid rig. Low-poly stylised. Best fit |
| Kenney character packs | CC0 [P19] | Blocky or toon; mostly game style, rig varies |
| Mixamo (Adobe) | Free, royalty free commercial use in projects; cannot redistribute raw character or animation files; cannot use to train ML models [P20, S for edge cases] | Needs Adobe sign-in to download. Downloading is a manual step; do not automate. Keep downloaded FBX out of public repos |
| VRoid Studio / VRM | pixiv guidelines allow profit from videos made with VRoid Studio models; base-model content is not CC0; VRoid Hub models carry per-model terms [P21] | Anime look; check per model |
| Ready Player Me | Closed 2026-01-31 after Netflix acquisition (announced 2025-12-19); API and hosted avatars offline; sources disagree on whether old exported GLBs are usable [P22, S] | Do not build on it |

- Cost in effort: GLB loading, retargeting, camera, lighting, per-character material and clothing variety, plus eye and head tracking. Roughly 3 to 5 times the 2D effort for a comparable scene [G, my estimate].
- Look risk: stylised low-poly 3D reads as "game", not "HR". Fine for tech explainers; weaker for sensitive workplace scenes.

### 3.4 AI avatars (HeyGen, Synthesia) via media-use

- `media-use` routes avatar video through HeyGen: `--type video` for a presenter speaking; credits and sign-in rules are in `C:\Users\BeerdeVreeze\.agents\skills\media-use\SKILL.md` (read 2026-11-27). Do not volunteer prices; use `--plan`.
- HeyGen API pay-as-you-go prices are in flux; sources disagree, so do not budget from this file. One consistent set: Avatar III digital twin about $0.60/min, Avatar IV photo about $2.31/min, Avatar V twin about $7.20/min; HeyGen's own blog quotes $0.05 to $0.10 per second for newer models [S]. Check the HeyGen help page (P23) before spending.
- Consent: HeyGen requires proof of consent for a digital twin (on-camera statement with one-time code, same-person check); creating avatars of others without consent is prohibited; actors can request removal and the creator must honour it [P24, S]. Synthesia: stock avatars may not be used for paid social ads, endorsements, news or political content without written consent; custom avatars need the individual's consent; removing watermarks or provenance marks is banned [S, adtestbench and AUP summary].
- Disclosure (EU AI Act, Regulation 2024/1689): Art. 50(4) requires deployers of AI that generates or manipulates image, audio or video that constitutes a deep fake to disclose it. A deep fake is content that appreciably resembles existing persons, objects, places or events and would falsely appear authentic (Art. 3(60)) [P25]. Where the work is evidently artistic, creative, satirical, fictional or analogous, the duty shrinks to disclosing existence in a way that does not hamper enjoyment [S via search; check the Art. 50(4) text in P25].
- Applies from 2 August 2026. The Digital Omnibus (Regulation 2026/1744, in force 2026-07-27) did not delay Art. 50(4); it moved the Art. 50(2) marking duty for systems already on the market to 2026-12-02 [S, secondary summaries; verify on EUR-Lex]. Commission guidelines (C/2026/6005, 2026-11-12) read "deepfake" broadly, including things that "could exist" [S].
- Practical rule: a synthetic presenter that looks like a real person to a viewer is likely in scope. Put "AI-generated presenter" on screen (end card is acceptable only for evidently fictional work) and in the written companion. Stylised SVG or 3D cartoon characters are not photoreal and are unlikely to be deepfakes, but disclosing that voices are synthetic is cheap and honest.
- Avatars for HR content also raise internal trust questions: a realistic AI "colleague" delivering a harassment policy can feel evasive. Prefer a named human on the cover sheet who owns the policy.
- Not verified: whether a fictional, non-real-person photoreal HeyGen stock avatar counts as a deepfake in a given enforcement context. Ask counsel for anything public.

## 4. Multiple speakers

### Voices

- Kokoro is Apache-2.0 licensed with many voices [P16]. `npx hyperframes tts --list` lists voice ids. Assign one id per character and keep it fixed across the video.
- Choose voices that differ in pitch and pace, not only gender. Check by ear that a listener can tell speakers apart without captions.
- Do not pick a voice to signal a trait (accent as "the harasser"). Rotate who plays what across scenarios.
- Generate each line as its own WAV (also what Rhubarb needs), place them on the timeline at fixed offsets, and add 150 to 300 ms of room tone between turns [G].
- Overlapping speech: avoid it in v1; one voice at a time makes captions, lip sync and clarity trivial.

### Captions with speaker identification

- BBC Subtitle Guidelines: colour is the preferred way to separate speakers; palette limited to white (#FFFFFF), yellow (#FFFF00), cyan (#00FFFF), green (#00FF00) on a black background [S, search summary; current version is v1.2.5, March 2026, and the colours section was not read directly]. P26 is the guideline document.
- Older BBC online guidance (v1.1): once a speaker has a colour, keep it; white can serve any number of speakers; use cyan and green sparingly (hard for low-vision viewers), green least; a label such as `MAN:` resolves ambiguity; `BOTH:` and `ALL:` for simultaneous speech [S].
- Ofcom's UK on-demand code adds magenta as a fifth colour [S, single source].
- For showhow: colour alone fails for colour-blind viewers and in greyscale prints. Use colour plus a short name label on the first line of each turn change (`Sam:`), and keep per-character colours consistent across videos in a series.
- Keep the narrator in white or yellow (BBC convention treats the narrator as yellow [S]) and avoid using the same colour as a character.
- Check contrast against the theme background, not only black; WCAG 2.2 AA is 4.5:1 for text [G].

## 5. Diversity and inclusion without tokenism

- Vary on purpose, not as decoration: across a set of scenarios, rotate who holds power, who gets harassed, who intervenes. One scene should not carry every demographic.
- Do not link an identity trait to the wrong behaviour. The bad behaviour is the subject, not the person's group [G, supported by P8].
- Include people the prototype misses as targets (men, older workers, LGBTQ people, people with disabilities) [S, Kaiser et al. summary].
- Names, accents and clothing: use ordinary names and realistic workplace clothing; avoid costume signals of culture. Let one detail be incidental (a wheelchair user who is simply the team lead) rather than the scene's lesson [G].
- Open Peeps and Humaaans both have a range of skin tones, hair, ages and body types; check the actual set for ability and religious dress coverage before promising it [G, unverified in the files].
- Make characters fictional composites. Do not base a face on a real colleague, a celebrity or a real complainant. For photoreal avatars, a real person's likeness needs written consent (see 3.4); for illustration, avoid caricatures of identifiable people.
- Co-review scripts with someone from an affected group or the HR owner before release; stereotypes are easiest to see from outside the author's head [G].
- Accessibility: do not rely on skin or hair colour alone to tell characters apart; give each a distinct silhouette, clothing colour and caption colour, and add alt text or a cast list in the companion.

## Options for showhow

| Approach | Look | Effort | Cost | Licence risk | Determinism | Best for |
|---|---|---|---|---|---|---|
| A. SVG parts (Open Peeps / Humaaans CC0) with GSAP rig and Rhubarb mouths | Flat, warm illustration | Low to medium | Free (Rhubarb binary is a manual install) | Very low (CC0) | Full | HR scenarios, how-tos, character-led explainers |
| B. DiceBear avatars (CC0 styles) as speaker badges only | Head-and-shoulder icons | Very low | Free | Low (avoid CC BY or credit) | Full | Dialogue explainers with little action, voice-over plus caption chips |
| C. Lottie or Rive character files | Polished, baked animation | Medium | Free to paid | Medium (per file licence; Rive splash on free export) | Good for Lottie (seekable), limited control | One-off animated spots, not agent-built scenes |
| D. 3D glTF (Quaternius CC0, Mixamo animations) with AnimationMixer.setTime | Low-poly 3D | High | Free | Low (CC0) to medium (Mixamo terms, manual download) | Full | Tech or physical-task explainers, spatial scenes |
| E. VRM/VRoid models | Anime 3D | High | Free | Medium (per-model terms) | Full | Niche audiences |
| F. HeyGen/Synthesia avatar | Photoreal presenter | Low | Paid, price unstable | Medium to high (consent, AI Act Art. 50, vendor AUP) | Not deterministic (cloud render) | Presenter-led policy announcements where realism is wanted |
| G. Live-action or stock footage of actors | Real | Very high | High | High (likeness rights) | n/a | Out of scope |

## Recommendation (ranked)

v1:

1. Option A. Build a `characters/` asset kit: a small cast (4 to 6 Open Peeps parts, different ages, builds, skin tones), a documented rig (groups, pivots, pose and expression names), and a `speak(line)` helper that reads a Rhubarb JSON and emits GSAP `set`s. Keep licence text in each video's `work/sources.md`.
2. One Kokoro voice per character, one WAV per line, Rhubarb with `--dialogFile`, colour plus label captions.
3. Script rules for scenario videos: mixed examples (wrong, then right), one named rule, end on an action and a contact, no graphic conduct, rotate who plays which role, and a one-line "AI-generated voices and characters" credit.
4. Add a note to the written companion that a video is not a substitute for live, interactive training on sensitive topics [P5, S].

Later:

5. Option B chips for dialogue-only videos, once voices are in place.
6. Option D for tech or physical explainers (Quaternius characters, Mixamo animations only if Beer downloads them himself), with morph-target lip sync driven by the same Rhubarb JSON.
7. Option F only for announcement-style videos, behind an explicit user request, with consent and disclosure checks and a counsel review for public use.
8. Skip: Ready Player Me, CC BY styles unless credited, Rive for agent-built scenes, any real person's likeness.

## What I could not verify

- Full-text effect sizes for Taylor et al. (2005) and Schroeder et al. (2013) (abstract-level only), and Mayer's exact numbers (secondary summary).
- BBC colours section (read via secondary summaries), Quaternius per-pack licence beyond the two named packs, and the EU Commission Art. 50 guidelines (summaries only).
- No effectiveness research comparing vendor video styles; no study of learning outcomes with realistic virtual instructors and uncanny valley.
- HeyGen and Synthesia prices (sources conflict), and Open Peeps diversity coverage (ability, religious dress).

## Sources

All read 2026-11-27. Entries marked (search) were read as search-result summaries, not the full page.

1. Taylor, Russ-Eft and Chan (2005), A meta-analytic review of behavior modeling training, J Applied Psychology 90(4):692-709. https://pubmed.ncbi.nlm.nih.gov/16060787/ (abstract; ERIC https://eric.ed.gov/?id=EJ936609)
2. Schroeder, Adesope and Gilbert (2013), How effective are pedagogical agents for learning?, J Educ Computing Research 49(1):1-39. https://doi.org/10.2190/EC.49.1.a (abstract and search summary)
3. Mayer, Principles based on social cues in multimedia learning, Cambridge Handbook of Multimedia Learning. https://www.cambridge.org/core/books/abs/cambridge-handbook-of-multimedia-learning/principles-based-on-social-cues-in-multimedia-learning-personalization-voice-image-and-embodiment-principles/3841340D8AD820C26DBCD39AE664BCEC (search)
4. Mayer principle summaries: https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-research-based-principles-for-designing-multimedia-instruction-mayer.pdf (search)
5. EEOC Select Task Force on the Study of Harassment in the Workplace, co-chairs' report (2016). https://www.eeoc.gov/select-task-force-study-harassment-workplace and https://www.eeoc.gov/sites/default/files/migrated_files/eeoc/task_force/harassment/report.pdf (search)
6. Dobbin and Kalev (2016), Why diversity programs fail, HBR. https://hbr.org/2016/07/why-diversity-programs-fail (search)
7. Mathur and Reichling (2016), Navigating a social world with robot partners, Cognition 146:22-32. https://www.researchgate.net/publication/282153342 (search); Katsyri et al. (2019) http://www.beatricedegelder.com/documents/Katsyri2019.pdf (search)
8. Kaiser et al. (2022), Gender prototypes shape perceptions of harassment, Current Directions in Psychological Science. https://doi.org/10.1177/09637214221078592 (search)
9. Open Peeps, CC0. https://www.openpeeps.com/ (fetched)
10. Humaaans, CC0. https://www.humaaans.com/ (fetched)
11. Blush licence. https://blush.design/license (search)
12. DiceBear style licences. https://www.dicebear.com/licenses/ (fetched)
13. Lottie Simple License. https://lottiefiles.com/page/license (search)
14. Rive runtime licence and pricing. https://github.com/rive-app/rive-runtime/blob/main/LICENSE and https://rive.app/pricing (search)
15. Rhubarb Lip Sync README and licence. https://raw.githubusercontent.com/DanielSWolf/rhubarb-lip-sync/master/README.adoc and https://raw.githubusercontent.com/DanielSWolf/rhubarb-lip-sync/master/LICENSE.md (fetched)
16. Kokoro README (Apache-2.0, phoneme output). https://raw.githubusercontent.com/hexgrad/kokoro/main/README.md (fetched)
17. three.js `AnimationMixer.setTime` source. https://raw.githubusercontent.com/mrdoob/three.js/dev/src/animation/AnimationMixer.js (fetched); docs https://threejs.org/docs/pages/AnimationMixer.html
18. Quaternius Universal Animation Library and Base Characters. https://quaternius.com/packs/universalanimationlibrary.html and https://quaternius.com/packs/universalbasecharacters.html (search); FAQ https://quaternius.com/faq.html (fetched: each kit is CC0 or the QAL licence, listed per kit)
19. Kenney. https://kenney.nl/support (search)
20. Mixamo FAQ. https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html (search; direct fetch returned boilerplate)
21. VRoid guidelines. https://vroid.com/en/studio/guidelines and https://vroid.pixiv.help/hc/en-us/articles/360016417013 (search)
22. Ready Player Me closure. https://techcrunch.com/2025/12/19/netflix-acquires-gaming-avatar-maker-ready-player-me/ and https://variety.com/2025/digital/news/netflix-acquires-ready-player-me-games-avatar-creation-1236612915/ (search)
23. HeyGen API pricing. https://help.heygen.com/en/articles/10060327-heygen-api-pricing-explained (search; not opened)
24. HeyGen avatar consent. https://developers.heygen.com/docs/avatar-consent and https://www.heygen.com/moderation-policy (search); Synthesia AUP https://www.synthesia.io/legal/acceptable-use-policy (search)
25. Regulation (EU) 2024/1689, Art. 50 and Art. 3(60), consolidated 2026-07-27. https://eur-lex.europa.eu/eli/reg/2024/1689/2026-07-27/eng ; Commission guidelines https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A52026XC06005 ; summary https://www.orrick.com/en/Insights/2026/08/EU-AI-Act-Transparency-Obligations-for-AI-Generated-Content-Article-50 (all via search summaries)
26. BBC Subtitle Guidelines v1.2.5 (March 2026). https://wallspace.studio/docs/matt-architecture/BBC%20Subtitle%20Guidelines%20v1.2.5%20March%202026.pdf (mirror, not opened); older online guidelines https://studylib.net/doc/18235197/bbc.co.uk-online-subtitling-editorial-guidelines-v1.1 (search)
27. Vendor positioning and Powtoon compliance tips. https://www.powtoon.com/blog/5-tips-for-making-the-best-videos-for-compliance-training/ and https://think.vyond.com/complete-guide-to-animated-training-videos (search)
28. paprika3d, three.js morph-target lip sync. https://paprika3d.com/docs/guides/threejs-morph-targets-lip-sync (search)
