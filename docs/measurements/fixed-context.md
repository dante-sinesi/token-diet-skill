# Fixed context: saving versus no skill

**Result: −37% to 41%** (minimum to maximum over 2 cases, net of the skill's own cost).

**Target (expected, not a result):** 0% to 30%. Basis: target: trimming what is over the limits.

## What was compared

- **Without the skill:** Everything that loads in every session stays as it is.
- **With the skill:** The audit is run and what it flags (a long CLAUDE.md, long skill descriptions, a long memory index) is trimmed to the limits.

## Inputs

Two synthetic setups: a lean one (nothing over the limits) and a bloated one (CLAUDE.md of 6,000 tokens, three skill descriptions of 1,200 characters, a memory index of 300 lines).

## Cases

| Case | Input fingerprint | Without the skill (tokens) | With the skill (tokens) | Saving |
|---|---|---:|---:|---:|
| lean setup | 399b309539 | 1,594 | 2,175 | −37% |
| bloated setup | e7f9ec8a16 | 10,281 | 6,006 | 41% |

## Evidence

| Field | Value |
|---|---|
| Basis of the result | benchmark counterfactual: the same inputs read without and with the skill |
| Basis of the token counts | inferred: characters divided by 4 for text, pixels divided by 750 for images; not a provider count |
| Inputs | listed above, each with a fingerprint (first 10 characters of the SHA-256 of the exact input) |
| Code revision | db204d2 |
| Quality check | not run: task success was not tested; 0 of 0 tasks checked |
| Failures and excluded cases | none excluded; all 2 cases are listed, losses included |
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
- The saving exists only if the flagged content is really trimmed, and trimming may remove something useful: that judgment is left to the person.
