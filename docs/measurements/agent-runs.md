# Real agent runs: simple tasks

**Result: on simple tasks the skill costs the same as not having it (within 3%), and it was not used. One real defect was found in the read hook, measured and fixed in release 1.0.1.**

This report is different from the others: instead of estimating tokens on files, it launches a real agent on a task and records what the agent itself reports (usage, dollars, turns), with and without the skill.

## What was compared

- **Task:** "in a server log, which order failed and why?" with the failing line planted in the middle of a log of 50, 500 and 5,000 lines. The answer is checked automatically.
- **Arms, in the same project, each seeing only the project settings (never the user's own skills or hooks):**
  - *without:* nothing is added;
  - *skill:* the skill is installed, no hook runs;
  - *hooks:* the read hook is registered, the skill is not loaded;
  - *with:* skill and hook.
- **Repetitions:** 3 per task and arm (36 calls) for the full comparison; 2 per task for the before and after of the fix.
- **What is recorded:** dollars, tokens (including cached reads), number of turns, what each turn did, whether the answer was right. Dollars come from the agent's own report and are notional on a subscription plan. In the column *Against without*, positive means cheaper than without and negative means more expensive.
- **Isolation check:** every call verifies that the skill is loaded exactly in the arms that have it; a call that cannot be executed (missing program, not logged in) aborts the run and is never counted.

## Full comparison (release 1.0.0)

| Task | Arm | Dollars (median) | Against without | Turns | Success | Hook denials |
|---|---|---:|---:|---:|---:|---:|
| log-50 | without | 0.038 |  | 2 | 100% | 0 |
| log-50 | skill | 0.037 | +3% | 2 | 100% | 0 |
| log-50 | hooks | 0.044 | −15% | 3 | 100% | 1 |
| log-50 | with | 0.037 | +3% | 2 | 100% | 0 |
| log-500 | without | 0.038 |  | 2 | 100% | 0 |
| log-500 | skill | 0.037 | +2% | 2 | 100% | 0 |
| log-500 | hooks | 0.045 | −17% | 3 | 100% | 1 |
| log-500 | with | 0.037 | +2% | 2 | 100% | 0 |
| log-5000 | without | 0.038 |  | 2 | 100% | 0 |
| log-5000 | skill | 0.037 | +1% | 2 | 100% | 0 |
| log-5000 | hooks | 0.037 | +3% | 2 | 100% | 0 |
| log-5000 | with | 0.038 | −0% | 2 | 100% | 0 |

Total over the 9 calls of each arm: without 0.342, skill 0.337, hooks 0.376, with 0.338 dollars.

## What it shows

1. **The skill was never used.** In the 18 calls of the arms that have it there were 0 activations of the skill and 0 Token Diet commands. The agent solved every task in 2 turns with one search, at every size, with 100% success.
2. **The fixed cost is small.** The agent's own context is about 58,000 cached tokens per turn (0.037 dollars per call). The description of the skill (about 79 tokens) is below the noise: with the skill and without it the cost is within 3%. One extra turn costs about 0.007 dollars here.
3. **The only harm was the hook.** On the two smaller logs the hook-only arm took exactly one extra turn in all three repetitions: the hook deviated a content search without a limit, and the agent repeated the same search. That is +15% to +17% in dollars for nothing gained.
4. **No break-even was found**, because at these sizes the agent never needs to read the file: a search finds the line. A cheaper way to read cannot save when nothing is read. This run does not say what happens on tasks where reading is the cost.

## The decision and the check

The notice on content searches was removed in release 1.0.1. The same tasks, before and after, in the hook-only arm against without:

Before (release 1.0.0):

| Task | Arm | Dollars (median) | Against without | Turns | Success | Hook denials |
|---|---|---:|---:|---:|---:|---:|
| log-50 | without | 0.037 |  | 2 | 100% | 0 |
| log-50 | hooks | 0.044 | −19% | 3 | 100% | 1 |
| log-500 | without | 0.038 |  | 2 | 100% | 0 |
| log-500 | hooks | 0.037 | +2% | 2 | 100% | 0 |
| log-5000 | without | 0.037 |  | 2 | 100% | 0 |
| log-5000 | hooks | 0.037 | −1% | 2 | 100% | 0 |

After (release 1.0.1):

| Task | Arm | Dollars (median) | Against without | Turns | Success | Hook denials |
|---|---|---:|---:|---:|---:|---:|
| log-50 | without | 0.038 |  | 2 | 100% | 0 |
| log-50 | hooks | 0.038 | −0% | 2 | 100% | 0 |
| log-500 | without | 0.038 |  | 2 | 100% | 0 |
| log-500 | hooks | 0.038 | +0% | 2 | 100% | 0 |
| log-5000 | without | 0.037 |  | 2 | 100% | 0 |
| log-5000 | hooks | 0.039 | −5% | 2 | 100% | 0 |

After the fix no call had a denial and the cost matches the arm without the hook, within noise (2 repetitions).

## Evidence

| Field | Value |
|---|---|
| Basis of the result | measured: real agent runs, paired by task and repetition |
| Basis of the figures | provider_reported: usage, dollars and turns as the agent reports them; dollars are not an invoice |
| Inputs | planted logs, fingerprints (first 10 characters of the SHA-256): log-50 a42d13a58a, log-500 6ed55985ee, log-5000 bb9851a2db |
| Skill releases | 1.0.0 for the full comparison and the before; 1.0.1 for the after |
| Quality check | automatic check of the final answer: 36 of 36 correct in the full comparison; 12 of 12 before and 12 of 12 after |
| Failures and excluded cases | none excluded; no call was aborted |
| Price | list prices are not applied; dollars are the agent's own figure |
| Scope | one task type (a needle in a log), one agent version and its default model; it does not extend to tasks where reading is the cost |

## Limits

- Few repetitions (3 and 2), medians; differences of a few percent are noise.
- One kind of task, and the easiest one for a plain search. It says nothing about HTML pages, large structured files or long test output, where the skill is meant to help.
- Success was 100% in every arm, so this run cannot show a drop in quality.
