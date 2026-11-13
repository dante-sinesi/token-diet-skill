# Images: saving versus no skill

**Result: −27% to 29%** (minimum to maximum over 10 cases, net of the skill's own cost).

**Target (expected, not a result):** 0% to 57%. Basis: ceiling from pixels / 750: 1024 px against the 1568 px API cap.

## What was compared

- **Without the skill:** Claude reads the original image. The API already shrinks anything above 1568 px on its long side, so the cost without the skill is that of the shrunk image.
- **With the skill:** The image is reduced to 1024 px on its long side before reading. Images that already fit are read as they are.

## Inputs

Ten image sizes from 640x480 to 4000x3000 px; three of them are typical screen captures (1920x1080, 2560x1440, 3840x2160).

## Cases

| Case | Input fingerprint | Without the skill (tokens) | With the skill (tokens) | Saving |
|---|---|---:|---:|---:|
| 640x480 px | e81dd57ce8 | 410 | 489 | −20% |
| 800x600 px | b01093be75 | 640 | 719 | −13% |
| 1024x768 px | 4841528268 | 1,049 | 1,128 | −8% |
| 1200x800 px | 705ef6a849 | 1,280 | 1,619 | −27% |
| 1568x1045 px | 0a4c381ab1 | 2,185 | 1,618 | 25% |
| 3000x2000 px | 5a127e5de6 | 2,185 | 1,619 | 25% |
| 4000x3000 px | 0125fbdad5 | 2,459 | 1,735 | 29% |
| 1920x1080 px | c687d19564 | 1,844 | 1,473 | 20% |
| 2560x1440 px | 88a175bba1 | 1,844 | 1,473 | 20% |
| 3840x2160 px | 9ac20afbda | 1,844 | 1,473 | 20% |

## Evidence

| Field | Value |
|---|---|
| Basis of the result | benchmark counterfactual: the same inputs read without and with the skill |
| Basis of the token counts | inferred: characters divided by 4 for text, pixels divided by 750 for images; not a provider count |
| Inputs | listed above, each with a fingerprint (first 10 characters of the SHA-256 of the exact input) |
| Code revision | db204d2 |
| Quality check | not run: task success was not tested; 0 of 0 tasks checked |
| Failures and excluded cases | none excluded; all 10 cases are listed, losses included |
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
- Image content is not compared: the cost of an image depends only on its size, but whether 1024 px is enough detail for a given task was not tested.
