# Documents (HTML): saving versus no skill

**Result: 57% to 70%** (minimum to maximum over 40 cases, net of the skill's own cost).

**Target (expected, not a result):** 50% to 90%. Basis: target for styled HTML, PDF and Word.

## What was compared

- **Without the skill:** Claude reads the HTML file as it is: markup, styles and scripts included.
- **With the skill:** The file is converted to Markdown and only the Markdown is read.

## Inputs

Real HTML pages of the Python 3.12 documentation (library section, between 3 KB and 700 KB), evenly spaced to avoid choosing the favorable ones.

## Cases

| Case | Input fingerprint | Without the skill (tokens) | With the skill (tokens) | Saving |
|---|---|---:|---:|---:|
| 2to3.html | 6d0cdb19be | 19,595 | 6,196 | 68% |
| archiving.html | 7866dc5491 | 5,839 | 1,965 | 66% |
| asyncio-exceptions.html | 0642318cc0 | 5,880 | 1,872 | 68% |
| asyncio-queue.html | d6dfcce1c1 | 9,664 | 3,099 | 67% |
| atexit.html | 2e5793a497 | 7,696 | 2,547 | 66% |
| bisect.html | 41f90e99b1 | 12,538 | 3,700 | 70% |
| cmath.html | 85f162640d | 12,699 | 4,201 | 66% |
| collections.html | fe5ffa24a1 | 50,383 | 16,784 | 66% |
| constants.html | 9bff2299a1 | 7,430 | 2,531 | 65% |
| csv.html | 62c665a618 | 23,912 | 8,120 | 66% |
| datatypes.html | edf5f2874e | 8,507 | 2,776 | 67% |
| dialog.html | 395d7aaff9 | 12,510 | 3,819 | 69% |
| email.contentmanager.html | de0bcee294 | 10,978 | 3,958 | 63% |
| email.html | b67358be01 | 9,262 | 3,956 | 57% |
| ensurepip.html | 18e89a4ed3 | 7,678 | 2,699 | 64% |
| fileformats.html | c10b0a4051 | 5,047 | 1,573 | 68% |
| functional.html | 54495063be | 4,596 | 1,422 | 69% |
| glob.html | 58f9b97d76 | 8,807 | 2,766 | 68% |
| html.entities.html | 6b606549af | 5,317 | 1,633 | 69% |
| http.server.html | 86d745f113 | 20,956 | 8,667 | 58% |
| importlib.resources.abc.html | 894ba35061 | 9,165 | 3,429 | 62% |
| ipaddress.html | 0100a0251f | 36,801 | 13,882 | 62% |
| locale.html | ba218c8ea7 | 24,517 | 8,875 | 63% |
| markup.html | fe61ceca4e | 7,213 | 2,599 | 63% |
| modules.html | ee370d61aa | 5,850 | 1,940 | 66% |
| nis.html | 375fc57b77 | 5,931 | 1,898 | 67% |
| os.path.html | 8480215618 | 19,602 | 7,129 | 63% |
| pipes.html | 3fc9b36659 | 7,089 | 2,156 | 69% |
| profile.html | 83ed0c588f | 23,314 | 9,484 | 59% |
| python.html | b01dacbd9b | 8,320 | 2,958 | 64% |
| resource.html | 789913e11e | 14,015 | 4,946 | 64% |
| selectors.html | 98da484673 | 12,505 | 4,263 | 65% |
| sndhdr.html | bf5181e87a | 6,747 | 2,054 | 69% |
| statistics.html | 6778a29e33 | 37,555 | 12,970 | 65% |
| superseded.html | 99a23ceafe | 5,165 | 1,501 | 70% |
| tabnanny.html | af10414590 | 5,576 | 1,749 | 68% |
| textwrap.html | e4ca10f7ca | 13,973 | 4,830 | 65% |
| tkinter.font.html | afbf281f2e | 7,122 | 2,184 | 69% |
| tokenize.html | 9d4083296a | 11,835 | 4,290 | 63% |
| types.html | 4dd9324e05 | 20,210 | 6,827 | 66% |

## Evidence

| Field | Value |
|---|---|
| Basis of the result | benchmark counterfactual: the same inputs read without and with the skill |
| Basis of the token counts | inferred: characters divided by 4 for text, pixels divided by 750 for images; not a provider count |
| Inputs | listed above, each with a fingerprint (first 10 characters of the SHA-256 of the exact input) |
| Code revision | 45797db |
| Quality check | not run: task success was not tested; 0 of 0 tasks checked |
| Failures and excluded cases | none excluded; all 40 cases are listed, losses included |
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
- PDF and Word documents are not included: no real files were available to test.
