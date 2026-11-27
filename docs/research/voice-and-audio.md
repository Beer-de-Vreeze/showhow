# Voice and audio research for showhow

Date read: 2026-11-27.
Scope: what would make showhow narration, caption timing and music clearly better.
Nothing was downloaded, installed or run.
Claims marked (secondary) come from blogs or aggregators, not an official repo, card or license file.
Claims marked (unverified) I could not confirm.

## Summary

- No open-weight model I could verify beats Kokoro on English quality while also being permissively licensed, CPU-friendly and easy on Windows; keep Kokoro as the default [1][14].
- The one real gap is Dutch and German: Kokoro has neither, and the candidates are Pocket TTS (CPU, German listed, Dutch claimed in the README only) and Chatterbox Multilingual (MIT, Dutch and German, but now unmaintained) [2][3][5].
- The biggest concrete problem found is licensing: MusicGen weights are CC BY-NC 4.0, so the "generate one with MusicGen" fallback in `SKILL.md` is not safe for commercial users [20].
- Caption timing can improve without any new model: showhow already has the script text, so forced alignment (torchaudio, WhisperX wav2vec2 alignment, or MFA) beats re-transcribing the TTS output [24][26][29].
- Pronunciation fixes can use Kokoro's inline IPA markup instead of respelling the text [18].

## What showhow does today (from the repo)

- `npx hyperframes tts` with Kokoro, default voice `af_heart`.
- `scripts/install.ps1` installs a Python 3.12 venv with `kokoro-onnx==0.6.1`, `soundfile`, `transformers`, `torch==2.14.1` (the installer step is named "Kokoro voice and MusicGen music"), `numpy`, plus `whisper-cli` b5130 from whisper.cpp and ffmpeg via winget.
- It installs no CUDA build; the optional earshot QA step is documented as "CPU torch".
- So the baseline is CPU-first Windows with no GPU assumption.
- Narration is English only; other languages get English narration with captions.
- Music: bundled tracks, then Incompetech (CC BY), then MusicGen on request.

## TTS models

Quality evidence is the Artificial Analysis Speech Arena Elo (blind votes, higher is better) read on 2026-11-27 [14].
Kokoro is rank 70 at 1060 out of roughly 100 entries.
Arena scores are crowd preference on short English samples, not narration-length MOS, so treat gaps under about 30 Elo as noise.

