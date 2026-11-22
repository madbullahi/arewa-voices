#!/usr/bin/env bash
# Time a campaign's script against its voiceover with the Montreal Forced Aligner,
# then write captions and word timings.
#
# Usage:
#   bash scripts/align.sh campaigns/health-nutrition            # Hausa, audio/voiceover.wav
#   bash scripts/align.sh campaigns/health-nutrition en         # English
#   bash scripts/align.sh campaigns/health-nutrition ha take2.m4a
#
# Needs MFA in a conda environment (see docs/captions.md): conda activate mfa
# Writes to campaigns/<issue>/output/:
#   captions_<lang>.srt        a few words per caption
#   captions_<lang>_words.srt  one word per caption
#   words_<lang>.json          word timings
set -euo pipefail

campaign="${1:?Usage: bash scripts/align.sh <campaign-dir> [ha|en] [audio-file]}"
lang="${2:-ha}"
audio="${3:-$campaign/audio/voiceover.wav}"
here="$(cd "$(dirname "$0")" && pwd)"

case "$lang" in
  ha) model=hausa_mfa ;;
  en) model=english_mfa ;;
  *) echo "Language must be ha or en, not '$lang'." >&2; exit 1 ;;
esac

command -v mfa >/dev/null || { echo "MFA not found. Run: conda activate mfa (install steps in docs/captions.md)" >&2; exit 1; }
[ -f "$campaign/script.json" ] || { echo "No script.json in $campaign" >&2; exit 1; }
[ -f "$audio" ] || { echo "No audio at $audio (record one, or run make_voiceover.py first)" >&2; exit 1; }

work="$campaign/output/align/$lang"
corpus="$work/corpus"
aligned="$work/aligned"
rm -rf "$corpus" "$aligned"
mkdir -p "$corpus" "$aligned"

# The script text, exactly as read.
python3 - "$campaign/script.json" "$lang" > "$corpus/voiceover.txt" <<'EOF'
import json, sys
text = json.load(open(sys.argv[1], encoding="utf-8"))["video"][f"script_{sys.argv[2]}"]
if text.startswith("TODO"):
    sys.exit(f"script_{sys.argv[2]} is not written yet in script.json.")
print(text)
EOF

# MFA wants a WAV; convert phone recordings (m4a, mp3, ...) to 16 kHz mono.
if [[ "${audio,,}" == *.wav ]]; then
  cp "$audio" "$corpus/voiceover.wav"
else
  command -v ffmpeg >/dev/null || { echo "ffmpeg is needed to convert $audio to WAV." >&2; exit 1; }
  ffmpeg -y -loglevel error -i "$audio" -ac 1 -ar 16000 "$corpus/voiceover.wav"
fi

# Download the models once.
for kind in acoustic dictionary; do
  mfa model inspect "$kind" "$model" >/dev/null 2>&1 || mfa model download "$kind" "$model"
done

# Report words missing from the pronunciation dictionary (alignment still runs).
if [ "${SKIP_VALIDATE:-0}" != 1 ]; then
  mfa validate --clean "$corpus" "$model" --acoustic_model_path "$model" || true
fi

mfa align --clean "$corpus" "$model" "$model" "$aligned"

grid="$aligned/voiceover.TextGrid"
out="$campaign/output"
python3 "$here/textgrid_to_srt.py" "$grid" --script "$corpus/voiceover.txt" \
  -o "$out/captions_${lang}.srt" --json "$out/words_${lang}.json"
python3 "$here/textgrid_to_srt.py" "$grid" --script "$corpus/voiceover.txt" \
  --mode words -o "$out/captions_${lang}_words.srt" 2>/dev/null
