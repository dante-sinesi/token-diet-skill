# Plain text, JSON, CSV: saving versus no skill

**Result: −64% to 70%** (minimum to maximum over 8 cases, net of the skill's own cost).

**Target (expected, not a result):** 0% to 77%. Basis: earlier small samples: JSON compaction 51%, tables 77%.

## What was compared

- **Without the skill:** Claude reads the file as it is.
- **With the skill:** Plain text is read as it is (the skill adds only its description). JSON is compacted, or turned into a table when the rows are uniform. A large CSV is read as a schema plus a sample.

## Inputs

Plain text from 0.5 KB to 500 KB; JSON with 30 and 300 uniform rows and a nested configuration of 600 keys; a CSV of 500 rows.

## Cases

| Case | Input fingerprint | Without the skill (tokens) | With the skill (tokens) | Saving |
|---|---|---:|---:|---:|
| plain text, 500 bytes | 8cff711dc2 | 125 | 204 | −64% |
| plain text, 5,000 bytes | c959411832 | 1,250 | 1,329 | −7% |
| plain text, 50,000 bytes | f199c6c2e1 | 12,500 | 12,579 | −1% |
| plain text, 500,000 bytes | 1a0ff0bb20 | 125,000 | 125,079 | −1% |
| JSON, 30 uniform rows | 7cf9674ef7 | 740 | 857 | −16% |
| JSON, 300 uniform rows | c1249e9f6d | 7,606 | 4,010 | 47% |
| JSON, nested configuration | 901b9ec329 | 3,308 | 2,306 | 30% |
| CSV, 500 rows | 7dca42b1cd | 1,981 | 586 | 70% |

## Evidence

| Field | Value |
|---|---|
| Basis of the result | benchmark counterfactual: the same inputs read without and with the skill |
| Basis of the token counts | inferred: characters divided by 4 for text, pixels divided by 750 for images; not a provider count |
| Inputs | listed above, each with a fingerprint (first 10 characters of the SHA-256 of the exact input) |
| Code revision | db204d2 |
| Quality check | not run: task success was not tested; 0 of 0 tasks checked |
| Failures and excluded cases | none excluded; all 8 cases are listed, losses included |
| Price | not applicable: no money figure is claimed (unpriced) |
| Scope | only these inputs and this counter; it does not extend to other models, providers, tasks or dates |

## Why this measurement can be trusted

- **Both sides come from real files and real tool output.** The "without the skill" figure is the size of the input Claude would read; the "with the skill" figure is the size of what the tool printed for that same input. Nothing is modeled except the token estimate itself.
- **The skill's own cost is charged in full, in every case.** Each case adds the skill description (79 tokens), the body of `SKILL.md` (420 tokens), the command that was run and, when the read hook intervenes, its block message. In a real session the description and the body are paid once, so real savings are higher than these.
- **The "no skill" side uses no resource of the skill at all.** It is a plain read, with no conversion, no summary and no index.
- **Every case is listed, including the ones where the skill loses.** The range is the minimum and the maximum of all the cases, rounded down.
- **The inputs are fixed and described**, so the numbers do not depend on a model's sampling and can be recomputed.

## Limits

- Tokens are estimated (characters divided by 4 for text, pixels divided by 750 for images), not counted with Anthropic's tokenizer, so each figure carries roughly a 30% margin. They are good for comparing, not for billing.
- Task success was not measured with agents. A mechanic that lowered success would not be accepted; this report only covers the tokens.
- The inputs are samples, partly synthetic. Real projects will differ.
- A table does not show the type of each value, and a CSV schema omits rows (it says how many). Whether those losses matter for a given task was not tested.
