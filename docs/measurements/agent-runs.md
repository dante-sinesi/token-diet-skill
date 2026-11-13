# Real agent runs

**Result: the skill pays where the agent has no cheap way of its own. A 12-page PDF costs 73% less, a long source file read whole about 33% less; on the other tasks no saving can be credited to the skill (the same within noise, or higher). The skill itself was almost never called: the savings come from the read hook.**

This report is different from the others: instead of estimating tokens on files, it launches a real agent on a task and records what the agent itself reports (usage, dollars, turns), with and without the skill. 295 calls in total, 294 with a correct answer.

## What was compared

- **Arms, in the same project, each seeing only the project settings (never the user's own skills or hooks):** *without* (nothing added), *skill* (the skill installed, no hook), *hooks* (the read hook registered, the skill not loaded) and *with* (skill and hook). The first comparison uses all four; later ones compare *without* and *with*.
- **What is recorded:** dollars, tokens (including cached reads), number of turns, what each turn did, whether the answer was right (an automatic check of the final answer). Dollars come from the agent's own report and are notional on a subscription plan. In the column *Against without*, positive means cheaper than without and negative means more expensive. Tokens are not compared because cached reads make them move the other way from dollars on some tasks.
- **Isolation check:** every call verifies that the skill is loaded exactly in the arms that have it; a call that cannot be executed (missing program, not logged in) aborts the run and is never counted. One pass was repeated because a permission setting stopped the agent's own shell; only the valid pass is reported.

## 1. Simple search tasks (release 1.0.0)

A planted failing line in a server log of 50, 500 and 5,000 lines; 3 repetitions per task and arm.

| Task | Arm | Dollars (median) | Against without | Turns | Success | Hook denials |
|---|---|---:|---:|---:|---:|---:|
| log-50 | without | 0.038 |  | 2 | 100% | 0.0 |
| log-50 | skill | 0.037 | +3% | 2 | 100% | 0.0 |
| log-50 | hooks | 0.044 | −15% | 3 | 100% | 1.0 |
| log-50 | with | 0.037 | +3% | 2 | 100% | 0.0 |
| log-500 | without | 0.038 |  | 2 | 100% | 0.0 |
| log-500 | skill | 0.037 | +2% | 2 | 100% | 0.0 |
| log-500 | hooks | 0.045 | −17% | 3 | 100% | 1.0 |
| log-500 | with | 0.037 | +2% | 2 | 100% | 0.0 |
| log-5000 | without | 0.038 |  | 2 | 100% | 0.0 |
| log-5000 | skill | 0.037 | +1% | 2 | 100% | 0.0 |
| log-5000 | hooks | 0.037 | +3% | 2 | 100% | 0.0 |
| log-5000 | with | 0.038 | 0% | 2 | 100% | 0.0 |

Total over the 9 calls of each arm: without 0.342, skill 0.337, hooks 0.376, with 0.338 dollars. In the 18 calls of the arms that have the skill there were 0 activations of the skill and 0 commands of the skill: the agent finds the line with one search at every size. The only harm was the read hook: on the two smaller logs the hook-only arm took one extra turn in all three repetitions, because the hook deviated a content search and the agent repeated it (+15% to +17%). The notice was removed in release 1.0.1; the same tasks before and after, hook-only arm against without (2 repetitions):

Before:

| Task | Arm | Dollars (median) | Against without | Turns | Success | Hook denials |
|---|---|---:|---:|---:|---:|---:|
| log-50 | without | 0.037 |  | 2 | 100% | 0.0 |
| log-50 | hooks | 0.044 | −19% | 3 | 100% | 1.0 |
| log-500 | without | 0.038 |  | 2 | 100% | 0.0 |
| log-500 | hooks | 0.037 | +2% | 2 | 100% | 0.0 |
| log-5000 | without | 0.037 |  | 2 | 100% | 0.0 |
| log-5000 | hooks | 0.037 | −1% | 2 | 100% | 0.0 |

After:

| Task | Arm | Dollars (median) | Against without | Turns | Success | Hook denials |
|---|---|---:|---:|---:|---:|---:|
| log-50 | without | 0.038 |  | 2 | 100% | 0.0 |
| log-50 | hooks | 0.038 | 0% | 2 | 100% | 0.0 |
| log-500 | without | 0.038 |  | 2 | 100% | 0.0 |
| log-500 | hooks | 0.038 | 0% | 2 | 100% | 0.0 |
| log-5000 | without | 0.037 |  | 2 | 100% | 0.0 |
| log-5000 | hooks | 0.039 | −5% | 2 | 100% | 0.0 |

## 2. Where reading is the cost (release 1.0.1)

Files the agent has to open, 3 repetitions per task and arm.

| Task | Arm | Dollars (median) | Against without | Turns | Success | Hook denials |
|---|---|---:|---:|---:|---:|---:|
| json-catalog | without | 0.036 |  | 2 | 100% | 0.0 |
| json-catalog | with | 0.037 | −3% | 2 | 100% | 0.0 |
| pdf-penalty | without | 0.207 |  | 3 | 100% | 0.0 |
| pdf-penalty | with | 0.054 | +74% | 5 | 100% | 1.0 |
| test-output | without | 0.060 |  | 5 | 100% | 0.0 |
| test-output | with | 0.063 | −5% | 5 | 100% | 0.0 |

- **PDF:** the agent's own read of a PDF loads the whole document. The hook rejects it, the agent converts it to Markdown and searches the result: two more turns, a quarter of the cost, correct 3 times out of 3.
- **JSON of about 200 KB and a 6,000-line test output:** the agent searches the file or filters the output on its own; nothing to save, the skill's text is a small extra cost.

## 3. Office documents and images (release 1.0.1)

| Task | Arm | Dollars (median) | Against without | Turns | Success | Hook denials |
|---|---|---:|---:|---:|---:|---:|
| docx-vacation | without | 0.050 |  | 4 | 100% | 0.0 |
| docx-vacation | with | 0.047 | +6% | 3 | 100% | 0.0 |
| image-ticket | without | 0.049 |  | 3 | 100% | 0.0 |
| image-ticket | with | 0.053 | −8% | 4 | 100% | 1.0 |
| xlsx-refund | without | 0.099 |  | 6 | 100% | 0.0 |
| xlsx-refund | with | 0.055 | +44% | 4 | 100% | 0.0 |

- **Word and Excel:** the agent opens both on its own with its shell and never calls `Read` on them, so the hook did not act (0 denials). The saving on the spreadsheet comes from a shorter path the agent chose in the *with* arm, not from the skill; it is reported because it is the literal comparison, and it is not a claim about the skill.
- **Image:** the hook rejected the read and the agent converted it and read it again: one more turn and −8% in dollars. The agent's own image read is already reduced. The block was removed in release 1.0.2 (see [what was tried and removed](removed.md)).

## 4. Long text files and sessions (release 1.0.1)

4 repetitions for the source file and the notes session; 3 for the HTML report session.

| Task | Arm | Dollars (median) | Against without | Turns | Success | Hook denials |
|---|---|---:|---:|---:|---:|---:|
| count-params | without | 0.089 |  | 3 | 100% | 0.0 |
| count-params | with | 0.059 | +34% | 4 | 100% | 0.5 |
| notes-session | without | 0.199 |  | 4 | 100% | 0.0 |
| notes-session | with | 0.200 | −1% | 4 | 100% | 0.0 |

| Session | Arm | Dollars (median) | Against without | Turns | Success | Hook denials |
|---|---|---:|---:|---:|---:|---:|
| html-session | without | 0.278 |  | 12 | 100% | 0.0 |
| html-session | with | 0.250 | +10% | 10 | 100% | 1.0 |

- **Long source file (1,100 lines, count the functions with more than 3 parameters):** the hook deviated the first whole read in 2 of 4 repetitions, and the agent wrote a short script instead of reading the file; in the other two the agent had already searched instead of reading. Correct every time, +34% in dollars.
- **380-line notes file, three questions in one session:** the file is under the cap, so the hook did not act; same cost.
- **330 KB HTML report, four questions in one session:** the agent's own read refuses a file this large, so in both arms it searched and read ranges; the saving (+10%) is two turns fewer, from the hook pointing at a range read at once instead of after a failed read.

## 5. Does the agent call the skill's own commands? (release 1.0.2)

Three tasks that invite them: a test run with 12,000 lines of output and three failures, a lockfile of 2,500 packages (count the dev dependencies), a log of 7,000 lines with four failure reasons. 3 repetitions per task; arms *without*, *skill* (installed, no hook) and *with*.

| Task | Arm | Dollars (median) | Against without | Turns | Success | Hook denials |
|---|---|---:|---:|---:|---:|---:|
| lock-count | without | 0.041 |  | 3 | 100% | 0.0 |
| lock-count | skill | 0.035 | +15% | 2 | 100% | 0.0 |
| lock-count | with | 0.042 | −1% | 3 | 100% | 0.0 |
| log-kinds | without | 0.051 |  | 3 | 100% | 0.0 |
| log-kinds | skill | 0.046 | +10% | 2 | 100% | 0.0 |
| log-kinds | with | 0.051 | +1% | 3 | 100% | 0.0 |
| tests-many | without | 0.055 |  | 4 | 100% | 0.0 |
| tests-many | skill | 0.056 | −1% | 4 | 100% | 0.0 |
| tests-many | with | 0.056 | −1% | 4 | 100% | 0.0 |

- **The agent never called the skill or any of its commands:** 0 activations and 0 commands in 18 calls of the arms that have the skill. It filtered the output with its own search, read the saved output file, or counted in the lockfile with a short script, for about $0.04 to $0.06 a task.
- **The differences between arms are the path the agent happened to choose** (for example fewer turns in the lockfile task of the *skill* arm), not the use of the skill: the skill was not used in them.

## 6. Fixed context: a bloated instruction file against the same facts trimmed

A project instruction file with the same 12 facts in three versions: trimmed (about 106 tokens), bloated to about 10,000 tokens and to about 40,000 tokens with repeated decisions and separators. One session of 5 questions that only the file can answer, 3 repetitions per version.

| Version | Dollars per session (median) | Turns | Context per turn | Success |
|---|---:|---:|---:|---:|
| trimmed (about 106 tokens) | 0.259 | 5 | 32,911 | 3/3 |
| bloated-10k (about 10,064 tokens) | 0.472 | 5 | 43,034 | 3/3 |
| bloated-40k (about 40,061 tokens) | 1.108 | 5 | 73,338 | 3/3 |

- **Every turn pays the fixed context again.** The 10,000-token file costs 82% more per session than the trimmed one, and the 40,000-token file about 4.3 times as much; all answers were correct.
- **Saving of trimming, with the skill's own cost charged** (its 76-token description paid on every turn at the rate this run implies, 0.0016 dollars per session): 44% from 10,000 tokens and 76% from 40,000 tokens, rounded down.
- **What this does and does not show.** It shows what the fixed context costs and what trimming it is worth. The trimming here was done by hand to the result the audit command points to (repetition and history removed, every fact kept); the agent did not trim anything, and a real file has facts that are harder to separate from the noise.

## 7. Can the agent trim the file by itself? (release 1.0.2)

The 10,000-token instruction file of section 6 in a project, with the request to reduce it as much as possible without losing a fact a future session would need; 3 repetitions in each of the arms *without* and *with* the skill.

| Arm | Dollars (median) | Turns | Size after | Facts kept | Skill commands called |
|---|---:|---:|---:|---:|---:|
| without | 0.087 | 2 | about 84 tokens | 12 of 12 | 0 |
| with | 0.087 | 2 | about 84 tokens | 12 of 12 | 0 |

- **The agent does it alone, in two turns, with or without the skill.** The instruction file is already in its context, so it rewrote it directly: about 84 tokens left, all 12 facts kept, 0.087 dollars. The skill was not called. Against the 0.213 dollars a 5-question session saves, the trimming pays for itself in the first session.
- **So the saving of section 6 is not the skill's work.** What the skill could add is noticing that the file is heavy before anyone asks (the audit command); that was not measured here.
- **Limit:** the bloat is pure repetition, which is the easiest case to trim without loss. A real file mixes obsolete and current rules, where losses are likelier.

## 8. The remaining mechanics (release 1.0.2)

Seven tasks, 4 repetitions per task and arm, three arms: *without*; *with* (skill and hooks installed, the agent decides, the literal comparison); *directed* (the same, and the prompt names the helper to use: an upper bound of what the mechanic can give, not what users get).

| Task | Arm | Dollars (median) | Against without | Turns | Success | Hook denials |
|---|---|---:|---:|---:|---:|---:|
| case-file | without | 0.059 |  | 5 | 100% | 0.0 |
| case-file | with | 0.059 | 0% | 5 | 100% | 0.0 |
| case-file | directed | 0.054 | +9% | 3 | 100% | 0.0 |
| continuity | without | 0.056 |  | 4 | 100% | 0.0 |
| continuity | with | 0.040 | +29% | 1 | 100% | 0.0 |
| continuity | directed | 0.047 | +17% | 2 | 100% | 0.0 |
| doc-index | without | 0.043 |  | 2 | 100% | 0.0 |
| doc-index | with | 0.043 | 0% | 2 | 100% | 0.0 |
| doc-index | directed | 0.049 | −14% | 3 | 100% | 0.0 |
| duplicates | without | 0.068 |  | 6 | 100% | 0.0 |
| duplicates | with | 0.056 | +17% | 3 | 100% | 0.0 |
| duplicates | directed | 0.045 | +34% | 2 | 100% | 0.0 |
| html-page | without | 0.197 |  | 9 | 100% | 0.0 |
| html-page | with | 0.062 | +68% | 4 | 100% | 1.0 |
| html-page | directed | 0.068 | +65% | 3 | 100% | 0.0 |
| inventory | without | 0.063 |  | 8 | 100% | 0.0 |
| inventory | with | 0.071 | −13% | 8 | 100% | 0.0 |
| inventory | directed | 0.057 | +9% | 3 | 100% | 0.0 |
| usage-search | without | 0.044 |  | 2 | 100% | 0.0 |
| usage-search | with | 0.045 | −1% | 2 | 100% | 0.0 |
| usage-search | directed | 0.045 | −1% | 2 | 100% | 0.0 |

- **HTML page of 3,000 lines (about 51,000 tokens):** +68% with the skill installed. The hook deviated the first whole read and the agent searched for the prices and read a range; it did not call the conversion (directed, which does call it: +65%).
- **Continuity note:** +29%. The note hook loads the note at the start of the session, so the agent answers in one turn; without it the agent reconstructs the state from the history and the files in 4 turns. The note holds exactly the facts asked about, so this is the best case for the mechanic.
- **Duplicated code:** +17% with the skill installed, though the agent did not call the helper (it chose a shorter reading path); +34% when it is told to use it.
- **Project inventory:** −13% with the skill installed (it costs more) and +9% directed.
- **Usage search, case file of a change, document index:** no effect with the skill installed (−1%, 0%, 0%); directed, −1%, +9% and −14%: the agent already has a cheap way of its own.
- **The agent called a helper on its own in none of the 28 calls of the arm *with*.**

### Strict diet profile

A 380-line notes file and a session of three questions; the strict profile deviates the first whole read of a file over 200 lines (the default profile does it over 400, so it does not act on this file).

| Session | Arm | Dollars (median) | Against without | Turns | Success | Hook denials |
|---|---|---:|---:|---:|---:|---:|
| notes-strict | without | 0.226 |  | 4 | 100% | 0.0 |
| notes-strict | with | 0.179 | +21% | 7 | 100% | 1.0 |

The strict profile costs 21% less on this session, with every answer correct.

### Delegating a search to a cheaper model

The same question answered directly and answered by telling the agent to delegate the search to a subagent on the light model (the delegation tool allowed in both arms). Four repetitions.

| Task | Arm | Dollars (median) | Against without | Turns | Success | Hook denials |
|---|---|---:|---:|---:|---:|---:|
| deleg-large | without | 0.044 |  | 2 | 100% | 0.0 |
| deleg-large | directed | 0.052 | −18% | 2 | 100% | 0.0 |
| deleg-medium | without | 0.043 |  | 2 | 75% | 0.0 |
| deleg-medium | directed | 0.056 | −29% | 1 | 100% | 0.0 |
| deleg-small | without | 0.047 |  | 3 | 100% | 0.0 |
| deleg-small | directed | 0.048 | −2% | 2 | 100% | 0.0 |

| Task | Arm | Dollars (median) | Against without | Turns | Success | Hook denials |
|---|---|---:|---:|---:|---:|---:|
| deleg-heavy-14 | without | 0.069 |  | 5 | 100% | 0.0 |
| deleg-heavy-14 | directed | 0.069 | −1% | 1 | 100% | 0.0 |
| deleg-heavy-4 | without | 0.108 |  | 6 | 100% | 0.0 |
| deleg-heavy-4 | directed | 0.061 | +44% | 1 | 100% | 0.0 |

- Delegation did not pay consistently: on the three searches it gave −2%, −29% and −18%, and on the two tasks that need several files read, −1% (14 files) and +44% (4 files). The agent's own search already returns little, so the fixed cost of a subagent is not recovered; the one clear gain came from a small task that obliged reading several files, and it did not repeat with more files.
- A numeric threshold could not be derived from these sizes: no task gave a consistent saving.

## What it shows

1. **The skill does not help on small tasks and does not cost either.** Its description is below the noise in every task.
2. **It helps where the agent's native way is expensive:** a PDF read whole, a long file read whole.
3. **It does not help where the agent already has a cheap way:** searching a file, filtering command output, counting in a lockfile, reading an image, opening Word or Excel with its shell. Even when the task invites the skill's commands, the agent does not call them.
4. **The fixed context is where the bill grows:** every turn pays it again, and trimming a bloated instruction file is worth 44% to 76% of a session's cost in section 6.
5. **Mechanics that did not pay were removed** (releases 1.0.1 and 1.0.2), see [what was tried and removed](removed.md).

## Evidence

| Field | Value |
|---|---|
| Basis of the result | measured: real agent runs, paired by task and repetition |
| Basis of the figures | provider_reported: usage, dollars and turns as the agent reports them; dollars are not an invoice |
| Inputs (first 10 characters of the SHA-256 of the planted files) | log-50 a42d13a58a, log-500 6ed55985ee, log-5000 bb9851a2db, json-catalog 67b2fd5f4f, pdf-penalty e3b0c44298, test-output 47939586e9, xlsx-refund e3b0c44298, docx-vacation e3b0c44298, image-ticket e3b0c44298, count-params 1c5a2c7f7a, notes-session 651e1ea3ae, tests-many 1c8a5e4d07, lock-count 309c866e74, log-kinds 4ffd6f2883 |
| Skill releases | 1.0.0 for section 1 (before); 1.0.1 for the rest and the after of section 1 |
| Quality check | 294 of 295 calls correct |
| Failures and excluded cases | no call was excluded; a run that could not execute was aborted and repeated |
| Price | list prices are not applied; dollars are the agent's own figure |
| Scope | small synthetic tasks with a planted answer, one agent version and its default model; they do not extend to other file contents or to very long sessions |

## Limits

- Few repetitions (3 or 4) and medians: differences of a few percent are noise, and a single run can take a different path (the spreadsheet saving is an example).
- One example of each kind of file: a text PDF without tables or images, a plain Word document, a spreadsheet of one sheet, one image, one lockfile, one test output.
- Success was 100% in every arm for every task of sections 2 to 4, so these runs cannot show a drop in quality beyond what the checks cover.
