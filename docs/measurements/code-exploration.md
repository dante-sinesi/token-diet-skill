# Code exploration: saving versus no skill

**Result: −91% to 98%** (minimum to maximum over 9 cases, net of the skill's own cost).

**Target (expected, not a result):** 50% to 95%. Basis: target: a summary of a few dozen lines instead of reading the files.

## What was compared

- **Without the skill:** Claude reads the files to get oriented, to find who uses a symbol and to spot repeated code.
- **With the skill:** Claude reads a short inventory of the project, a list of where a symbol is defined and used, and a list of repeated blocks.

## Inputs

Synthetic Python projects of 6, 40 and 200 files; for the symbol lookup, the baseline is only the files that mention it.

## Cases

| Case | Input fingerprint | Without the skill (tokens) | With the skill (tokens) | Saving |
|---|---|---:|---:|---:|
| 6 files: inventory | b258c1200f | 1,096 | 525 | 52% |
| 6 files: uses of one symbol | b258c1200f | 294 | 557 | −90% |
| 6 files: repeated blocks | b258c1200f | 1,096 | 464 | 57% |
| 40 files: inventory | 10eac731f1 | 7,109 | 530 | 92% |
| 40 files: uses of one symbol | 10eac731f1 | 294 | 558 | −90% |
| 40 files: repeated blocks | 10eac731f1 | 7,109 | 506 | 92% |
| 200 files: inventory | 7275521eb8 | 36,249 | 532 | 98% |
| 200 files: uses of one symbol | 7275521eb8 | 294 | 559 | −91% |
| 200 files: repeated blocks | 7275521eb8 | 36,249 | 722 | 98% |

## Evidence

| Field | Value |
|---|---|
| Basis of the result | benchmark counterfactual: the same inputs read without and with the skill |
| Basis of the token counts | inferred: characters divided by 4 for text, pixels divided by 750 for images; not a provider count |
| Inputs | listed above, each with a fingerprint (first 10 characters of the SHA-256 of the exact input) |
| Code revision | b5b01c3 |
| Quality check | not run: task success was not tested; 0 of 0 tasks checked |
| Failures and excluded cases | none excluded; all 9 cases are listed, losses included |
| Price | not applicable: no money figure is claimed (unpriced) |
| Scope | only these inputs and this counter; it does not extend to other models, providers, tasks or dates |

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
- The inventory and the lists point to places; Claude may still need to open some files afterwards. That follow-up reading is not counted on either side.