| Model | License (weights) | Languages | CPU ok? | Quality evidence | Notes |
|---|---|---|---|---|---|
| Kokoro-82M v1.0 (current default) | Apache-2.0 [2] | en-US, en-GB, es, fr, it, pt-BR, hi, ja, zh; no nl, no de [2] | Yes, 82M params | Arena 1060, rank 70 [14] | No cloning. Inline IPA markup. Weak on short (<10-20 tokens) and long (>400 tokens) utterances; chunk to 100-200 tokens [2]. Repo last pushed 2025-08 [1]. |
| Pocket TTS (Kyutai, 100M) | Code MIT; model card CC BY 4.0, attribution required [3][4] | Model card: en, fr, de, pt, it, es. README also lists nl but ships no Dutch voice (unverified) [3][4] | Yes, built for CPU; Kyutai claims ~6x real-time on an M4 [3]. A 4-core Xeon benchmark measured RTF 0.71 and UTMOS 4.10, a notch below Kokoro (secondary) [21] | Not on the Arena list I read | Windows x86 standalone binary, no Python or PyTorch, needs AVX2 [3]. Cloning from a wav. Per-voice licenses on the `kyutai/tts-voices` page [3]. Weak on foreign proper nouns (secondary) [21]. Active: pushed 2026-11-23 [1]. |
| Chatterbox: Multilingual V3 (0.5B), Turbo (350M), Nano (110M) | MIT [5] | 23 on the card incl. nl, de, fr, es; Turbo and Nano English [5][6] | Nano targets CPU, 3x real-time on 8 cores [5]; V3 and Turbo want a GPU (unverified) | Arena: Chatterbox 1021 (rank 87); hosted Chatterbox HD 1112 [14] | README: retired and unmaintained since 2026-08, repo kept as an MIT archive [5]. Paralinguistic tags (`[laugh]`) on Turbo and Nano. Built-in cloning. |
| Qwen3-TTS 0.6B / 1.7B | Apache-2.0 [7] | zh, en, ja, ko, de, fr, ru, pt, es, it; no nl [7] | Examples use CUDA, bf16, flash-attention [7]; CPU speed unknown | Arena 932-942, rank 93-96 [14] | Natural-language style instructions (tone, emotion, speed), 3-second cloning, voice design [7]. Scores below Kokoro despite being larger. |
| Kyutai TTS 1.6B | CC BY 4.0 [8] | en, fr | GPU oriented | Not on the list I read | Voices limited to Kyutai's embeddings, no arbitrary cloning [8]. Superseded for our needs by Pocket TTS. |
| Fish Audio S2 / S2.1 Pro | "other" (Fish research license); repo NOASSERTION; S1-mini CC BY-NC-SA [1][9] | 80+ listed on the S2 card [9] | GPU | S2.1 Pro 1181 (rank 25), S2 Pro 1104 (rank 48), Drama 3 1278 (rank 9) [14] | Best quality found, but the arena entries are the hosted API ($15 per 1M chars). Open weights need a license read before commercial use. |
| Voxtral TTS (Mistral, 4B) | CC BY-NC 4.0 [10] | en, fr, es, pt, it, nl, de, ar, hi [10] | GPU | Voxtral TTS 1094 (rank 51); "Voxtral 3 TTS" 1211 (rank 20) is hosted [14] | Covers Dutch and German but non-commercial. |
| F5-TTS | Code MIT; weights CC BY-NC 4.0 [1][11] | en, zh | GPU preferred | Not on the list I read | Weights non-commercial. Skip. |
| XTTS v2 (Coqui) | Coqui Public Model License, non-commercial (secondary) | 17 | GPU preferred | n/a | Company shut down (secondary). Skip. |
| Orpheus 3B | Apache-2.0 [12] | en | GPU, heavy | Not on the list I read | Emotion tags like `<laugh>`. Last push 2025-12 [1]. Too heavy for a no-GPU default. |
| Dia 1.6B (Nari) | Apache-2.0 [13] | en only [13] | GPU | Not on the list I read | Dialogue and nonverbals, not narration. Last push 2025-11. |
| Sesame CSM-1B | Apache-2.0 [11] | en | GPU preferred | Not on the list I read | Conversational, not tuned for narration. Last push 2025-05. |
| Zonos v0.1 | Apache-2.0 [11] | multilingual (claimed) | GPU | Not on the list I read | Last push 2025-03; stale. |
| VibeVoice (Microsoft) | MIT repo, research-use intent [15] | en, zh on the 1.5B card [15] | GPU | VibeVoice 1.5B 954, rank 92 [14] | Microsoft removed the TTS code in 2025-09 after misuse [15]. Avoid. |
| Piper (OHF `piper1-gpl`) | Engine GPL-3.0; each voice has its own license [16] | Many, incl. nl_NL, nl_BE and de [17] | Yes, very fast | Not on the Arena list | Fast but plainly robotic next to Kokoro. GPL engine is fine as an external tool, awkward to bundle. Seeking maintainers [16]. |
| StyleTTS2 | MIT code (secondary) | en | GPU preferred | n/a | Kokoro is built on it [2]; no reason to use it directly. |

Reading this table:

- Hosted models dominate the top of the Arena (Fish, Voxtral 3, Eleven v3 at 1194); the permissive open field tops out around Kokoro and Chatterbox [14].
- "Newer" does not mean "better here": Qwen3-TTS and VibeVoice score below Kokoro [14].
- Kokoro has had no new model release since v1.0 in January 2025 [2].
- Practical conclusion: do not swap the English default.

