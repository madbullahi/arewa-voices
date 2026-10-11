#!/usr/bin/env bash
# Generate a talking-presenter video with LongCat-Video-Avatar 1.5.
# Usage: bash scripts/generate_avatar_video.sh campaigns/out-of-school-children
# Expects: <campaign>/audio/voiceover.wav and <campaign>/avatar_input.json,
# both made by scripts/make_voiceover.py.
# Env vars: GPUS (default 2), STAGE (ai2v = animate the presenter image, default;
# at2v = generate the presenter from the text prompt), SEGMENTS (default 1;
# more segments continue the video for longer voiceovers).
set -euo pipefail

CAMPAIGN="$(realpath "${1:?campaign folder required}")"
LONGCAT_DIR="${LONGCAT_DIR:-external/LongCat-Video}"
GPUS="${GPUS:-2}"
STAGE="${STAGE:-ai2v}"
SEGMENTS="${SEGMENTS:-1}"

[ -f "$CAMPAIGN/audio/voiceover.wav" ] || { echo "Missing $CAMPAIGN/audio/voiceover.wav"; exit 1; }
[ -f "$CAMPAIGN/avatar_input.json" ] || { echo "Missing $CAMPAIGN/avatar_input.json"; exit 1; }

cd "$LONGCAT_DIR"
torchrun --nproc_per_node="$GPUS" run_demo_avatar_single_audio_to_video.py \
  --context_parallel_size="$GPUS" \
  --checkpoint_dir=./weights/LongCat-Video-Avatar-1.5 \
  --stage_1="$STAGE" \
  --input_json="$CAMPAIGN/avatar_input.json" \
  --num_segments="$SEGMENTS" \
  --model_type avatar-v1.5 \
  --use_distill \
  --use_int8
