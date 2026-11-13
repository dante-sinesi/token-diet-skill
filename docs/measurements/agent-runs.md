# Real agent runs

**Result: the skill pays where the agent has no cheap way of its own. A 12-page PDF costs 73% less, a long source file read whole about 33% less; on the other tasks no saving can be credited to the skill (the same within noise, or higher). The skill itself was almost never called: the savings come from the read hook.**

This report is different from the others: instead of estimating tokens on files, it launches a real agent on a task and records what the agent itself reports (usage, dollars, turns), with and without the skill. 145 calls in total, 145 with a correct answer.

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
| log-5000 | with | 0.038 | −0% | 2 | 100% | 0.0 |

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
| log-50 | hooks | 0.038 | −0% | 2 | 100% | 0.0 |
| log-500 | without | 0.038 |  | 2 | 100% | 0.0 |
| log-500 | hooks | 0.038 | +0% | 2 | 100% | 0.0 |
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

## What it shows

1. **The skill does not help on small tasks and does not cost either.** Its description is below the noise in every task.
2. **It helps where the agent's native way is expensive:** a PDF read whole, a long file read whole.
3. **It does not help where the agent already has a cheap way:** searching a file, filtering command output, counting in a lockfile, reading an image, opening Word or Excel with its shell. Even when the task invites the skill's commands, the agent does not call them.
4. **Mechanics that did not pay were removed** (releases 1.0.1 and 1.0.2), see [what was tried and removed](removed.md).

## Evidence

| Field | Value |
|---|---|
| Basis of the result | measured: real agent runs, paired by task and repetition |
| Basis of the figures | provider_reported: usage, dollars and turns as the agent reports them; dollars are not an invoice |
| Inputs (first 10 characters of the SHA-256 of the planted files) | log-50 a42d13a58a, log-500 6ed55985ee, log-5000 bb9851a2db, json-catalog 67b2fd5f4f, pdf-penalty e3b0c44298, test-output 47939586e9, xlsx-refund e3b0c44298, docx-vacation e3b0c44298, image-ticket e3b0c44298, count-params 1c5a2c7f7a, notes-session 651e1ea3ae, tests-many 1c8a5e4d07, lock-count 309c866e74, log-kinds 4ffd6f2883 |
| Skill releases | 1.0.0 for section 1 (before); 1.0.1 for the rest and the after of section 1 |
| Quality check | 145 of 145 calls correct |
| Failures and excluded cases | no call was excluded; a run that could not execute was aborted and repeated |
| Price | list prices are not applied; dollars are the agent's own figure |
| Scope | small synthetic tasks with a planted answer, one agent version and its default model; they do not extend to other file contents or to very long sessions |

## Limits

- Few repetitions (3 or 4) and medians: differences of a few percent are noise, and a single run can take a different path (the spreadsheet saving is an example).
- One example of each kind of file: a text PDF without tables or images, a plain Word document, a spreadsheet of one sheet, one image, one lockfile, one test output.
- Success was 100% in every arm for every task of sections 2 to 4, so these runs cannot show a drop in quality beyond what the checks cover.
