<p align="center"><img src="docs/img/cover.svg" alt="Token Diet" width="760"><br><sub>Token Diet cover: a Claude Code skill that saves tokens without lowering performance.</sub></p>

## Measured savings

<p align="center"><img src="docs/img/agent-savings.svg" alt="Measured saving versus no skill, by aspect" width="760"><br><sub>Median cost in dollars of the same task with and without the skill, from real agent runs (3 to 4 repetitions per task, answers checked, 100% success in every arm); negative means the skill costs more. For documents and long files the saving comes from the read hook (the agent did not call the skill itself); for fixed context it is the value of trimming an instruction file of 10,000 to 40,000 tokens, which an agent asked to do it does alone, with or without the skill. Aspects not shown were tried and removed, or have no agent measurement yet.</sub></p>

## Expected savings

<p align="center"><img src="docs/img/savings.svg" alt="Expected saving versus no skill, by aspect" width="760"><br><sub>Expected targets for the saving versus using no skill at all, net of the skill's own cost; these are not results. Real data today (estimates from runs on sample inputs, no agent runs; negative means the skill costs more than it saves): Code exploration −119% to 98%; Change review 21% to 88%; Documentation lookup 57% to 89%; Lockfiles and generated 78% to 99%.</sub></p>

## Measurements

Each report gives the method, every case measured and the limits:

- [Documents](docs/measurements/documents.md)
- [Command output](docs/measurements/command-output.md)
- [Code exploration](docs/measurements/code-exploration.md)
- [Change review](docs/measurements/change-review.md)
- [Documentation lookup](docs/measurements/documentation-lookup.md)
- [Lockfiles and generated files](docs/measurements/lockfiles-and-generated.md)
- [Fixed context](docs/measurements/fixed-context.md)
- [Real agent runs](docs/measurements/agent-runs.md)
- [Tried, measured and removed](docs/measurements/removed.md): what did not pay for itself, with the measurement behind each decision

## Main goal

The main goal is that, when the time comes, the `senior` skill sheds everything Token Diet already covers.

- When a Token Diet token-saving mechanic covers the same or more than the one in `senior`, `senior` drops its own.
- From then on `senior` depends on Token Diet being always installed, because without it `senior` would consume too much.
- Direction of the dependency: `senior` will depend on Token Diet; Token Diet will never depend on `senior`.

## Usage

Every script lives in `token-diet/scripts/` and answers `--version`. The options listed here are stable: they do not change inside a major version, and new ones may be added.

| Command | What it does | Stable options |
|---|---|---|
| `convertir_fuentes.py FILE...` | Documents to Markdown (images to 1024 px on request); read the output in `.token-diet/sources/`, never the originals | `--out`, `--max-px`, `--json` |
| `capturar.py URL_OR_FILE` | Headless screenshot of a page or file, reduced to 1024 px | `--out`, `--max-px`, `--width`, `--height`, `--json` |
| `consumo.py` | Audits what loads every session and says what to trim first; `--repo` adds a repository's skills, `--only-repo` measures them instead of the installed ones | `--root`, `--home`, `--repo`, `--only-repo`, `--json`, `--out` |
| `compactar.py FILE` | Compacts JSON, CSV, logs, lockfiles and generated files and says what it may have lost | `--mode`, `--sample`, `--context`, `--out`, `--stdout`, `--lines A-B` |
| `resumir.py -- COMMAND` | Runs a test, lint or build command and returns only the lines that matter | `--max-lines`, `--timeout`, `--out` |
| `texto.py check \| compare OLD NEW` | Documents above their line cap, paragraphs repeated between documents, and what a moved or trimmed text lost | `--root`, `--min-chars`, `--json` |
| `comentarios.py [PATH...]` | Reports comment noise (says what the code says, commented-out code, decoration), optionally only on changed lines; never edits | `--ext`, `--max`, `--json`, `--changed`, `--base` |
| `estimar.py [PATH...]` | Estimates the token cost of reading paths before spending it | `--depth`, `--top`, `--budget`, `--json` |
| `impacto.py SYMBOL` | Where a symbol is defined and used, and what similar already exists; `--exists WORDS` finds definitions that share words | `--root`, `--max-files`, `--json`, `--exists` |
| `contexto.py` | Case file of a change, of some files as they are, or of a Pull Request: what it touches, who uses it, what to look at first | `--staged`, `--base`, `--head`, `--files`, `--pr`, `--root`, `--json` |
| `duplicados.py [PATH...]` | Repeated blocks of code | `--min-lines`, `--max`, `--ext`, `--json` |
| `relevar.py [ROOT]` | Inventory of an unfamiliar project | `--top`, `--out`, `--json` |
| `indexar_docs.py build \| query TERMS \| note show\|write` | Index of documents and code with the cost of opening each result; continuity note with a token cap | `--root`, `--limit`, `--text`, `--quiet` |
| `modo.py allow PATTERN \| show \| profile [light\|standard\|strict]` | Emergency exit for the read hook; diet profile that sets how strict the thresholds are (standard by default) | `profile` |
| `instalar.py install \| check \| status \| uninstall` (repository root) | Installs the skill and its hooks, checks for drift, shows what is on and the next step, removes both | `--home`, `--no-note-hook`, `--dry-run` |

## Install

To make the conversion mandatory and the continuity note automatic, install the skill and its hooks:

```bash
python instalar.py install
```

It copies the skill to `~/.claude/skills/token-diet/` and registers two hooks in `~/.claude/settings.json` (a backup is kept and the rest of the file is untouched; `--dry-run` shows every change without making it): one blocks a `Read` of a PDF, Office document, or big lockfile or generated file and gives the exact command, and deviates once per session the first whole read of a text file longer than the line cap of the profile (400 lines by default) toward a ranged read; the other loads the continuity note at the start of a session. `python instalar.py check` says whether the installed copy still matches this repository and `python instalar.py uninstall` removes both.

Emergency exits: `python token-diet/scripts/modo.py allow PATTERN` for one file, or `TOKEN_DIET_LECTURA_DIRECTA=1` for everything. A broken hook allows the read and logs the error in `.token-diet/hook-errors.log` (`TOKEN_DIET_HOOK_DEPURAR=1` shows it).
