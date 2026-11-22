"""Turn a Montreal Forced Aligner TextGrid into captions (.srt) and word timings (.json).

MFA writes words in lower case without punctuation. Pass --script with the text
that was read, and the captions get the script's own spelling, capitals and
punctuation back, with each word keeping MFA's timing.

Modes:
    lines  captions of a few words, broken at sentence ends and commas (default)
    words  one caption per word, for word-by-word reels

No dependencies beyond the Python standard library.

Usage:
    python scripts/textgrid_to_srt.py aligned/voiceover.TextGrid --script corpus/voiceover.txt -o captions.srt
    python scripts/textgrid_to_srt.py aligned/voiceover.TextGrid --script corpus/voiceover.txt --mode words -o words.srt --json words.json
"""
import argparse
import difflib
import json
import re
import sys
from pathlib import Path

SILENCE = {"", "<eps>", "sil", "sp", "spn"}
SENTENCE_END = (".", "?", "!", "…")
SHORT_WORD = 0.05  # seconds; shorter than this usually means a skipped or squeezed word


def read_words(path: Path) -> list[dict]:
    """Read the word tier of a long-format TextGrid (MFA's default output)."""
    text = path.read_text(encoding="utf-8-sig")
    if 'class = "IntervalTier"' not in text:
        raise SystemExit(f"{path}: not a long-format TextGrid. Run mfa align with --output_format long_textgrid.")
    tiers = re.split(r"\n\s*item \[\d+\]:", text)[1:]
    for tier in tiers:
        name = re.search(r'name = "(.*)"', tier)
        if name and name.group(1).strip().lower().endswith("words"):
            words = []
            for xmin, xmax, label in re.findall(
                r'xmin = ([\d.]+)\s*\n\s*xmax = ([\d.]+)\s*\n\s*text = "((?:[^"]|"")*)"', tier
            ):
                label = label.replace('""', '"').strip()
                if label.lower() not in SILENCE:
                    words.append({"word": label, "start": float(xmin), "end": float(xmax)})
            return words
    raise SystemExit(f"{path}: no 'words' tier found.")


def norm(token: str) -> str:
    token = token.lower().replace("ʼ", "'").replace("’", "'")
    return re.sub(r"[^\w']", "", token).strip("'")


def script_tokens(script: str) -> list[str]:
    """Split the script into display tokens; punctuation on its own joins the word before it."""
    tokens = []
    for raw in script.split():
        if tokens and not norm(raw):
            tokens[-1] += " " + raw if raw in ("–", "—", "-") else raw
        else:
            tokens.append(raw)
    return tokens


def attach_script(words: list[dict], script: str) -> tuple[list[dict], list[str]]:
    """Give each script token the timing of its matching aligned word."""
    tokens = script_tokens(script)
    matcher = difflib.SequenceMatcher(None, [norm(w["word"]) for w in words], [norm(t) for t in tokens], autojunk=False)
    timed: list[dict | None] = [None] * len(tokens)
    for block in matcher.get_matching_blocks():
        for k in range(block.size):
            w = words[block.a + k]
            timed[block.b + k] = {"word": tokens[block.b + k], "start": w["start"], "end": w["end"]}

    missing = [tokens[i] for i, t in enumerate(timed) if t is None]
    # Spread unmatched tokens evenly across the gap between their matched neighbours.
    i = 0
    while i < len(tokens):
        if timed[i] is not None:
            i += 1
            continue
        j = i
        while j < len(tokens) and timed[j] is None:
            j += 1
        start = timed[i - 1]["end"] if i > 0 else (words[0]["start"] if words else 0.0)
        end = timed[j]["start"] if j < len(tokens) else (words[-1]["end"] if words else start + 0.5 * (j - i))
        step = max(end - start, 0.0) / (j - i)
        for k in range(i, j):
            timed[k] = {"word": tokens[k], "start": start + step * (k - i), "end": start + step * (k - i + 1), "guessed": True}
        i = j
    return timed, missing  # type: ignore[return-value]


def group_lines(words: list[dict], max_words: int, max_chars: int) -> list[list[dict]]:
    lines, current = [], []
    for w in words:
        if current:
            text = " ".join(x["word"] for x in current + [w])
            if len(current) >= max_words or len(text) > max_chars:
                lines.append(current)
                current = []
        current.append(w)
        last = w["word"].rstrip("\"'”’)")
        if last.endswith(SENTENCE_END) or (last.endswith((",", ";", ":")) and len(current) >= 3):
            lines.append(current)
            current = []
    if current:
        lines.append(current)
    return lines


def stamp(seconds: float) -> str:
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def to_srt(cues: list[tuple[float, float, str]]) -> str:
    return "\n".join(f"{n}\n{stamp(a)} --> {stamp(b)}\n{text}\n" for n, (a, b, text) in enumerate(cues, 1))


def make_cues(groups: list[list[dict]], hold: float) -> list[tuple[float, float, str]]:
    """One cue per group; each stays up to `hold` seconds after its last word, but never overlaps the next."""
    cues = []
    for n, group in enumerate(groups):
        start, end = group[0]["start"], group[-1]["end"] + hold
        if n + 1 < len(groups):
            end = min(end, groups[n + 1][0]["start"])
        cues.append((start, max(end, group[-1]["end"]), " ".join(w["word"] for w in group)))
    return cues


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("textgrid", type=Path)
    parser.add_argument("--script", type=Path, help="Text file with the script exactly as read (restores spelling and punctuation)")
    parser.add_argument("--mode", choices=("lines", "words"), default="lines")
    parser.add_argument("--max-words", type=int, default=6, help="Most words per caption in lines mode (default 6)")
    parser.add_argument("--max-chars", type=int, default=32, help="Most characters per caption in lines mode (default 32)")
    parser.add_argument("--hold", type=float, default=0.4, help="Seconds a caption stays after its last word (default 0.4)")
    parser.add_argument("-o", "--output", type=Path, help="Output .srt (default: next to the TextGrid)")
    parser.add_argument("--json", type=Path, help="Also write word timings as JSON (for hyperframes or Concat)")
    args = parser.parse_args()

    words = read_words(args.textgrid)
    if not words:
        raise SystemExit("No words in the alignment: check that the audio and script match.")

    missing: list[str] = []
    if args.script:
        words, missing = attach_script(words, args.script.read_text(encoding="utf-8"))

    groups = [[w] for w in words] if args.mode == "words" else group_lines(words, args.max_words, args.max_chars)
    hold = min(args.hold, 0.15) if args.mode == "words" else args.hold
    out = args.output or args.textgrid.with_suffix(f".{args.mode}.srt")
    out.write_text(to_srt(make_cues(groups, hold)), encoding="utf-8")
    print(f"Captions: {out} ({len(groups)} cues)")

    if args.json:
        rows = [{"word": w["word"], "start": round(w["start"], 3), "end": round(w["end"], 3)} | ({"guessed": True} if w.get("guessed") else {}) for w in words]
        args.json.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Word timings: {args.json}")

    # Voiceover check: words MFA could not place, or squeezed into almost no time.
    short = [w["word"] for w in words if not w.get("guessed") and w["end"] - w["start"] < SHORT_WORD]
    if missing:
        print(f"Check: {len(missing)} script word(s) not found in the audio (timing guessed): {' '.join(missing)}", file=sys.stderr)
    if short:
        print(f"Check: {len(short)} word(s) shorter than {int(SHORT_WORD * 1000)} ms, possibly skipped or rushed: {' '.join(short)}", file=sys.stderr)
    if not missing and not short:
        print("Check: every script word was found in the audio.")


if __name__ == "__main__":
    main()
