# Setup

## 1. Images (LongCat-Image)

```bash
conda create -n arewa python=3.10 -y
conda activate arewa
pip install -r requirements.txt
```

The model downloads from Hugging Face on first run (`meituan-longcat/LongCat-Image`).

Text inside an image must be wrapped in quotation marks in the prompt, or LongCat-Image will not render it reliably.

## 2. Video (LongCat-Video-Avatar 1.5)

Run on a cloud GPU machine with CUDA 12.4.

```bash
git clone --single-branch --branch main https://github.com/meituan-longcat/LongCat-Video external/LongCat-Video
cd external/LongCat-Video
pip install torch==2.6.0+cu124 torchvision==0.21.0+cu124 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
pip install ninja psutil packaging flash_attn==2.7.4.post1
pip install -r requirements.txt
conda install -c conda-forge librosa ffmpeg -y
pip install -r requirements_avatar.txt
huggingface-cli download meituan-longcat/LongCat-Video-Avatar-1.5 --local-dir ./weights/LongCat-Video-Avatar-1.5
```

Then from the repo root:

```bash
bash scripts/generate_avatar_video.sh campaigns/out-of-school-children
```

## 3. Voiceover

`scripts/make_voiceover.py` creates `campaigns/<issue>/audio/voiceover.wav` and the `avatar_input.json` that the video step needs.

**Preferred: a human recording.** Record a consenting Hausa speaker, then:

```bash
python scripts/make_voiceover.py --campaign campaigns/out-of-school-children --audio recording.wav
```

**Draft: text-to-speech.** Uses Meta's MMS models (`facebook/mms-tts-hau`, `facebook/mms-tts-eng`). They are licensed CC-BY-NC 4.0, so use them for drafts and non-commercial posts only.

```bash
python scripts/make_voiceover.py --campaign campaigns/out-of-school-children --lang ha
```

The script stops if `script_ha` in `script.json` is still a TODO.

## Full order of steps

1. `python scripts/generate_image.py --campaign <campaign>` (makes the presenter portrait, poster and thumbnail)
2. `python scripts/make_voiceover.py --campaign <campaign> ...`
3. `bash scripts/generate_avatar_video.sh <campaign>`