## Voice cloning, consent and ethics

- Pocket TTS, Chatterbox, Qwen3-TTS and F5 can clone from seconds of audio [3][5][7].
- Showhow narrates product docs; cloning adds legal and trust risk and no quality gain over a good stock voice.
- If ever offered: clone only the user's own voice or one with written consent, keep the consent note in `work/`, never clone a public figure, and disclose synthetic narration in the video description.
- Kyutai TTS 1.6B deliberately restricts voices [8]; Microsoft pulled VibeVoice TTS code over misuse [15]; Resemble AI retired Chatterbox to focus on deepfake detection [5].
- Recommendation: no cloning in showhow by default.
- Pocket TTS voices carry per-voice licenses; check them before shipping any bundled voice [3].

## Multi-language narration and dubbing

| Language | Local options that cover it | Verdict |
|---|---|---|
| Spanish, French | Kokoro (1 to 3 voices each, thin G2P) [2]; Pocket TTS [3]; Qwen3-TTS [7]; Chatterbox [5] | Kokoro works for short clips; Pocket TTS or Qwen3-TTS may sound better (unverified, needs a listening test). |
| German | Pocket TTS (`juergen`) [3]; Qwen3-TTS [7]; Chatterbox [5]; Piper [17]; Voxtral, non-commercial [10] | Pocket TTS for CPU, Qwen3-TTS if a GPU exists. |
| Dutch | Chatterbox Multilingual [5]; Piper nl_NL and nl_BE [17]; Voxtral, non-commercial [10]; Pocket TTS README claims it but no Dutch voice is listed [3] | Chatterbox is the only permissive, natural-sounding option I could verify; it is unmaintained and probably wants a GPU. Hosted ElevenLabs is the safe Dutch fallback. |

Dubbing (re-voicing existing speech) is out of scope: showhow videos are generated from text, so the cheaper path is translate the script, then synthesise in the target language.
Keep captions in the target language and have a native speaker check the script; machine-translated UI strings are the real risk, not the voice.
Kokoro needs `lang_code` to match the voice (`a`, `b`, `e`, `f`, `h`, `i`, `j`, `p`, `z`) [2]; the existing `npx hyperframes tts --list` check in `SKILL.md` covers that.

## Pronunciation control

| Model | Lexicon / phoneme / IPA | Notes |
|---|---|---|
| Kokoro | Inline IPA: `[Kokoro](/kˈOkəɹO/)` overrides one word; misaki G2P with espeak-ng fallback [2][18] | Verified in the misaki README. Whether `npx hyperframes tts` passes the markup through is unverified; test with one word. |
| Pocket TTS | No phoneme input documented [3] | Respell only. |
| Chatterbox | No phoneme input documented [5] | Respell only; tags cover non-speech sounds. |
| Qwen3-TTS | Natural-language instructions for tone and pace; no lexicon documented [7] | Respell only. |
| Piper | Phoneme input via espeak-ng voices [16] | Strongest control, weakest voice. |
| ElevenLabs | Pronunciation dictionaries (alias or phoneme rules) | Hosted only (secondary, not re-read here). |
| Azure Neural | SSML `<phoneme>`, `<sub>`, `<break>`, `<emphasis>` | Standard SSML, hosted only (secondary, not re-read here). |

Practical rule: keep a per-project `work/pronunciations.md` mapping product terms to IPA, use Kokoro IPA markup first and respelling second.

## Hosted fallback

