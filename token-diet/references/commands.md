# Commands and options

Every script answers `--version`. Options listed here are stable inside a major version.

| Script | Use | Options |
|---|---|---|
| `convertir_fuentes.py FILE...` | Documents to Markdown (cached by hash, warns when text may have been lost); images to 1024 px on the long side, never enlarged, EXIF respected. Plain text, JSON and CSV are left alone | `--out`, `--max-px`, `--json` |
| `capturar.py URL_OR_FILE` | Headless screenshot (Edge, Chrome or Chromium installed on the machine, or `TOKEN_DIET_BROWSER`) already reduced to 1024 px; the raw capture stays under `<out>/raw` | `--out`, `--max-px`, `--width`, `--height`, `--json` |
| `hook_lectura_externa.py` | Pre-read hook: blocks PDF, Office, images over the profile size and big lockfiles or generated files, and gives the exact command; the first whole read of a text file above the profile line cap (400 by default) is deviated once per session with the way to read a range, and repeating the same Read goes through. Registered by `instalar.py` | `--version` |
| `modo.py allow PATTERN \| show \| profile [light\|standard\|strict]` | Emergency exit for the hook (`TOKEN_DIET_LECTURA_DIRECTA=1` disables every block); the diet profile sets the thresholds the other tools read: image size (1568, 1024 or 768 px), generated-file size, read cap in lines, minimum gain worth a rewrite | `profile` |
| `consumo.py` | Fixed cost per session against limits, what to trim first; `--repo DIR` audits a repository without installing it | `--root`, `--home`, `--repo`, `--json`, `--out` |
| `compactar.py FILE` | JSON (a table when rows are uniform), CSV schema, logs (WARN and ERROR with context), lockfiles, generated files. Says what may have been lost | `--mode`, `--sample`, `--context`, `--out`, `--stdout`, `--lines A-B` |
| `resumir.py -- COMMAND` | Runs the command; returns the exit code, duration and the lines that matter; the full output is saved | `--max-lines`, `--timeout`, `--out` |
| `texto.py check \| compare OLD NEW` | Documents above their line cap (path patterns in `.token-diet/config.json`, `document_limits`), paragraphs repeated between documents, and what a moved or trimmed text lost (headings, inline code, URLs, paths, numbers); `token-diet-ignore` skips | `--root`, `--min-chars`, `--json` |
| `comentarios.py PATH...` | Reports comments that say what the code says, commented-out code and decoration; skips directives, licenses, TODO and `token-diet-ignore`; never edits | `--ext`, `--max`, `--json` |
| `estimar.py PATH...` | Token cost of reading paths, by folder; `--budget` exits 1 when over | `--depth`, `--top`, `--budget`, `--json` |
| `impacto.py SYMBOL` | Definition, uses and similar existing names | `--root`, `--max-files`, `--json` |
| `contexto.py` | Case file of a change: files, symbols, users, what to look at first, warnings | `--staged`, `--base`, `--head`, `--root`, `--json` |
| `duplicados.py PATH...` | Repeated blocks of code | `--min-lines`, `--max`, `--ext`, `--json` |
| `relevar.py ROOT` | Inventory of an unfamiliar project | `--top`, `--out`, `--json` |
| `indexar_docs.py build \| query TERMS \| note show\|write` | Index of documents and code with the cost of opening each result; continuity note with a token cap | `--root`, `--limit`, `--text`, `--quiet` |

## Cost

What the skill itself adds, in tokens (characters divided by 4):

| When | Cost |
|---|---|
| Every session | about 80 (the description) |
| When the skill is used | about 400 once (the body of `SKILL.md`) |
| Each call | about 20 for the command plus its output: one line for a conversion, a summary or a block message, up to a few dozen lines for a case file or an index query |

Whether it pays: the measurement report of each aspect lists every case, losses included. For a small input the skill costs more than it saves; the tools say so and return the original (`not worth compacting`).
