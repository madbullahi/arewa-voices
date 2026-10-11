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

Record the Hausa voiceover with a consenting human speaker (preferred), or use a TTS tool that supports Hausa. Save it as `campaigns/<issue>/audio/voiceover.wav`.