| Service | Price | Per minute (about 1,000 chars) | License and privacy |
|---|---|---|---|
| ElevenLabs Flash v2.5 / Turbo | $0.04 per 1K chars [19] | about $0.04 | Commercial use on paid plans; script is sent to ElevenLabs. Prices were cut 20% with Eleven v4 in Oct 2026 [19]. |
| ElevenLabs Multilingual v2 / v3 / v4 | $0.08 per 1K chars [19] | about $0.08 | Best Dutch and German quality; same privacy note. |
| OpenAI gpt-4o-mini-tts | $0.60 per 1M text tokens in, $12 per 1M audio tokens out [22]; about $0.015 per minute is a secondary estimate [22] | about $0.015 | Deprecated: tts-1, tts-1-hd and gpt-4o-mini-tts shut down 2027-01-06, replacement `gpt-realtime-2.1-mini` [22]. Do not build on it. |
| Azure Neural TTS | $15 per 1M chars; Neural HD $22 per 1M [14] | about $0.015 to $0.022 | 0.5M chars free per month [23]; SSML control; regional data residency. |

All four send the script to a third party; the script is usually public product copy, but flag it for private repos.

## Word-level timing and captions

Today `whisper-cli` transcribes the TTS output and supplies word times.
For generated speech the text is already known, so the job is alignment, not recognition.
Whisper word timestamps come from cross-attention and can drift, and ASR can mishear product names (the reason the skill needs a mispronunciation check at all) [24].

| Tool | License | Windows | Languages | Verdict |
|---|---|---|---|---|
| torchaudio forced alignment (MMS_FA) | BSD-2-Clause [29] | Already in the torch venv | Many via MMS (unverified in the pinned torchaudio) | Lightest option: no new dependency. Check the API is not deprecated in the pinned version. |
| WhisperX | BSD-2-Clause, active (pushed 2026-11-21) [24] | `pip install whisperx`, CPU works, CUDA 12.8 optional [24]; torch pin conflict with `install.ps1` unverified | wav2vec2 alignment models incl. nl, de, fr, es, pt [25] | Best fit if torchaudio falls short. Its align step works on given text without transcribing. |
| Montreal Forced Aligner | MIT, active [26] | Needs conda or mamba [27] | Pretrained models for many languages incl. Dutch and French [28] | Most accurate on clean TTS audio and gives phone timing, but a second environment is heavy. |
| aeneas | AGPL-3.0 [30] | Painful build | Many | Skip: AGPL, awkward on Windows. |
| stable-ts | MIT, archived and paused [31] | Pip | Whisper languages | Skip: unmaintained. |
| whisper-timestamped | AGPL-3.0 [32] | Pip | Whisper languages | Skip: AGPL. |
| whisper.cpp `-ml 1`, `-sow` [33] | MIT | Already installed | Whisper languages | Cheap tweak only; same drift. |

A zero-dependency alternative: showhow already measures each scene clip, so use the clip length as the sentence time and distribute words inside a sentence by character count.
Kokoro's Python `KPipeline` yields graphemes, phonemes and audio per chunk [2]; whether the pinned `kokoro-onnx` exposes timestamps is unverified.

## Music

| Source | License | Notes |
|---|---|---|
| Incompetech (Kevin MacLeod) | CC BY; attribution required, paid license removes it [34] | Already the first fallback in `SKILL.md`. |
| Kenney, OpenGameArt | CC0 | Already used for SFX [35]; OpenGameArt also hosts CC0 music. |
| Free Music Archive | Per-track Creative Commons, CC0 to CC BY-NC | Filter strictly on CC0 or CC BY; the terms URL I tried returned 404, so read the license guide first [36]. |
| Pixabay Music | Pixabay Content License | License page blocked scraping here, so terms not re-read (unverified). |
| Openverse | CC0 and CC BY filters | Already behind `media-use` in `references/audio.md`. |

Local generative music:

| Model | License | Verdict |
|---|---|---|
| MusicGen small / medium / large | Code MIT [37]; weights CC BY-NC 4.0 [20] | Non-commercial only. Contradicts the current `SKILL.md` fallback as a safe default. Gate it behind a warning or drop it. |
| Stable Audio Open 1.0 / Small | Stability AI Community License: free under US $1,000,000 annual revenue, enterprise license above [38]; gated on Hugging Face [39] | Up to 47 s, English prompts, 44.1 kHz stereo. Needs a Hugging Face login and license acceptance, so awkward for an unattended installer. |
| ACE-Step 1.0 | Repo Apache-2.0 [40]; weights license not verified | Full tracks with vocals; check the weights card before relying on it. |

