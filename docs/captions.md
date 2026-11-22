# Captions from the script (forced alignment)

Every topic already has its script, so captions don't need speech recognition. The [Montreal Forced Aligner](https://montreal-forced-aligner.readthedocs.io/) (MFA) takes the voiceover and the script and works out when each word is spoken. `scripts/align.sh` turns that into:

| File (in `topics/<topic>/output/`) | Use |
| --- | --- |
| `captions_<lang>.srt` | Captions of a few words each, broken at sentence ends and commas: upload with the video, or import into Concat |
| `captions_<lang>_words.srt` | One word per caption, for word-by-word reels |
| `words_<lang>.json` | Word timings, for placing graphics on a word (hyperframes `reel.json`, Concat through Claude Code) |

It also checks the voiceover: words from the script that MFA couldn't find in the audio, or that were squeezed into almost no time, are listed at the end. That usually means the speaker skipped, changed or rushed a word.

Models: `hausa_mfa` and `english_mfa` from MFA's pretrained models. The Hausa model and dictionary are by Michael McAuliffe, CC-BY-4.0, so commercial use is allowed (unlike the MMS voices in `make_voiceover.py`). Everything runs on a laptop CPU; no GPU needed.

## Install (once)

MFA comes from conda-forge (it bundles Kaldi), not pip. If you have no conda, install [Miniforge](https://github.com/conda-forge/miniforge) first.

```bash
conda create -n mfa -c conda-forge montreal-forced-aligner -y
conda activate mfa
mfa model download acoustic hausa_mfa
mfa model download dictionary hausa_mfa
mfa model download acoustic english_mfa
mfa model download dictionary english_mfa
```

`align.sh` downloads any model that's missing, so the last four lines are optional.

## Run

```bash
conda activate mfa
bash scripts/align.sh topics/daphnia            # Hausa, uses audio/voiceover.wav
bash scripts/align.sh topics/daphnia en         # English
bash scripts/align.sh topics/daphnia ha take2.m4a   # a phone recording; converted with ffmpeg
```

The text comes from `script_ha` or `script_en` in `script.json`, so the script there must match what was read, word for word. Fix the script or re-record before aligning.

Options for the converter (run it on its own to re-cut captions without re-aligning):

```bash
python scripts/textgrid_to_srt.py topics/<topic>/output/align/ha/aligned/voiceover.TextGrid \
  --script topics/<topic>/output/align/ha/corpus/voiceover.txt \
  --max-words 4 --max-chars 24 -o captions_short.srt
```

`--max-words` (default 6) and `--max-chars` (default 32) set the caption length; `--hold` (default 0.4 s) is how long a caption stays after its last word.

## When a word isn't in the dictionary

`mfa validate` (run by `align.sh` first; skip with `SKIP_VALIDATE=1`) lists out-of-vocabulary words: usually names, places, loanwords and health terms. Alignment still runs, but those words get poor timing. Two fixes:

1. Generate pronunciations with the Hausa G2P model, check them, and add them to a custom dictionary:
   ```bash
   mfa model download g2p hausa_mfa
   mfa g2p oovs.txt hausa_mfa science_words.dict
   ```
2. Keep `science_words.dict` growing across topics, so each new clip aligns better. (Pointing `align.sh` at a merged dictionary is a small change when this is needed.)

## Things to know

- **Write the script the normal way.** Hausa is usually written without tone or vowel-length marks, and the dictionary follows that spelling. Keep the hooked letters (ɓ, ɗ, ƙ, ƴ) and ʼy.
- **Children's voices may align poorly.** The model was trained on adult speakers; test with a child's clip before using it for content voiced by children.
- **One speaker per clip.** For interviews or several speakers, split the audio first.
- **Unscripted audio** (interviews, field recordings) needs transcription first; WhisperX can do that, with a Hausa wav2vec2 model for its timing step.
