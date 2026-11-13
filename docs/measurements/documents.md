# Documents (HTML): saving versus no skill

**Result: 57% to 70%** (minimum to maximum over 40 cases, net of the skill's own cost).

**Target (expected, not a result):** 50% to 90%. Basis: target for styled HTML, PDF and Word.

## What was compared

- **Without the skill:** Claude reads the HTML file as it is: markup, styles and scripts included.
- **With the skill:** The file is converted to Markdown and only the Markdown is read.

## Inputs

Real HTML pages of the Python 3.12 documentation (library section, between 3 KB and 700 KB), evenly spaced to avoid choosing the favorable ones.

## Cases

| Case | Without the skill (tokens) | With the skill (tokens) | Saving |
|---|---:|---:|---:|
| 2to3.html | 19,595 | 6,196 | 68% |
| archiving.html | 5,839 | 1,965 | 66% |
| asyncio-exceptions.html | 5,880 | 1,872 | 68% |
| asyncio-queue.html | 9,664 | 3,099 | 67% |
| atexit.html | 7,696 | 2,547 | 66% |
| bisect.html | 12,538 | 3,700 | 70% |
| cmath.html | 12,699 | 4,201 | 66% |
| collections.html | 50,383 | 16,784 | 66% |
| constants.html | 7,430 | 2,531 | 65% |
| csv.html | 23,912 | 8,120 | 66% |
| datatypes.html | 8,507 | 2,776 | 67% |
| dialog.html | 12,510 | 3,819 | 69% |
| email.contentmanager.html | 10,978 | 3,958 | 63% |
| email.html | 9,262 | 3,956 | 57% |
| ensurepip.html | 7,678 | 2,699 | 64% |
| fileformats.html | 5,047 | 1,573 | 68% |
| functional.html | 4,596 | 1,422 | 69% |
| glob.html | 8,807 | 2,766 | 68% |
| html.entities.html | 5,317 | 1,633 | 69% |
| http.server.html | 20,956 | 8,667 | 58% |
| importlib.resources.abc.html | 9,165 | 3,429 | 62% |
| ipaddress.html | 36,801 | 13,882 | 62% |
| locale.html | 24,517 | 8,875 | 63% |
| markup.html | 7,213 | 2,599 | 63% |
| modules.html | 5,850 | 1,940 | 66% |
| nis.html | 5,931 | 1,898 | 67% |
| os.path.html | 19,602 | 7,129 | 63% |
| pipes.html | 7,089 | 2,156 | 69% |
| profile.html | 23,314 | 9,484 | 59% |
| python.html | 8,320 | 2,958 | 64% |
| resource.html | 14,015 | 4,946 | 64% |
| selectors.html | 12,505 | 4,263 | 65% |
| sndhdr.html | 6,747 | 2,054 | 69% |
| statistics.html | 37,555 | 12,970 | 65% |
| superseded.html | 5,165 | 1,501 | 70% |
| tabnanny.html | 5,576 | 1,749 | 68% |
| textwrap.html | 13,973 | 4,830 | 65% |
| tkinter.font.html | 7,122 | 2,184 | 69% |
| tokenize.html | 11,835 | 4,290 | 63% |
| types.html | 20,210 | 6,827 | 66% |

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
