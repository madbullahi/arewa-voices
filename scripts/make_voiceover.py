"""Make a draft voiceover and the LongCat-Video-Avatar input file for a campaign.

Uses Meta's MMS text-to-speech models (facebook/mms-tts-hau for Hausa,
facebook/mms-tts-eng for English). These are licensed CC-BY-NC 4.0, i.e.
non-commercial only. For anything commercial or sponsored, record a consenting
human speaker instead and use --audio to skip text-to-speech.

Usage:
    python scripts/make_voiceover.py --campaign campaigns/out-of-school-children --lang en
    python scripts/make_voiceover.py --campaign campaigns/out-of-school-children --audio my_recording.wav
"""
import argparse
import json
import shutil
from pathlib import Path

MODELS = {"ha": "facebook/mms-tts-hau", "en": "facebook/mms-tts-eng"}


def synthesise(text: str, lang: str, out_path: Path) -> None:
    import numpy as np
    import scipy.io.wavfile
    import torch
    from transformers import AutoTokenizer, VitsModel

    model = VitsModel.from_pretrained(MODELS[lang])
    tokenizer = AutoTokenizer.from_pretrained(MODELS[lang])
    torch.manual_seed(0)  # reproducible output

    # Synthesise sentence by sentence: MMS is more stable on short inputs.
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    pause = np.zeros(int(model.config.sampling_rate * 0.3), dtype=np.float32)
    chunks = []
    for sentence in sentences:
        inputs = tokenizer(sentence + ".", return_tensors="pt")
        with torch.no_grad():
            wave = model(**inputs).waveform[0].numpy()
        chunks += [wave, pause]
    scipy.io.wavfile.write(out_path, rate=model.config.sampling_rate, data=np.concatenate(chunks))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--campaign", required=True)
    parser.add_argument("--lang", choices=MODELS, default="ha")
    parser.add_argument("--audio", help="Use this recorded audio file instead of text-to-speech")
    parser.add_argument("--presenter", default="presenter", help="Image name (from script.json) to animate")
    args = parser.parse_args()

    campaign = Path(args.campaign).resolve()
    script = json.loads((campaign / "script.json").read_text(encoding="utf-8"))
    audio_dir = campaign / "audio"
    audio_dir.mkdir(exist_ok=True)
    voiceover = audio_dir / "voiceover.wav"

    if args.audio:
        shutil.copyfile(args.audio, voiceover)
    else:
        text = script["video"][f"script_{args.lang}"]
        if text.startswith("TODO"):
            raise SystemExit(f"script_{args.lang} is not written yet. Add it to script.json (Hausa must be reviewed by a native speaker).")
        synthesise(text, args.lang, voiceover)
    print(f"Voiceover: {voiceover}")

    presenter = campaign / "output" / "images" / f"{args.presenter}.png"
    if not presenter.exists():
        print(f"Warning: {presenter} not found. Run generate_image.py first.")

    avatar_input = {
        "prompt": script["video"]["presenter_prompt"],
        "cond_image": str(presenter),
        "cond_audio": {"person1": str(voiceover)},
    }
    out = campaign / "avatar_input.json"
    out.write_text(json.dumps(avatar_input, indent=2), encoding="utf-8")
    print(f"Avatar input: {out}")


if __name__ == "__main__":
    main()
