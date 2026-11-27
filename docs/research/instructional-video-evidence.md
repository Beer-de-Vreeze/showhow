# Instructional video evidence for showhow

Scope: how-to and explainer video design beyond Mayer's multimedia principles (covered in another file).
Read date for every source: 2026-11-27.
CONFIRMS, CHANGES and NEW refer to the rules in `skills/showhow/SKILL.md` (Teaching laws, Script and plan, Sound) and `references/tones.md`.
Sources marked (secondary) were read through a search summary or a third-party write-up, not the primary page.

## Summary

- The core showhow design (short, task-focused, real UI, narrated, highlighted, click cues, outcome first) matches the screencast literature (Plaisant & Shneiderman 2005, van der Meij's demonstration-based training) and holds up.
- Weakest existing claim: "music hurts retention in teaching videos". The evidence is mixed (small harm in older meta-analyses, small benefit in a 2023 one); keep the no-music default but justify it by voice-first design and WCAG 1.4.7, not by a proven retention penalty.
- Captions: the 42-character line is longer than BBC (37 characters, or 68% of landscape width) and DCMP (32); vertical needs 90% width and may use 3 lines.
- Accessibility gap: WCAG 1.2.5 (AA) is met by narration only if every important visual fact is also spoken, and 1.2.2 needs captions; showhow should gate on both and ship a transcript and a sidecar caption file.
- Practice prompts and a short review help procedural learning in some studies and not in others; "Now try it" is right, and an explicit pause point plus a one-line recap of the steps are cheap additions (weak to medium evidence).

## 1. Software tutorial and screencast research

### Findings

- Plaisant & Shneiderman (2005) give ten "Show Me!" guidelines from a review of web demos and a 12-person usability test. [1]
  - Procedural instruction over conceptual content.
  - Segments of 15 to 60 seconds, each autonomous, in a linear sequence.
  - Clear, simple tasks, with the same example data across segments.
  - Voice narration synchronized with the action; a typical error is generic "advertisement-like" narration while the viewer cannot tell what is being done.
  - Be faithful to the real UI and do not shrink it.
  - Highlight the cursor with a circle, plus a click sound.
  - Zoom when text is unreadable; if you cannot do a fast zoom transition, highlight the area first, then jump.
  - Edit hard to cut words.
  - Their review found demos without voice "plainly less appealing and more difficult to follow", and long pauses were the biggest content flaw.
  - No effect sizes; usability evidence only.
- van der Meij & van der Meij built the demonstration-based training (DBT) model for software video: a preview of the outcome, short task demonstrations, and a review, grounded in Bandura's attention, retention, reproduction and motivation. [2][3]
  - 2016 (55 German pupils): demonstration plus review beat demonstration only on procedural knowledge; both raised motivation. [2]
  - 2018 (65 elementary pupils): preview, demo, review and second-demo variants all raised self-efficacy and procedural knowledge, but no condition effect; the authors blame overlap between video types and blocked access during tests. [3]
  - Brar & van der Meij 2017 (university statistics): demo plus review versus demo only; videos held motivation and attention, knowledge scores were moderate, no condition effect. [4]
  - van der Meij 2019 (61 Chinese pupils, Word tasks): advance organizers before the demos improved gain scores to the delayed post-test and the accuracy of self-efficacy appraisals. [5]
  - van der Meij & Dunkel 2020 (70 students): original videos watched 94.1%, review video 60.5%; practice with external feedback improved procedural knowledge (not declarative or transfer); review or practice raised self-efficacy. [6]
- Cueing in software video: a study of 118 experienced ICT undergraduates found no effect on task performance or cognitive load, but higher motivation (d=0.46). [7]
  A domain-expert study also found no effect (secondary, 8).
  A 2023 study of 114 nursing students (less ICT experience) reported cueing and practice helped novices (secondary, 9).
  Reading: cues help novices more than experienced users and cost little.
- Learner control: learner-paced animations beat system-paced ones even though pause buttons were rarely used (Hasler, Kersten & Sweller 2007); interactive video shortened learning time and learners used controls more on hard parts (Schwan & Riempp 2004) (secondary, 10).
- Guo et al. 2014 found students engage differently with tutorials than lectures and recommend support for "rewatching and skimming" in tutorials. [11]

### Implications for showhow

| Finding | Verdict |
|---|---|
| Highlight the target, click cue, orient with the full UI, voice synced to action, real UI | CONFIRMS "orient, point, act, result", "show the real product", click SFX |
| Same example data across segments | CONFIRMS "state carries forward"; NEW plan gate: one fictional dataset per video |
| Segments of 15 to 60 s | CONFIRMS 45-120 s total; NEW: each step group between silent holds should be 15-60 s and stand alone as a chapter |
| Highlight first when a zoom cannot be smooth | NEW small rule: ring the area before the cut |
| Review helped in one of three studies; practice helped procedural knowledge | NEW weak rules, see Rule changes |
| Cueing benefit is for novices | CONFIRMS "highlight before act" as default; can be lighter for expert audiences |
| Tutorials are skimmed and rewatched | CONFIRMS chapters and step counter |

## 2. Video engagement data

### Findings

- Guo, Kim & Rubin 2014 (6.9 million edX sessions): median engagement time is at most 6 minutes whatever the video length; the authors recommend chunks under 6 minutes. [11]
  Khan-style drawing tutorials beat slides and code screencasts; talking head interleaved with slides beat slides alone; informal beat studio polish; lectures planned for the medium beat re-cut classroom lectures; fast, enthusiastic speakers engaged most.
  Engagement means watch time, not learning.
- Wistia (secondary, 12): engagement rate is total time played divided by plays times length; under 1 minute averages about 50-52%, a slow decline to 5 minutes, bigger drops after.
  A third-party summary of the 2024 report gives instructional videos of 3-5 minutes 74% against 43% for all videos (not verified on Wistia's page).
- Vidyard Video in Business Benchmark 2025 (943,305 videos, Jan-Dec 2024), from a search summary (secondary, 13): 65% reach the end under 1 minute, 20% over 20 minutes; 2022 edition: 66% under 1 min, 56% at 1-2 min, 50% at 2-10 min.
  Different metric from Wistia; do not compare the two.
- YouTube Help "key moments for audience retention" [14]: "Intro" is the share still watching after 30 seconds; if top moments come late, move compelling content earlier because audience size falls over the video; spikes can mean viewers rewatched unclear content.
  YouTube publishes no single benchmark; "50% is good" figures attributed to Creator Academy could not be verified.
- Vertical short form (secondary, 15): since 2024-10-15 square or vertical uploads up to 3 minutes count as Shorts; vendor blogs put the sweet spot at 15-45 s for hook-led and 45-90 s for deeper content (weak).
  LinkedIn-specific length data: not found.

### Implications

- "Outcome first within 5 s": no source gives a 5 s threshold; YouTube measures 30 s and Guo says only that shorter engages more. CONFIRMS the direction; label 5 s as a heuristic.
- 45-120 s target, 180 s limit: all data say shorter wins, none sets a 45 s floor. CONFIRMS; below 45 s the `quick-tip` shape applies.
- Pacing near 150 wpm: Guo says do not slow down. CONFIRMS (section 3).
- Silent holds of about 2 s at subtask boundaries: Plaisant found long pauses hurt; Rey 2019 finds segmenting helps. CONFIRMS; keep holds short.

## 3. Narration

### Findings

- Voice: Craig & Schroeder 2017 (randomized online trial, classic TTS, modern TTS, human voice): modern TTS gave better transfer, equal credibility and facilitating-learning ratings, better training efficiency than the classic engine (secondary, 16).
  Chiou, Schroeder & Craig 2020: voice quality did not change learning but did change trust and perceptions; human voice rated above both TTS voices (d about 0.7-0.9 in the preprint) (secondary, 17).
  Mayer, Fiorella & Stull 2020 covers five other video principles, not TTS; I could not find a 2020 Mayer paper on modern TTS and treat that citation as unverified. [18]
- Speech rate: Guo mean 156 wpm (sd 31, range 48-254), faster was more engaging. [11]
  DCMP caps caption presentation at 130 wpm (lower-level), 140 (middle), 160 (upper-level) and supports editing above that. [19]
  BBC recommends 160-180 wpm for subtitles. [20]
- Personalization: Ginns, Martin & Marsh 2013 (22 studies, 3,312 students): conversational style gives retention d=0.30, transfer d=0.54, friendliness d=0.46; small non-significant effects beyond 35-minute lessons; interest not reliably raised (secondary, 21).
- Plaisant: lively, direct, concrete narration that names the effect on screen, not the layout. [1]

### Implications

- Local TTS default: CONFIRMS (modern TTS matches human voice on learning). NEW: require a modern neural voice; offer a recorded human voice for `release` and brand-facing explainers where trust matters.
- 2.5 words per second (150 wpm): CONFIRMS against Guo and BBC; sits under the DCMP upper-level cap and above the lower and middle caps. Proposed: keep 2.5 as plan value, add a measured per-scene cap of 2.7 words per second (162 wpm), because captions are verbatim.
- Second person, conversational: CONFIRMS.
- "Say the result": CONFIRMS (Plaisant).

## 4. Music and sound effects

### Findings

- Kämpfe, Sedlmeier & Renkewitz 2011 (97 studies with usable data): overall null; music disturbs reading and has small harmful effects on memory; helps emotion and sport (secondary, 22).
- de la Mora Velasco et al. 2023 (47 studies, 71 effect sizes): small positive mean effect of background music on learners, d=0.314, contradicting the cognitive-load prediction (secondary, 23).
- Rey 2012 (seductive details meta-analysis) is negative, and music is often classed as one; Lehmann & Seufert 2019 found music helped transfer; a systematic review found few multimedia-learning studies and mixed results (all secondary, 23).
- Mayer, Fiorella & Stull 2020 list seductive details as the one way not to use video; that is about extraneous video and text, not music specifically. [18]
- WCAG 1.4.7 (AAA): speech-primary audio should have no background sound, a way to turn it off, or background at least 20 dB lower than speech (W3C says about four times quieter; 20 dB is a tenth in amplitude). [24]
- WCAG 1.4.2 (A): audio that plays automatically for over 3 seconds needs a pause, stop or independent volume control; this binds the host page, not the render. [25]
- Plaisant: a click sound combined with a circle around the cursor helps viewers see when and where the click happened. [1]

### Implications

- "No music by default (it hurts retention)": CHANGES the justification, not the default. The retention penalty is not established; the defensible reasons are speech intelligibility (1.4.7), no proven benefit, and the seductive-details caution.
- Duck at 0.1 under narration: CONFIRMS, 0.1 amplitude is 20 dB; gate on the measured gap.
- Action-matched SFX: CONFIRMS (Plaisant).
- `release` music: no evidence against; it is a marketing video.

## 5. Captions and accessibility

### Findings

- WCAG 2.2 SC 1.2.2 (A) captions for prerecorded audio in synchronized media; SC 1.2.3 (A) audio description or media alternative; SC 1.2.5 (AA) audio description for prerecorded video, with the note that if all important information in the video track is already conveyed in the audio track, no additional audio description is necessary. [26][27]
- WCAG 2.2 SC 2.3.1 (A): no more than three flashes in any one second, or below the general and red flash thresholds. [28]
- BBC Subtitle Guidelines v1.2.5 [20]:
  - 160-180 wpm; minimum about 0.3 s per word (1.2 s for four words).
  - 37 characters on broadcast; online, a line at most 68% of the width of landscape 16:9, 90% for square and vertical 9:16.
  - Two lines on landscape and square; three on vertical.
  - About 10% of broadcast viewers use subtitles regularly, up to 35% for some online content; most are not hard of hearing.
  - Delivered as separate files so viewers can switch them off.
- DCMP Captioning Key: 130/140/160 wpm caps by level; each caption keeps meaning and essential vocabulary; 32-character line (secondary for the 32). [19]
- Mayer, Fiorella & Stull 2020: subtitles in the learner's second language raise learning from narrated video. [18]

### Implications

- Burned-in verbatim captions: CONFIRMS. Burned-in text meets 1.2.2 but cannot be switched off or restyled; NEW: ship a sidecar `.vtt` or `.srt` where the host supports it.
- Line length 42 characters, 2 lines: CHANGES to 37 characters or 68% of landscape width, 90% for square and vertical, 3 lines on vertical only.
- NEW gate: each caption at least 0.3 s per word and at least 1 s on screen.
- Audio description 1.2.5: NEW. Narration that names label, action and result meets the exception only if every visual fact is spoken. Gate: on-screen-only content (hook text, change-card tags, version numbers, table numbers) is spoken or in the transcript and written companion, which also serves as the 1.2.3 alternative.
- No flashing: CONFIRMS; the real WCAG test also involves area, so the strict "three per second, no strobe, no white flash frames" rule stays.
- Works muted: CONFIRMS (35% online subtitle use, BBC).

## 6. Explainer specific

### Findings

- Pre-training: knowing names and characteristics of key concepts first; 13 of 16 experiments, median d=0.75 (Mayer & Pilegard 2014; a later summary gives d=0.46) (secondary, 29). The DBT preview and advance organizer are the video form. [5]
- Signaling: moderate gains in retention, smaller in transfer (Schneider et al. 2018, 103 studies); two secondary summaries disagree on the exact g, check the paper's tables (secondary, 30).
- Segmenting: small to medium effects on retention and transfer, lower cognitive load, more learning time, stronger for high-prior-knowledge learners (Rey et al. 2019, 56 investigations) (secondary, 31).
- Generative activity (prompts to summarize or explain) improves learning from video. [18]
- Practice testing beats restudying and most other conditions (Adesope et al. 2017, 118 articles); the g=0.61 headline came from a blog and is unverified (secondary, 32).
- Review: one of three DBT studies showed a benefit, and the review video was watched by about 60%. [2][3][6]
- Worked examples (Sweller, Cooper), analogies, "explain like a teacher": not found or read in this pass; no effect sizes recorded.

### Implications

- Outcome first = preview: CONFIRMS.
- "Before you start (only if needed)": CHANGES slightly: it may also name two or three exact control labels used later, only when a step uses a label the viewer cannot guess.
- "Now try it": CONFIRMS (generative activity, practice testing); make it a specific, time-boxed task.
- `quick-tip` no recap: CONFIRMS; recap evidence is for longer multi-step tasks.
- Explainers and release videos: no extra rules found; the 2 s hold and one-screen-per-change already act as segmenting.

## Rule changes

| Rule | Current | Proposed | Evidence strength | Source # |
|---|---|---|---|---|
| Music default | None in teaching styles because "it hurts retention" | Keep default none; reword the reason: no proven benefit, speech intelligibility (WCAG 1.4.7), seductive-details caution | medium | 18, 22, 23, 24 |
| Music ducking | 0.1 under voice, 0.3 without | Keep; gate on a measured gap of at least 20 dB under narration | strong | 24 |
| Caption line | Max 2 lines of about 42 characters | 37 characters or 68% of landscape width; 90% width for square and vertical; 3 lines on vertical only | medium | 20, 19 |
| Caption timing and rate | Verbatim, one phrase at a time | Add: at least 0.3 s per word and 1 s on screen; measured narration at most 2.7 words per second per scene | medium | 11, 19, 20 |
| Narration rate | Plan about 2.5 words per second | Keep 2.5; add the 2.7 cap above | medium | 11, 19, 20 |
| Audio description | Not mentioned | Gate: every on-screen-only fact is spoken or in the transcript/companion; state this meets WCAG 1.2.5 by its exception | strong | 26, 27 |
| Caption files | Burned in only | Also ship `.vtt` or `.srt` sidecar | medium | 26, 20 |
| Segment length | Whole video 45-120 s | Each step group between holds 15-60 s and stands alone as a chapter | weak | 1, 31 |
| Practice | "Now try it" 3-5 s at the end | Keep; make it a specific task using data from the video; optional silent pause point at subtask boundaries | medium | 6, 18, 32 |
| Recap | None (quick-tip: explicitly none) | Howto of 4+ steps: one spoken line recapping the steps inside the Result beat; quick-tip unchanged | weak | 2, 3, 6 |
| Pre-training | "Before you start" for prerequisites | Also name 2-3 exact control labels used later, only when needed | weak | 5, 29 |
| Voice | Local TTS default | Keep; require a modern neural voice; offer a human recording for `release` and brand explainers | medium | 16, 17 |
| Example data | "State carries forward" | Plan gate: one fictional dataset across all steps | medium | 1 |
| Zoom | Camera moves 0.6-1.0 s | If a smooth zoom is not possible, ring the area first, then cut | weak | 1 |
| Vertical cut | Format only | Keep captions and highlights inside the platform safe zone (about the central 900x1330 px of 1080x1920, a vendor figure) | weak | 15 |
| 5 s outcome rule | "Within 5 seconds" | Keep as a heuristic; the platform's own measure is the first 30 s | weak | 14 |

## Sources

1. Plaisant & Shneiderman, "Show Me! Guidelines for Producing Recorded Demonstrations", IEEE VL/HCC 2005. http://www.cs.umd.edu/~ben/papers/Plaisant2005Show.pdf (full text, read 2026-11-27).
2. van der Meij & van der Meij, "Demonstration-based training (DBT) in the design of a video tutorial for software training", Instructional Science 44(6), 2016. https://doi.org/10.1007/s11251-016-9394-9 (abstract, read 2026-11-27).
3. van der Meij & van der Meij, "Supporting motivation, task performance and retention in video tutorials for software training", ETR&D, 2018. https://doi.org/10.1007/s11423-017-9560-z (abstract, read 2026-11-27).
4. Brar & van der Meij, "Complex software training: Harnessing and optimizing video instruction", Computers in Human Behavior 70, 2017. https://doi.org/10.1016/j.chb.2017.01.014 (abstract via search summary) (secondary), read 2026-11-27.
5. van der Meij, "Advance organizers in videos for software training of Chinese students", BJET 50(3), 2019. https://doi.org/10.1111/bjet.12619 (abstract via search summary) (secondary), read 2026-11-27.
6. van der Meij & Dunkel, "Effects of a review video and practice in video-based statistics training", Computers & Education 143, 2020. https://doi.org/10.1016/j.compedu.2019.103665 (abstract via search summary) (secondary), read 2026-11-27.
7. Cueing in videotutorials for complex software, Themes in eLearning 2020, https://eric.ed.gov/?id=EJ1291470, and Ragazou & Karasavvidis, IADIS 2021, https://files.eric.ed.gov/fulltext/ED622465.pdf (ERIC abstracts), read 2026-11-27.
8. Visual cueing and practice type with domain experts, Interactive Technology and Smart Education 20(1). https://www.emerald.com/itse/article-abstract/20/1/36/181178 (search summary only) (secondary), read 2026-11-27.
9. Signaling and practice types in video-based software training, Education Sciences 13(6), 2023. https://doi.org/10.3390/educsci13060602 (search summary only) (secondary), read 2026-11-27.
10. Hasler, Kersten & Sweller 2007, https://doi.org/10.1002/acp.1345; Schwan & Riempp 2004, Learning and Instruction 14 (search summaries only) (secondary), read 2026-11-27.
11. Guo, Kim & Rubin, "How video production affects student engagement: an empirical study of MOOC videos", L@S 2014. https://up.csail.mit.edu/other-pubs/las2014-pguo-engagement.pdf, DOI 10.1145/2556325.2566239 (full text, read 2026-11-27).
12. Wistia, https://wistia.com/blog/video-marketing-statistics and https://wistia.com/blog/optimal-video-length (figures via search summary; the 74% figure from a third-party summary) (secondary), read 2026-11-27.
13. Vidyard, Video in Business Benchmark. https://www.vidyard.com/business-video-benchmarks/ (page is script-rendered; figures via search summary) (secondary), read 2026-11-27.
14. YouTube Help, "Measure key moments for audience retention". https://support.google.com/youtube/answer/9314415 (read 2026-11-27).
15. YouTube Shorts length and safe-zone guidance via vendor blogs, e.g. https://riverside.com/blog/how-long-can-youtube-shorts-be and https://recast.studio/blog/youtube-shorts-dimension (search summaries) (secondary), read 2026-11-27.
16. Craig & Schroeder, "Reconsidering the voice effect when learning from a virtual human", Computers & Education 114, 2017. https://doi.org/10.1016/j.compedu.2017.07.003 (abstract via search summary) (secondary), read 2026-11-27.
17. Chiou, Schroeder & Craig, Computers & Education 146, 2020. https://doi.org/10.1016/j.compedu.2019.103756; Craig & Schroeder 2019, J. Educational Computing Research (search summaries) (secondary), read 2026-11-27.
18. Mayer, Fiorella & Stull, "Five ways to increase the effectiveness of instructional video", ETR&D 68, 2020. https://doi.org/10.1007/s11423-020-09749-6 (abstract, read 2026-11-27).
19. DCMP Captioning Key, presentation rate. https://dcmp.org/learn/601-captioning-key---presentation-rate (read 2026-11-27); the 32-character line from a search summary (secondary).
20. BBC Subtitle Guidelines v1.2.5. https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles (read 2026-11-27).
21. Ginns, Martin & Marsh, "Designing instructional text in a conversational style: a meta-analysis", Educational Psychology Review 25, 2013. https://doi.org/10.1007/s10648-013-9228-0 (abstract via search summary) (secondary), read 2026-11-27.
22. Kämpfe, Sedlmeier & Renkewitz, "The impact of background music on adult listeners: a meta-analysis", Psychology of Music 39, 2011. https://doi.org/10.1177/0305735610376261 (abstract via search summary) (secondary), read 2026-11-27.
23. de la Mora Velasco et al. 2023, https://doi.org/10.1177/03057356231153070; Rey 2012; Lehmann & Seufert 2019, https://doi.org/10.1002/acp.3509 (search summaries only) (secondary), read 2026-11-27.
24. W3C, Understanding SC 1.4.7 Low or No Background Audio. https://www.w3.org/WAI/WCAG22/Understanding/low-or-no-background-audio.html (read 2026-11-27).
25. W3C, Understanding SC 1.4.2 Audio Control. https://www.w3.org/WAI/WCAG22/Understanding/audio-control.html (read 2026-11-27).
26. W3C, Understanding SC 1.2.5 Audio Description (Prerecorded). https://www.w3.org/WAI/WCAG22/Understanding/audio-description-prerecorded.html (read 2026-11-27).
27. W3C, Understanding SC 1.2.2 Captions (Prerecorded). https://www.w3.org/WAI/WCAG22/Understanding/captions-prerecorded.html (fetched 2026-11-27; the 1.2.2 wording used here is the SC text as known, not re-quoted).
28. W3C, Understanding SC 2.3.1 Three Flashes or Below Threshold. https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html (read 2026-11-27).
29. Mayer & Pilegard, "Principles for managing essential processing: segmenting, pre-training and modality", Cambridge Handbook of Multimedia Learning, 2014 (chapter abstract via search summary) (secondary), read 2026-11-27.
30. Schneider, Beege, Nebel & Rey, "A meta-analysis of how signaling affects learning with media", Educational Research Review 23, 2018. https://doi.org/10.1016/j.edurev.2017.11.001 (effect sizes from two secondary summaries that disagree) (secondary), read 2026-11-27.
31. Rey et al., "A meta-analysis of the segmenting effect", Educational Psychology Review 31, 2019. https://doi.org/10.1007/s10648-018-9456-4 (abstract via search summary) (secondary), read 2026-11-27.
32. Adesope, Trevisan & Sundararajan, "Rethinking the use of tests: a meta-analysis of practice testing", Review of Educational Research 87, 2017. https://doi.org/10.3102/0034654316689306 (abstract via search summary; g=0.61 from a blog) (secondary), read 2026-11-27.
