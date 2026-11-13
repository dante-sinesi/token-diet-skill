---
name: token-diet
description: Saves tokens without lowering performance. Use when reading documents, PDFs, Word files, images, JSON, logs, lockfiles or large files; when running commands with long output; when measuring or trimming what is loaded every session (CLAUDE.md, skills, memory); and when sessions fill up fast or context keeps growing.
---

# Token Diet

Saves tokens only where it does not change a decision (format, whitespace, markup, repetition, noise, generated files), never on reasoning or on what is verified.

**Golden rule:** the fixed part, minimal; the detail, on demand; what a script can resolve, let a script resolve it and return few lines.

## Before reading or asking
1. Is it needed?
2. Is it already in the conversation?
3. Is there a summary or a script that gives it in a few lines?

## Principles
- Every reduction carries an emergency exit (line range, original with permission, full section).
- Each mechanic declares its risk and warns when it may have lost something.
- A mechanic that lowers task success does not get in.
- The skill cannot cost more than it saves.

## Mechanics

| Mechanic | Script |
|---|---|
| Documents to Markdown and images to 1024 px. Run `python scripts/convertir_fuentes.py FILE`, then read the generated `.md` or image in `.token-diet/sources/`, never the original | `convertir_fuentes.py` |
| Block direct reads of PDF, Word, heavy images and big lockfiles or generated files; the block message gives the exact command. `modo.py allow PATTERN` lets one file through | `hook_lectura_externa.py`, `modo.py` |
| Measure what is always loaded and say what to trim first (`--repo DIR` audits a repository without installing it) | `consumo.py` |
| Compact JSON (table when rows are uniform), logs (WARN and ERROR with context), lockfiles and generated files. `--lines A-B` reads the original; the report says what may have been lost | `compactar.py` |
| Summarize test, linter or build output: `python scripts/resumir.py -- COMMAND` | `resumir.py` |
| Estimate the cost of reading some paths before spending it (`--budget`) | `estimar.py` |
| Where a symbol is defined and used, what similar already exists, repeated blocks | `impacto.py`, `duplicados.py` |
| Case file for a change (read it instead of the diff) | `contexto.py` |
| System inventory before reading an unfamiliar project | `relevar.py` |
| Index of documents and code with the cost of opening each result: `build`, then `query TERMS`; `note show` at the start of a session and `note write` at the end keep the continuity note | `indexar_docs.py` |

## References
- `references/tokens.md`: guide to command output and reads.
