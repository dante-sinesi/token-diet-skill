# Code exploration: saving versus no skill

**Result: −172% to 97%** (minimum to maximum over 9 cases, net of the skill's own cost).

**Target (expected, not a result):** 50% to 95%. Basis: target: a summary of a few dozen lines instead of reading the files.

## What was compared

- **Without the skill:** Claude reads the files to get oriented, to find who uses a symbol and to spot repeated code.
- **With the skill:** Claude reads a short inventory of the project, a list of where a symbol is defined and used, and a list of repeated blocks.

## Inputs

Synthetic Python projects of 6, 40 and 200 files; for the symbol lookup, the baseline is only the files that mention it.

## Cases

| Case | Without the skill (tokens) | With the skill (tokens) | Saving |
|---|---:|---:|---:|
| 6 files: inventory | 1,096 | 763 | 30% |
| 6 files: uses of one symbol | 294 | 795 | −171% |
| 6 files: repeated blocks | 1,096 | 702 | 35% |
| 40 files: inventory | 7,109 | 768 | 89% |
| 40 files: uses of one symbol | 294 | 796 | −171% |
| 40 files: repeated blocks | 7,109 | 744 | 89% |
| 200 files: inventory | 36,249 | 770 | 97% |
| 200 files: uses of one symbol | 294 | 797 | −172% |
| 200 files: repeated blocks | 36,249 | 960 | 97% |

## Why this measurement can be trusted

- **Both sides come from real files and real tool output.** The "without the skill" figure is the size of the input Claude would read; the "with the skill" figure is the size of what the tool printed for that same input. Nothing is modeled except the token estimate itself.
- **The skill's own cost is charged in full, in every case.** Each case adds the skill description (79 tokens), the body of `SKILL.md` (576 tokens), the command that was run and, when the read hook intervenes, its block message. In a real session the description and the body are paid once, so real savings are higher than these.
- **The "no skill" side uses no resource of the skill at all.** It is a plain read, with no conversion, no summary and no index.
- **Every case is listed, including the ones where the skill loses.** The range is the minimum and the maximum of all the cases, rounded down.
- **The inputs are fixed and described**, so the numbers do not depend on a model's sampling and can be recomputed.

## Limits

- Tokens are estimated (characters divided by 4 for text, pixels divided by 750 for images), not counted with Anthropic's tokenizer, so each figure carries roughly a 30% margin. They are good for comparing, not for billing.
- Task success was not measured with agents. A mechanic that lowered success would not be accepted; this report only covers the tokens.
- The inputs are samples, partly synthetic. Real projects will differ.
- The inventory and the lists point to places; Claude may still need to open some files afterwards. That follow-up reading is not counted on either side.
