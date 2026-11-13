# Change review: saving versus no skill

**Result: 31% to 88%** (minimum to maximum over 3 cases, net of the skill's own cost).

**Target (expected, not a result):** 50% to 93%. Basis: earlier sample: a case file about 93% smaller than the diff of three commits.

## What was compared

- **Without the skill:** Claude reads the full diff of the change.
- **With the skill:** Claude reads a case file: files, symbols touched, who uses them, what to look at first and warnings.

## Inputs

Changes touching 3, 20 and 60 files of a synthetic project, every file modified.

## Cases

| Case | Without the skill (tokens) | With the skill (tokens) | Saving |
|---|---:|---:|---:|
| 3 files changed | 832 | 568 | 31% |
| 20 files changed | 5,614 | 1,030 | 81% |
| 60 files changed | 17,001 | 1,932 | 88% |

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
- The case file tells where to look; reviewing the flagged files still costs tokens. That reading is not counted on either side.