A generator rarely beats a curated CC BY track for teaching videos, and the skill already defaults to no music for how-tos, so generative music is low value.

## Recommendation (ranked)

1. Fix the MusicGen license trap. Change `SKILL.md` and `references/audio.md` so MusicGen is only offered after the user confirms non-commercial use, or replace it with a curated CC0/CC BY list. Drop `transformers` and `torch` from `install.ps1` if nothing else needs them (earshot may). Effort: S.
2. Replace transcribe-the-TTS with forced alignment of the known script. Try torchaudio MMS_FA first (no new dependency), then WhisperX align if quality falls short; keep whisper-cli only for the mispronunciation check. Effort: M (a day: script, per-clip words JSON, a test on one video).
3. Use Kokoro IPA markup for pronunciation fixes and add `work/pronunciations.md`. First test that `npx hyperframes tts` passes `[word](/ipa/)` through. Effort: S.
4. Add optional non-English narration. Spanish and French stay on Kokoro; German and Dutch need a second engine. Prefer Pocket TTS for German on CPU (Windows binary; add a CC BY credit to `credits.txt`) and test its Dutch before promising it. Use Chatterbox Multilingual (MIT) for Dutch if a GPU exists, otherwise offer ElevenLabs as a hosted opt-in. Keep "English narration plus translated captions" as the default. Effort: L (a `--lang` flow, voice mapping, a listening test per language, an installer branch).
5. Keep Kokoro as the English default. Re-check when something permissive, CPU-capable and above about 1100 Arena Elo appears (Fish S2.1 and Voxtral are better but not commercially clean). Effort: none now.
6. Do not add voice cloning. If a user asks, require their own voice plus a consent note. Effort: none.
7. Skip OpenAI TTS (shutdown 2027-01-06); document ElevenLabs and Azure as optional paid fallbacks only. Effort: S.

## What I could not verify

- Pocket TTS Dutch quality (README claims Dutch, no Dutch voice shipped) and its real speed on a typical Windows laptop.
- Chatterbox Multilingual V3 CPU speed and Arena score.
- Whether `npx hyperframes tts` accepts Kokoro IPA markup or exposes per-token timestamps.
- Weights licenses for ACE-Step and Fish S2.1 Pro, and the Pixabay license text.
- Whether the pinned `torch` and `transformers` in `install.ps1` coexist with `whisperx`, and whether torchaudio MMS_FA is still available in that torch version.

## Sources

All read 2026-11-27.
Items marked (secondary) are not official.

