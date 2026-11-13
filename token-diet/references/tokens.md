# Guide to command output and reads

## Where tokens are spent

| What is loaded | Example | When it is paid |
|---|---|---|
| Always | skill descriptions, `CLAUDE.md`, memory index | every session |
| On activation | body of a `SKILL.md` | when the skill comes into play |
| On demand | `references/`, documents, code, command output | when it is opened or run |
| Accumulated | everything that entered the conversation | on every following turn |

## Command output
- `git log -n 20 --oneline`; `git diff --stat` before `git diff`.
- Tests in quiet mode (`pytest -q`, `--silent`).
- `grep -c` or `grep -l` before `grep`; `head` or `tail` to bound output.
- Save the detail to a file and read only the section that matters.

## Reads
- Search before reading; read by ranges.
- Do not re-read what was just edited.
- Subagents with a short report.
- External documents: convert to Markdown before reading.

## Prompt cache
Do not modify `CLAUDE.md` or the skills in the middle of a long session: a change in what is loaded first forces the prefix to be reprocessed.

## Context hygiene

Everything in the conversation is paid again on every turn, and answers tend to degrade when the conversation passes about half of the context window (a rule of thumb, not a measured limit).

- **Summarize** after a finished milestone, before changing topic, and when the same files keep being read again.
- **Start a new session** for an unrelated task, when the conversation is above half of the window, or when the same error keeps coming back.
- **How:** write the continuity note (`python scripts/indexar_docs.py note write`) with the goal, the state, the next step and the decisions, within its token cap; the new session reads it with `note show`.
- **Do not edit** `CLAUDE.md` or the skills in the middle of a long session: it invalidates the cached prefix.

