---
name: token-diet
description: Saves tokens without lowering performance. Use when reading documents, PDFs, Word files, images, JSON, logs, lockfiles or large files; when running commands with long output; when measuring or trimming what is loaded every session (CLAUDE.md, skills, memory); and when sessions fill up fast or context keeps growing.
---

# Token Diet

Save tokens only where no decision changes (format, markup, repetition, noise, generated files), never on reasoning or verification. Fixed part minimal, detail on demand, what a script can resolve returned in few lines.

Before reading or asking: is it needed? already in the conversation? is there a summary or a script?

Run `python scripts/NAME.py` (options and costs: `references/commands.md`):
- Document, PDF, Word, image: `convertir_fuentes.py FILE`; read its output in `.token-diet/sources/`, never the original. Page or screen: `capturar.py URL_OR_FILE`.
- JSON, CSV, log, lockfile, minified file: `compactar.py FILE`. Test, lint or build output: `resumir.py -- COMMAND`.
- Before reading many files: `estimar.py PATH`. Unfamiliar project: `relevar.py`. A symbol: `impacto.py SYMBOL`. A change: `contexto.py`. Repeated code: `duplicados.py`. Comment noise: `comentarios.py`.
- Answers from documents: `indexar_docs.py query TERMS`. Continuity: `note show` at the start of a session, `note write` at the end. Documents too long or repeated: `texto.py check`; after moving text: `texto.py compare OLD NEW`.
- What loads every session: `consumo.py`.
- A read was blocked: follow the command in the message; `modo.py allow PATTERN` lets one file through. Small task or strict budget: `modo.py profile light|strict`.

Ask the user before launching parallel agents or a verifier agent (8,000 to 25,000 tokens each). Every reduction has an exit (line range, original, full section) and says what it may have lost. A mechanic that lowers task success does not get in. The skill must not cost more than it saves. Guide to output and reads: `references/tokens.md`.
