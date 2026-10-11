# Running on a rented cloud GPU

This guide takes one campaign from script to finished video on a rented GPU, then shuts the machine down so you stop paying.

## 1. Choose a machine

| Job | GPU | Disk |
| --- | --- | --- |
| Images only (LongCat-Image) | 1 × 24 GB GPU (RTX 4090, L4, A10) | 60 GB |
| Images + avatar video | 2 × 80 GB GPU (A100 or H100) | 200 GB |

Providers that rent by the hour include RunPod, Lambda, Vast.ai and the big clouds (AWS, Google Cloud, Azure). Prices change often, so compare them on the day. Pick an image with **Ubuntu 22.04, CUDA 12.4 and PyTorch** preinstalled to save setup time.

Tip: do all script writing, translation review and voiceover recording **before** you start the machine. GPU time should only be generation.

## 2. Connect and get the code

```bash
ssh <user>@<machine-address>
git clone https://github.com/madbullahi/arewa-voices
cd arewa-voices
```

## 3. Install

```bash
conda create -n arewa python=3.10 -y
conda activate arewa
pip install -r requirements.txt
```

For video, also follow section 2 of [setup.md](setup.md) to install LongCat-Video into `external/LongCat-Video` and download the Avatar 1.5 weights. Model downloads are tens of gigabytes; start them first.

Check the GPUs are visible:

```bash
nvidia-smi
python -c "import torch; print(torch.cuda.device_count(), 'GPUs')"
```

## 4. Upload your voiceover

From your own computer:

```bash
scp recording.wav <user>@<machine-address>:~/arewa-voices/
```

## 5. Generate

```bash
CAMPAIGN=campaigns/out-of-school-children

python scripts/generate_image.py --campaign $CAMPAIGN --high-vram
python scripts/make_voiceover.py --campaign $CAMPAIGN --audio recording.wav
bash scripts/generate_avatar_video.sh $CAMPAIGN
```

For a single GPU, run the video step with `GPUS=1`. It is slower and may run out of memory on cards under 80 GB.

Use `tmux` so a dropped connection doesn't kill a long run:

```bash
tmux new -s gen      # start a session; detach with Ctrl+B then D
tmux attach -t gen   # reconnect later
```

## 6. Download the results

From your own computer:

```bash
scp -r <user>@<machine-address>:~/arewa-voices/campaigns/out-of-school-children/output ./output
```

The video is written inside `external/LongCat-Video` (check its output folder); copy it into the campaign's `output/` folder before downloading.

## 7. Shut down

**Stop or delete the machine as soon as downloads finish.** Most providers keep billing a stopped machine for its disk; delete it if you don't need the downloaded models again soon.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `CUDA out of memory` on images | Drop `--high-vram` to use CPU offload |
| `CUDA out of memory` on video | Use 2 GPUs, keep `--use_int8`, or switch to 480p (`--resolution`) in the LongCat-Video command |
| `flash_attn` fails to install | Make sure the CUDA toolkit matches PyTorch (cu124); install `ninja` first |
| Lip sync is off | Raise the audio CFG to 4–5 (see LongCat-Video README tips) |
| Presenter repeats the same gestures | Set `--ref_img_index` to 30 (LongCat-Video README tips) |
