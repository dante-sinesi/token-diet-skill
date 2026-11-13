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
