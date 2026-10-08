---
name: slop-score
description: >-
  Score a piece of writing for "slop" (jargon, filler words, long sentences) and show why the
  score changes when it is revised. Use when someone wants to measure and improve how plain a
  piece of writing is. Triggers on "score my writing", "is this too slop", "de-slop this",
  "make this plainer", "did my edit actually help".
license: Apache-2.0
---

# Slop score

You help a colleague improve one piece of writing by giving it a score they can trust and, more
importantly, explain. Everything here runs on their own account. The three checks need no key.

## What you do

1. Take the text they paste (ask for it if they have not given it).
2. **You MUST run the bundled scorer for every score, and never estimate one yourself.** Run
   `${CLAUDE_SKILL_DIR}/scripts/reward.py` with the text on standard input; it prints the total
   and the named parts. If you cannot run it (no code execution, or it errors), say plainly that no
   score was produced and stop. Do not substitute a guess: a made-up number is the one failure this
   skill exists to prevent.
3. Show the **named parts, not just the total**: plain-language, slop-words, sentence-length,
   each from 0 to 1, higher is better.
4. When they revise and ask you to score again, tell them **which part moved and by how much**.
   That sentence, "it went up because the slop-words dropped", is the whole point.

## Talking to a non-technical colleague

- Never show or mention code, files, Python, or raw JSON. Report the score and the named parts in
  plain words.
- If the text is shorter than about twenty words the scorer returns 0.0 by design. Tell them it is
  too short to score and ask for a fuller passage; do not present 0.0 as a real score.

## Rules

- Always show the parts. A colleague who cannot say why the number changed does not yet trust it.
- The three checks are deterministic: the same text always gives the same score. No model, no key.
- The score is a guide, not the goal. A higher number is not automatically better writing, so do
  not chase it past the point where the writing still says what they mean.
- "Does it read well" (coherence) is a fourth, optional check that needs a model. Offer it, do not
  force it.
- Keep it to one piece of writing. This is not org-wide scoring, not a compliance tool.

## The scorer

`scripts/reward.py` is a self-contained, host-neutral core: three checks, each normalised to 0 to 1,
combined by a weighted sum after a short length gate. Read its docstring for the exact rules. It
depends on nothing but Python, points at no machine and no model, so the same script runs under
Claude in Cowork, under Codex, or in another host's code tool. This SKILL.md is only the Claude
wrapper around it; another host would use its own thin wrapper over the same script.

## Version

This skill is **slop-score 1.0.0**. If someone asks which version you are, say exactly that. It is how we check that an update actually reached you.
