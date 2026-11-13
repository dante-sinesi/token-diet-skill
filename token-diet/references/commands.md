# Commands and options

Every script answers `--version`. Options listed here are stable inside a major version.

| Script | Use | Options |
|---|---|---|
| `convertir_fuentes.py FILE...` | Documents to Markdown (cached by hash, warns when text may have been lost); images to 1024 px on the long side, never enlarged, EXIF respected. Plain text, JSON and CSV are left alone | `--out`, `--max-px`, `--json` |
| `capturar.py URL_OR_FILE` | Headless screenshot (Edge, Chrome or Chromium installed on the machine, or `TOKEN_DIET_BROWSER`) already reduced to 1024 px; the raw capture stays under `<out>/raw` | `--out`, `--max-px`, `--width`, `--height`, `--json` |
| `hook_lectura_externa.py` | Pre-read hook: blocks PDF, Office, images over 1024 px and big lockfiles or generated files, and gives the exact command. Registered by `instalar.py` | `--version` |
| `modo.py allow PATTERN \| show` | Emergency exit for the hook; `TOKEN_DIET_LECTURA_DIRECTA=1` disables every block | none |
| `consumo.py` | Fixed cost per session against limits, what to trim first; `--repo DIR` audits a repository without installing it | `--root`, `--home`, `--repo`, `--json`, `--out` |
| `compactar.py FILE` | JSON (a table when rows are uniform), CSV schema, logs (WARN and ERROR with context), lockfiles, generated files. Says what may have been lost | `--mode`, `--sample`, `--context`, `--out`, `--stdout`, `--lines A-B` |
| `resumir.py -- COMMAND` | Runs the command; returns the exit code, duration and the lines that matter; the full output is saved | `--max-lines`, `--timeout`, `--out` |
| `texto.py check \| compare OLD NEW` | Documents above their line cap (path patterns in `.token-diet/config.json`, `document_limits`), paragraphs repeated between documents, and what a moved or trimmed text lost (headings, inline code, URLs, paths, numbers); `token-diet-ignore` skips | `--root`, `--min-chars`, `--json` |
| `estimar.py PATH...` | Token cost of reading paths, by folder; `--budget` exits 1 when over | `--depth`, `--top`, `--budget`, `--json` |
| `impacto.py SYMBOL` | Definition, uses and similar existing names | `--root`, `--max-files`, `--json` |
| `contexto.py` | Case file of a change: files, symbols, users, what to look at first, warnings | `--staged`, `--base`, `--head`, `--root`, `--json` |
| `duplicados.py PATH...` | Repeated blocks of code | `--min-lines`, `--max`, `--ext`, `--json` |
| `relevar.py ROOT` | Inventory of an unfamiliar project | `--top`, `--out`, `--json` |
| `indexar_docs.py build \| query TERMS \| note show\|write` | Index of documents and code with the cost of opening each result; continuity note with a token cap | `--root`, `--limit`, `--text`, `--quiet` |
