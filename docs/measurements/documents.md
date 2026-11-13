# Documents (HTML): saving versus no skill

**Result: 54% to 68%** (minimum to maximum over 40 cases, net of the skill's own cost).

**Target (expected, not a result):** 50% to 90%. Basis: target for styled HTML, PDF and Word.

## What was compared

- **Without the skill:** Claude reads the HTML file as it is: markup, styles and scripts included.
- **With the skill:** The file is converted to Markdown and only the Markdown is read.

## Inputs

Real HTML pages of the Python 3.12 documentation (library section, between 3 KB and 700 KB), evenly spaced to avoid choosing the favorable ones.

## Cases

| Case | Without the skill (tokens) | With the skill (tokens) | Saving |
|---|---:|---:|---:|
| 2to3.html | 19,595 | 6,434 | 67% |
| archiving.html | 5,839 | 2,203 | 62% |
| asyncio-exceptions.html | 5,880 | 2,110 | 64% |
| asyncio-queue.html | 9,664 | 3,337 | 65% |
| atexit.html | 7,696 | 2,785 | 63% |
| bisect.html | 12,538 | 3,938 | 68% |
| cmath.html | 12,699 | 4,439 | 65% |
| collections.html | 50,383 | 17,022 | 66% |
| constants.html | 7,430 | 2,769 | 62% |
| csv.html | 23,912 | 8,358 | 65% |
| datatypes.html | 8,507 | 3,014 | 64% |
| dialog.html | 12,510 | 4,057 | 67% |
| email.contentmanager.html | 10,978 | 4,196 | 61% |
| email.html | 9,262 | 4,194 | 54% |
| ensurepip.html | 7,678 | 2,937 | 61% |
| fileformats.html | 5,047 | 1,811 | 64% |
| functional.html | 4,596 | 1,660 | 63% |
| glob.html | 8,807 | 3,004 | 65% |
| html.entities.html | 5,317 | 1,871 | 64% |
| http.server.html | 20,956 | 8,905 | 57% |
| importlib.resources.abc.html | 9,165 | 3,667 | 59% |
| ipaddress.html | 36,801 | 14,120 | 61% |
| locale.html | 24,517 | 9,113 | 62% |
| markup.html | 7,213 | 2,837 | 60% |
| modules.html | 5,850 | 2,178 | 62% |
| nis.html | 5,931 | 2,136 | 63% |
| os.path.html | 19,602 | 7,367 | 62% |
| pipes.html | 7,089 | 2,394 | 66% |
| profile.html | 23,314 | 9,722 | 58% |
| python.html | 8,320 | 3,196 | 61% |
| resource.html | 14,015 | 5,184 | 63% |
| selectors.html | 12,505 | 4,501 | 64% |
| sndhdr.html | 6,747 | 2,292 | 66% |
| statistics.html | 37,555 | 13,208 | 64% |
| superseded.html | 5,165 | 1,739 | 66% |
| tabnanny.html | 5,576 | 1,987 | 64% |
| textwrap.html | 13,973 | 5,068 | 63% |
| tkinter.font.html | 7,122 | 2,422 | 65% |
| tokenize.html | 11,835 | 4,528 | 61% |
| types.html | 20,210 | 7,065 | 65% |

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
- PDF and Word documents are not included: no real files were available to test.
