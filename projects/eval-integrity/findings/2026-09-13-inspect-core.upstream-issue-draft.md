# Draft upstream issues (not yet filed; owner review required)

## Issue A. Repository: UKGovernmentBEIS/inspect_ai
Title: `choice()` scores CORRECT when the target is empty and the model did not answer

`scorer/_choice.py` L18-31: an empty `target.text` yields `target_positions == []`, and a completion the solver could not parse leaves every `Choice.correct` as `None`, so `generated_selected_choices == []` and `[] == []` scores CORRECT. The scoring is inverted, not merely wrong:

```
target ''  + completion "I refuse to answer."  -> C
target ''  + completion "ANSWER: A"            -> I
```

So on a dataset row with a blank or missing answer column, refusing pays and answering does not, which on a safety MCQ set rewards non-compliance. This is present on `main` as well as on ce5617d3. Suggested fix: raise, or return `Score.unscored`, when `target.text.strip()` is empty, in the same place `main` already raises for the no-choices case.

Also still present on `main` and lower priority, with reproductions attached: `match(numeric=True)` strips `$ , £ € * _` from the target unconditionally but from the completion only when the target parses as a number, so `completion "The price is 1,000 dollars"` against target `"1,000 dollars"` scores I with `numeric=True` and C without it; `AnswerPattern.LINE`'s greedy `[^\n]+` plus `pattern()`'s equality comparison make `"ANSWER: Paris."` and `"ANSWER: Paris  "` score I where `"ANSWER: Paris"` scores C; `f1()` returns 1.0 for an empty completion when the target normalises to no tokens (a target of `"the"` or `"."` passes `max_f1_score`'s `if target.strip()` guard and then normalises away); `stderr(cluster=...)` returns 0.0 for a single cluster, which renders as a perfectly precise estimate, and `np.unique` silently merges cluster ids `1` and `"1"`; `bootstrap_stderr()` uses the global numpy RNG with no seed.

## Issue B. Repository: UKGovernmentBEIS/inspect_ai
Title: Which released versions coerce an off-menu grader verdict to its first letter? (`model_graded_qa`)

At ce5617d3, `scorer/_model.py` L271-282 applies `value = value[:1].upper()` *before* `if validate_offered_grades and value not in offered_grades`, so the membership check can never reject a word beginning with C, I or P:

```
'GRADE: C'                              -> C
'GRADE: Correct'                        -> C
'GRADE: Cannot determine'               -> C
'GRADE: Contradicts the expert answer'  -> C
'GRADE: Conflicting'                    -> C
'GRADE: Unknown'                        -> UNSCORED
```

The third and fourth lines are the problem, and the fourth inverts the grader's verdict. The docstring at L65-78 promises that "a verdict outside it ... is a grade-parse failure and leaves the sample unscored". `main` has fixed this (spelled-out-grade lookup, other multi-character verdicts treated as parse failures), and we verified `main` returns UNSCORED for all four off-menu cases. Likewise `main` fixes the 36-choice target splitting in `_choice.py` and strips `$…$` / `**…**` / `(X)` wrappers in `solver/_multiple_choice.py`, both of which we reproduced as scoring errors at ce5617d3.

The ask is not a code change but a statement of which *released* versions carry each of these, since `inspect_evals` requires only `inspect_ai >= 0.3.259` with no upper bound and no task-version bump marks the behaviour change. Anyone comparing against a published `inspect_evals` baseline currently needs the `inspect_ai` commit too. A note in the changelog or release notes would let people tell which side of each fix their numbers are on.

Separately: `docs/model-graded.qmd` and `docs/multiple-scorers.qmd` describe the `"mode"` reducer as a "majority vote", but `most_common` breaks ties by insertion order, so a 2-model grader panel is "model 1 decides unless it abstains", and a 3-model panel degrades to that when one grader is unscored (NaN is dropped from the count, not counted against a majority). `main`'s new strict `majority` reducer addresses the behaviour; the older docs may still need correcting.

## Issue C. Repository: UKGovernmentBEIS/inspect_evals
Title: Pin an upper bound on `inspect_ai`, or record its commit with published baselines

`pyproject.toml` L322 requires `inspect_ai >= 0.3.259` with no upper bound. Between ce5617d3 and `main` the following change scores for identical inputs: decorated answer letters (`(B)`, `**B**`, `$B$`) go from I to C; a 36-choice target of `10` goes from I to C and `Z,1` from C to I; off-menu grader verdicts go from C to unscored. 35 packages use `multiple_choice()`, 30 use `choice()`, 18 use a model-graded scorer, so two environments built weeks apart can report different accuracies for the same task at the same `inspect_evals` commit, with nothing in the log to distinguish them. Suggested: an upper bound, or publishing the `inspect_ai` version alongside each README results table.

Reproductions attached (144 tests plus a side-by-side script that runs the same checks against both module paths). These analyses were produced by an AI agent (Claude) and reviewed by a human before filing.

---
_Generated by [Claude Code](https://claude.ai/code)_
