# Arewa Voices

An open toolkit for making short, accurate, Hausa- and English-language social media content about issues facing Northern Nigeria, using open-source AI models from [Meituan LongCat](https://github.com/meituan-longcat).

## What it does

1. **Script**: write a short campaign script in Hausa and English (`campaigns/<issue>/script.json`).
2. **Visuals**: generate posters, thumbnails and quote cards with [LongCat-Image](https://github.com/meituan-longcat/LongCat-Image) (`scripts/generate_image.py`).
3. **Video**: animate a presenter portrait to a voiceover with [LongCat-Video-Avatar 1.5](https://github.com/meituan-longcat/LongCat-Video) (`scripts/generate_avatar_video.sh`).
4. **Publish**: export 9:16 clips for WhatsApp Status, TikTok, Instagram Reels, YouTube Shorts and Facebook.

## First campaign

`campaigns/out-of-school-children/` is a back-to-school awareness campaign aimed at parents and community leaders.

`campaigns/health-nutrition/` is a first-1,000-days campaign on breastfeeding, complementary foods and early clinic visits.

More issues are planned (see `docs/roadmap.md`), including farming and climate, and verified safety information.

## Hardware

| Step | Model | Minimum hardware |
| --- | --- | --- |
| Images | LongCat-Image (6B) | 1 GPU with ~17 GB VRAM (CPU offload), e.g. RTX 4090 |
| Video | LongCat-Video-Avatar 1.5 | Cloud GPU (A100/H100); 2 GPUs in the official commands, INT8 reduces VRAM |

No GPU? Write scripts and captions locally, then run generation on a rented cloud GPU.

## Quick start

```bash
git clone <this repo>
cd arewa-voices
pip install -r requirements.txt
python scripts/generate_image.py --campaign campaigns/out-of-school-children
```

See `docs/setup.md` for full setup, including LongCat-Video, and `docs/cloud-gpu.md` for running everything on a rented GPU.

## Ethics

Read `docs/ethics.md` before publishing. In short: use only presenter faces and voices you have consent for, label AI-generated content, have a native Hausa speaker review all text, and check every fact against a named source.

## Licence

Code: MIT. LongCat-Image is Apache 2.0; LongCat-Video weights are MIT.
