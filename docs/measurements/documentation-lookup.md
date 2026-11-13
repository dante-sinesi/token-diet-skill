# Documentation lookup: saving versus no skill

**Result: 61% to 90%** (minimum to maximum over 6 cases, net of the skill's own cost).

**Target (expected, not a result):** 50% to 95%. Basis: earlier sample: a query answers in about 116 tokens and warns that opening the diagram costs about 221.

## What was compared

- **Without the skill:** Claude reads the whole document that contains the answer (it is assumed to already know which one, which favors the no-skill side). To resume a session, it re-reads the project documents.
- **With the skill:** Claude runs a query and reads only the section it points to; to resume, it reads a continuity note.

## Inputs

Documentation sets of 5, 30 and 120 documents with one planted answer; continuity notes of 150, 400 and 800 tokens against re-reading four documents.

## Cases

| Case | Without the skill (tokens) | With the skill (tokens) | Saving |
|---|---:|---:|---:|
| 5 documents: find one answer | 1,784 | 679 | 61% |
| 30 documents: find one answer | 1,787 | 680 | 61% |
| 120 documents: find one answer | 1,787 | 680 | 61% |
| resume from a 150-token note | 6,328 | 575 | 90% |
| resume from a 400-token note | 6,328 | 825 | 86% |
| resume from a 800-token note | 6,328 | 1,225 | 80% |

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
- The continuity note is modeled: its real value depends on how well it is written in real sessions.
