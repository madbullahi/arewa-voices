# Kimiyya

*Kimiyya* is Hausa for "science". This is an open toolkit for discussing science in Hausa: short, accurate explainers for social media, with the scientific terms explained in words Hausa speakers already use.

Most science reaches Hausa speakers in English, or not at all. Kimiyya turns one explainer at a time (what a virus is, why antibiotics don't cure a cold, how a tiny water flea tells us whether water is safe) into a script, visuals, a voiceover and captions in Hausa, with an English version alongside.

## How a topic is made

1. **Script**: a 30–60 second explainer in Hausa and English, one idea per topic (`topics/<topic>/script.json`), with every claim sourced in `sources.md`.
2. **Terms**: scientific words go through the shared glossary (`glossary/terms.csv`), so the same Hausa term is used every time.
3. **Visuals**: diagrams, posters and thumbnails with [LongCat-Image](https://github.com/meituan-longcat/LongCat-Image) (`scripts/generate_image.py`).
4. **Voiceover and video**: a recorded Hausa speaker (or a draft MMS text-to-speech voice), optionally animated as a presenter with [LongCat-Video-Avatar 1.5](https://github.com/meituan-longcat/LongCat-Video) (`scripts/make_voiceover.py`, `scripts/generate_avatar_video.sh`).
5. **Captions**: the script timed against the voiceover with the Montreal Forced Aligner, as `.srt` captions and word timings, on a laptop CPU (`scripts/align.sh`, see `docs/captions.md`).
6. **Publish**: 9:16 clips for WhatsApp Status, TikTok, Instagram Reels, YouTube Shorts and Facebook.

## Topics

| Topic | Idea | Status |
| --- | --- | --- |
| `topics/antibiotics-and-viruses/` | Antibiotics kill bacteria, not viruses, so they don't cure a cold or flu; misuse breeds resistance | English draft; Hausa script, science and Hausa review to do |
| `topics/daphnia/` | A water flea smaller than a grain of rice cleans water by filter-feeding and is used to test whether chemicals are safe | English draft; Hausa script, science and Hausa review to do |

Ideas for more are in `docs/roadmap.md`. To start one, copy a topic folder, rewrite `script.json`, and fill in `sources.md` before anything else.

## Principles

- **Accurate first.** Every claim has a named, reliable source (peer-reviewed papers, WHO, national agencies, standard methods) in the topic's `sources.md`. Say what is known and what is still uncertain.
- **Hausa by Hausa speakers.** A native speaker writes or reviews every Hausa script and caption; machine Hausa is only ever a draft.
- **Plain words, real terms.** Explain an idea in everyday Hausa first, then give the scientific term (Hausa and English) once.
- **Not medical advice.** Health topics explain the science and point to health workers and official guidance.

Full rules in `docs/ethics.md`.

## Hardware

| Step | Model | Minimum hardware |
| --- | --- | --- |
| Images | LongCat-Image (6B) | 1 GPU with ~17 GB VRAM (CPU offload), e.g. RTX 4090 |
| Video | LongCat-Video-Avatar 1.5 | Cloud GPU (A100/H100); 2 GPUs in the official commands, INT8 reduces VRAM |
| Captions | Montreal Forced Aligner (`hausa_mfa`, `english_mfa`) | Any laptop CPU |

No GPU? Write scripts, record voiceovers and make captions locally; run image and video generation on a rented cloud GPU (`docs/cloud-gpu.md`).

## Quick start

```bash
git clone https://github.com/madbullahi/kimiyya
cd kimiyya
pip install -r requirements.txt
python scripts/generate_image.py --topic topics/daphnia
```

See `docs/setup.md` for full setup.

## History

The project began as **Arewa Voices**, a toolkit for awareness campaigns on social issues in Northern Nigeria (out-of-school children; health and nutrition). Those campaigns are in the git history at commit `c62aea0`.

## Licence

Code: MIT. LongCat-Image is Apache 2.0; LongCat-Video weights are MIT. The MFA Hausa model and dictionary are CC-BY-4.0. MMS text-to-speech voices are CC-BY-NC 4.0 (non-commercial).
