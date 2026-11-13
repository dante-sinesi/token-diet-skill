# Lockfiles and generated files: saving versus no skill

**Result: 81% to 99%** (minimum to maximum over 3 cases, net of the skill's own cost).

**Target (expected, not a result):** 90% to 99%. Basis: target: a summary of a few dozen packages instead of tens of thousands of tokens.

## What was compared

- **Without the skill:** Claude reads the lockfile as it is.
- **With the skill:** Claude reads a summary: package count and the first packages. The read hook blocks the direct read and points to the summary.

## Inputs

Synthetic package-lock.json files with 50, 400 and 3,000 packages.

## Cases

| Case | Without the skill (tokens) | With the skill (tokens) | Saving |
|---|---:|---:|---:|
| package-lock.json, 50 packages | 3,426 | 639 | 81% |
| package-lock.json, 400 packages | 27,376 | 639 | 97% |
| package-lock.json, 3,000 packages | 206,476 | 639 | 99% |

## Why this measurement can be trusted

- **Both sides come from real files and real tool output.** The "without the skill" figure is the size of the input Claude would read; the "with the skill" figure is the size of what the tool printed for that same input. Nothing is modeled except the token estimate itself.
- **The skill's own cost is charged in full, in every case.** Each case adds the skill description (79 tokens), the body of `SKILL.md` (338 tokens), the command that was run and, when the read hook intervenes, its block message. In a real session the description and the body are paid once, so real savings are higher than these.
- **The "no skill" side uses no resource of the skill at all.** It is a plain read, with no conversion, no summary and no index.
- **Every case is listed, including the ones where the skill loses.** The range is the minimum and the maximum of all the cases, rounded down.
- **The inputs are fixed and described**, so the numbers do not depend on a model's sampling and can be recomputed.

## Limits

- Tokens are estimated (characters divided by 4 for text, pixels divided by 750 for images), not counted with Anthropic's tokenizer, so each figure carries roughly a 30% margin. They are good for comparing, not for billing.
- Task success was not measured with agents. A mechanic that lowered success would not be accepted; this report only covers the tokens.
- The inputs are samples, partly synthetic. Real projects will differ.
- Only package-lock.json was measured; the other lockfile formats and source maps share the code path but were not measured separately.
