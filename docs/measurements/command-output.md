# Command output: saving versus no skill

**Result: −35% to 99%** (minimum to maximum over 10 cases, net of the skill's own cost).

**Target (expected, not a result):** 50% to 99%. Basis: earlier small samples: filtered log 93%, test summary about 99% (578 tokens against about 44,600).

## What was compared

- **Without the skill:** Claude reads the whole output of a log or of a test or build run.
- **With the skill:** Logs are filtered to warnings and errors with context; test and build runs are summarized to the failing lines and the closing summary.

## Inputs

Logs of 54 to 10,004 lines with one error and its stack trace; passing and failing test runs of 100, 1,000 and 5,000 lines.

## Cases

| Case | Input fingerprint | Without the skill (tokens) | With the skill (tokens) | Saving |
|---|---|---:|---:|---:|
| log, 54 lines | efc1900284 | 685 | 500 | 27% |
| log, 504 lines | efc3abd9fc | 6,623 | 502 | 92% |
| log, 2,004 lines | e93ae84f5b | 26,705 | 503 | 98% |
| log, 10,004 lines | 5afd20164c | 134,483 | 504 | 99% |
| passing test run, 100 lines | 3c57bed91d | 379 | 508 | −35% |
| failing test run, 100 lines | c415c367cb | 396 | 518 | −31% |
| passing test run, 1,000 lines | 8601664822 | 3,979 | 513 | 87% |
| failing test run, 1,000 lines | f6b2164f10 | 3,996 | 522 | 86% |
| passing test run, 5,000 lines | 23700fdc94 | 20,979 | 516 | 97% |
| failing test run, 5,000 lines | 0bf8e1a79b | 20,996 | 525 | 97% |

## Evidence

| Field | Value |
|---|---|
| Basis of the result | benchmark counterfactual: the same inputs read without and with the skill |
| Basis of the token counts | inferred: characters divided by 4 for text, pixels divided by 750 for images; not a provider count |
| Inputs | listed above, each with a fingerprint (first 10 characters of the SHA-256 of the exact input) |
| Code revision | 1b8d334 |
| Quality check | not run: task success was not tested; 0 of 0 tasks checked |
| Failures and excluded cases | none excluded; all 10 cases are listed, losses included |
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
- A cause far from the error line can be filtered out: the tool says how to read the original by line range. That risk was tested with one planted case only.
