# Changelog

## 1.0.1

- **Fixed:** the read hook no longer deviates a content search without a limit. In real runs the agent repeated the same search right after the notice, so the notice only added a turn (+15% to +17% in dollars on small tasks). The hook now watches only the `Read` tool; installing again drops the `Grep` matcher.

## 1.0.0

First stable release. The commands and options listed in the README are stable: they do not change inside a major version, and new options may be added.

- **Reading:** `convertir_fuentes.py` (documents to Markdown, images to 1024 px), `capturar.py` (headless screenshots reduced), and a read hook that blocks heavy files with the exact command, deviates once per session a long file read whole, a repeated read of the same range and a content search without a limit.
- **Compaction and output:** `compactar.py` (JSON, CSV, logs, lockfiles, generated files), `resumir.py` (test, lint and build output). Both return the original when the gain is not meaningful, cap the input at 64 MiB, strip ANSI and progress redraws, keep every error signal and say what they may have lost.
- **Exploration and review:** `estimar.py`, `relevar.py` (languages, entry points, manifests, tests and tools, CI, documentation), `impacto.py`, `duplicados.py`, `contexto.py`.
- **Memory:** `indexar_docs.py` (index of documents and code with the cost of opening each result, continuity note with a token cap).
- **Hygiene:** `consumo.py` (fixed context, CLAUDE.md as a sum, hooks and permissions, heaviest skills), `texto.py` (line caps, repetition and information loss in documents), `comentarios.py` (comment noise, optionally only on changed lines).
- **Behavior:** diet profiles (light, standard, strict) chosen once with `modo.py profile`.
- **Installer:** `instalar.py install | check | status | uninstall`, with a dry run, a settings backup and an integrity check of the installed hook files.
- **Measurement:** every aspect has a report in `docs/measurements/` with its method, every case, its evidence basis and its limits.
