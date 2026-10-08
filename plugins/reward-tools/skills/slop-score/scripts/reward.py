"""Self-contained slop scorer for the slop-score Cowork skill.

Three offline checks, no key, no network, deterministic. Each sub-score is in [0, 1], higher is
better, combined by a weighted sum after a length gate. This file is bundled with the skill so it
runs the same on any account, with nothing pointing back at the author's machine.

    echo "your text" | python3 reward.py     score the text, print total + named parts as JSON
    python3 reward.py                         run the built-in smoke test over the sample drafts
"""
from __future__ import annotations

import json
import re
import sys

# A short, illustrative filler list. A full run builds this with the user; this is enough to score.
SLOP_WORDS = {
    "delve", "crucial", "leverage", "robust", "seamless", "seamlessly", "synergy", "synergies",
    "transformative", "empower", "unlock", "unprecedented", "ecosystem", "myriad", "landscape",
    "utilise", "ultimately", "holistic", "paradigm", "best-in-class", "cutting-edge",
    "game-changing", "in order to", "going forward",
}
WEIGHTS = {"plain_language": 0.5, "slop_words": 0.3, "sentence_length": 0.2}
MIN_WORDS = 20  # the gate: too short to judge


def _words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z'-]*", text)


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"[.!?]+", text) if s.strip()]


def _slop_hits(low_text: str) -> int:
    """Count filler terms as whole words, so 'seamless' does not fire inside 'seamlessly'."""
    return sum(len(re.findall(r"\b" + re.escape(term) + r"\b", low_text)) for term in SLOP_WORDS)


def parts(text: str) -> dict[str, float]:
    """The three named sub-scores, each normalised to [0, 1], higher is better."""
    words = _words(text)
    n = max(len(words), 1)
    slop_hits = _slop_hits(text.lower())
    long_words = sum(1 for w in words if len(w) > 12)
    sents = _sentences(text)
    short_enough = sum(1 for s in sents if len(_words(s)) <= 20) / max(len(sents), 1)
    # plain_language is a proxy: the share of very long words, not a grammar check.
    return {
        "plain_language": 1 - min(long_words / n * 100 / 8, 1),
        "slop_words": 1 - min(slop_hits / n * 100 / 5, 1),
        "sentence_length": short_enough,
    }


def score(text: str) -> float:
    """Gated, weighted slop score in [0, 1]. Text under the word gate scores 0.0.

    Deterministic: the same text always yields the same score, so a caller may cache by content
    hash. We do not cache here, to avoid a stale result if the filler list or weights change.
    """
    if len(_words(text)) < MIN_WORDS:
        return 0.0
    p = parts(text)
    return round(sum(WEIGHTS[k] * p[k] for k in WEIGHTS), 4)


_DRAFTS = {
    "v0_first_draft": (
        "Our team has worked hard this quarter, and we are excited to leverage a robust set of "
        "tools to ultimately deliver a seamless experience for our stakeholders. The onboarding "
        "flow, which had previously been a source of considerable friction for many of the new "
        "users who joined us during the busy period, was completely rewritten from the ground up. "
        "Early numbers look good."
    ),
    "v1_slop_removed": (
        "Our team has worked hard this quarter, and we are glad to use a solid set of tools to "
        "deliver a smooth experience for our partners. The onboarding flow, which had previously "
        "been a source of considerable friction for many of the new users who joined us during the "
        "busy period, was completely rewritten from the ground up. Early numbers look good."
    ),
    "v2_sentences_split": (
        "Our team worked hard this quarter. We used a solid set of tools to give partners a "
        "smoother experience. We rewrote the onboarding flow. It used to frustrate new users "
        "during busy periods. Early numbers look good."
    ),
}


def _smoke() -> None:
    rows = [(name, score(text), parts(text)) for name, text in _DRAFTS.items()]
    print(f"{'draft':22} {'total':>6}  plain  slop  length")
    for name, total, p in rows:
        print(f"{name:22} {total:6.2f}  {p['plain_language']:4.2f}  {p['slop_words']:4.2f}  "
              f"{p['sentence_length']:4.2f}")
    totals = [total for _, total, _ in rows]
    if not (totals == sorted(totals) and len(set(totals)) == len(totals)):
        raise SystemExit(f"drafts do not rank v0 < v1 < v2: {totals}")
    print("OK: v0 < v1 < v2, each revision scores strictly higher")


if __name__ == "__main__":
    piped = "" if sys.stdin.isatty() else sys.stdin.read()
    if piped.strip():
        print(json.dumps(
            {"score": score(piped), "parts": {k: round(v, 2) for k, v in parts(piped).items()}},
            indent=2))
    else:
        _smoke()