1. GitHub REST metadata (license, last push) per repo - https://api.github.com/repos/hexgrad/kokoro, .../resemble-ai/chatterbox, .../kyutai-labs/pocket-tts, .../canopyai/Orpheus-TTS, .../nari-labs/dia, .../SWivid/F5-TTS, .../microsoft/VibeVoice, .../OHF-Voice/piper1-gpl, .../fishaudio/fish-speech
2. Kokoro-82M model card and VOICES.md - https://huggingface.co/hexgrad/Kokoro-82M ; https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md ; https://github.com/hexgrad/kokoro
3. Pocket TTS README - https://github.com/kyutai-labs/pocket-tts
4. Pocket TTS model metadata (cc-by-4.0, languages) - https://huggingface.co/api/models/kyutai/pocket-tts
5. Chatterbox README (retired notice, V3, Turbo, Nano) - https://github.com/resemble-ai/chatterbox
6. Chatterbox model metadata (MIT, 23 languages) - https://huggingface.co/api/models/ResembleAI/chatterbox
7. Qwen3-TTS model card (Apache-2.0, 10 languages) - https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base
8. Kyutai TTS 1.6B en/fr (CC BY 4.0) - https://huggingface.co/api/models/kyutai/tts-1.6b-en_fr ; https://github.com/kyutai-labs/delayed-streams-modeling
9. Fish Audio S2 Pro and S1-mini metadata - https://huggingface.co/api/models/fishaudio/s2-pro ; https://huggingface.co/api/models/fishaudio/s1-mini
10. Voxtral TTS metadata (CC BY-NC 4.0, nine languages) - https://huggingface.co/api/models/mistralai/Voxtral-4B-TTS-2603
11. F5-TTS, Sesame CSM, Zonos metadata - https://huggingface.co/api/models/SWivid/F5-TTS ; https://huggingface.co/api/models/sesame/csm-1b ; https://huggingface.co/api/models/Zyphra/Zonos-v0.1-transformer
12. Orpheus TTS repo - https://github.com/canopyai/Orpheus-TTS
13. Dia README (English only) - https://github.com/nari-labs/dia
14. Artificial Analysis Text to Speech Arena leaderboard - https://artificialanalysis.ai/text-to-speech/arena?tab=leaderboard
15. VibeVoice README (TTS code removed 2025-09-05) and 1.5B metadata - https://github.com/microsoft/VibeVoice ; https://huggingface.co/api/models/microsoft/VibeVoice-1.5B
16. Piper (OHF) README - https://github.com/OHF-Voice/piper1-gpl
17. Piper voices, nl folder - https://huggingface.co/rhasspy/piper-voices/tree/main/nl
18. misaki G2P README (inline IPA markup, espeak fallback) - https://github.com/hexgrad/misaki
19. ElevenLabs API pricing - https://elevenlabs.io/pricing/api
20. MusicGen small model card (cc-by-nc-4.0) - https://huggingface.co/facebook/musicgen-small
21. Neo CPU TTS benchmark incl. Pocket TTS (secondary) - https://heyneo.com/blog/kokoro-supertonic-inflect-nano-pocket-tts-cpu-benchmark
22. OpenAI deprecations and pricing pages; per-minute estimate from TokenMix (secondary) - https://platform.openai.com/docs/deprecations ; https://platform.openai.com/docs/pricing ; https://tokenmix.ai/blog/gpt-4o-mini-tts-cheapest-tts-api-2026
23. Azure Speech pricing page (free tier; per-character figure taken from [14] because the page renders prices by script) - https://azure.microsoft.com/en-us/pricing/details/speech/
24. WhisperX README and repo - https://github.com/m-bain/whisperX
25. WhisperX alignment model table - https://github.com/m-bain/whisperX/blob/main/whisperx/alignment.py
26. Montreal Forced Aligner repo - https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner
27. MFA installation (conda) - https://montreal-forced-aligner.readthedocs.io/en/latest/installation.html
28. MFA pretrained acoustic models - https://mfa-models.readthedocs.io/en/latest/acoustic/index.html
29. torchaudio repo (BSD-2-Clause) - https://github.com/pytorch/audio
30. aeneas repo (AGPL-3.0) - https://github.com/readbeyond/aeneas
31. stable-ts README (development paused, repo archived) - https://github.com/jianfch/stable-ts
32. whisper-timestamped repo (AGPL-3.0) - https://github.com/linto-ai/whisper-timestamped
33. whisper.cpp CLI options - https://github.com/ggml-org/whisper.cpp/blob/master/examples/cli/README.md
34. Incompetech FAQ and licenses - https://incompetech.com/music/royalty-free/faq.html
35. OpenGameArt keyboard soundpack CC0 (cited in `references/audio.md`) - https://opengameart.org/content/keyboard-soundpack-1-typing-and-single-keystrokes
36. Free Music Archive - https://freemusicarchive.org
37. audiocraft repo (MIT code) - https://github.com/facebookresearch/audiocraft
38. Stability AI Community License - https://stability.ai/community-license-agreement
39. Stable Audio Open 1.0 model card (gated, points to Stability license for commercial use) - https://huggingface.co/stabilityai/stable-audio-open-1.0
40. ACE-Step repo (Apache-2.0) - https://github.com/ace-step/ACE-Step
