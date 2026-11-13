# Tried, measured and removed

Some mechanics were built, measured against not having them, and taken out because having them cost more than not having them. This page says which, with the measurement behind each decision. The reports linked here are the ones written before the decision; they measure the mechanic on its own, not what an agent does with it.

## Heavy images: the read block and the 1024 px conversion

- **What it did:** the read hook blocked a `Read` of an image larger than 1024 px and pointed to `convertir_fuentes.py`, which reduces it.
- **What was measured:** estimating tokens on sample images ([Images](images.md)) gave −27% to 29% on sample images (a loss on small ones, a gain on large ones). A real agent run ([Real agent runs](agent-runs.md), a 3000 by 2000 px image with a ticket number in large letters, 3 repetitions) cost −8% in dollars with the skill and took one more turn: the agent's own image read is already reduced, so the block only added a round trip.
- **Decision:** the hook no longer blocks images (release 1.0.2), and the skill no longer recommends converting them. The converter stays available as a command.

## Compacting JSON, CSV and plain text

- **What it did:** the skill told the agent to compact a JSON, CSV or plain-text file before reading it.
- **What was measured:** estimating tokens on sample files ([Plain text, JSON, CSV](plain-text-json-csv.md)) gave −64% to 70% on sample files. A real agent run ([Real agent runs](agent-runs.md), a 1,400-item JSON catalog of about 200 KB, one price to find, 3 repetitions) cost −3% in dollars with the skill: the agent searched the file for the item and never read it whole, so there was nothing to compact, and the skill's own text was paid for nothing.
- **Decision:** the skill no longer lists JSON or CSV among the files to compact. The compaction command stays for logs, lockfiles and generated files.

## Notice on a repeated read of the same range

- **What it did:** the second read of the same unchanged range in a session was deviated once toward the text already in the conversation.
- **What was measured:** in a 3-question session over a 380-line file (4 repetitions, [Real agent runs](agent-runs.md)) the notice never fired, because the agent read the file once and answered from it; the cost was −1% against not having it.
- **Decision:** removed in release 1.0.2: a mechanic with no measured benefit does not stay.

## Document index query

- **What it did:** the skill told the agent to query an index of the documents instead of searching them.
- **What was measured:** in a folder of 40 documents with one fact to find ([Real agent runs](agent-runs.md), section 8, 4 repetitions) the cost with the skill installed was 0% against not having it, and −14% when the agent was told to build and query the index first: the agent's own search already finds a distinctive word in one call.
- **Decision:** the query is no longer recommended by the skill (release 1.0.3). The index stays available as a command, and the continuity note, which did pay (+29%), stays.

## Delegating a search to a cheaper model

- **What it would do:** hand mechanical searches to a subagent on the light model and answer from its short report.
- **What was measured:** five tasks, 4 repetitions ([Real agent runs](agent-runs.md), section 8): −2%, −29% and −18% on three searches, −1% and +44% on two tasks that need several files read. No size gave a consistent saving.
- **Decision:** not built. The skill only keeps the rule of asking before launching agents.

## Notice on content searches

- **What it did:** a content search without a limit was deviated once toward a narrower search.
- **What was measured:** in 36 real agent runs on a log-search task the agent repeated the same search right after the notice, adding one turn: +15% to +17% in dollars ([Real agent runs](agent-runs.md)).
- **Decision:** removed in release 1.0.1.

## Why the bar is "costs more to have than not to have"

An agent already knows how to search a file, read a range and read an image, so a mechanic that only repeats those saves nothing, while its text, its notices and the extra turns they cause are paid in every session. The mechanics that stay are the ones where the agent has no cheap way of its own: a PDF, and a long text file read whole.
