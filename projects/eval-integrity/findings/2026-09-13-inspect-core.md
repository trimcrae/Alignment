# Inspect's own scoring primitives: a grader verdict of "Cannot determine" or "Contradicts the expert answer" scores as CORRECT, and an empty target credits a refusal

```
Target:            UKGovernmentBEIS/inspect_ai, the scoring primitives every eval depends on (scorer/, solver/_multiple_choice.py)
Version:           0.3.260.dev154, a verified git build of commit ce5617d3, as installed in the eval library's environment; compared against upstream main at f6719bb
Defect classes:    4 (judge and answer parsing), 1 (scorer exploitability), 9 (metrics), 10/3 (versioning and reproducibility)
Reproduction:      repro/inspect_core/ (144 tests, all pass, rerun in this session; they assert the observed behaviour so they also serve as a tripwire when it is fixed)
Severity:          high for items 1 to 3; medium for items 4 to 6
Confidence:        high (each item verified by reading the source and by running the reproductions; I also re-derived item 1's resolution logic independently)
Disclosure:        drafted 2026-09-13; awaiting repo-owner review. Items 1, 3 and 4 are already fixed on upstream main, so the useful report is which released versions are affected; items 2, 5 and 6 are still present on main.
Why it matters:    In the eval library, 18 packages use the model-graded scorers, 35 use the multiple-choice solver, 30 use the choice scorer, and 26 use the text matcher. A defect here moves all of those numbers at once.
Full audit:        2026-09-13-inspect-core-full-audit.md (agent report, 14 items plus a list of documented-but-surprising behaviour)
```

## Verified findings

1. **The model-graded scorers truncate the grader's verdict to its first letter before validating it, so any verdict beginning with C is scored CORRECT.** In `scorer/_model.py` the permissive default pattern captures a whole word, then the code does `value = value[:1].upper()` and only afterwards checks membership in the offered grades. The check can therefore never reject a word starting with C, I or P. Verified by re-deriving the logic against the installed source: "GRADE: Cannot determine", "GRADE: Contradicts the expert answer" and "GRADE: Conflicting" all resolve to CORRECT, while "GRADE: Unknown" is correctly rejected. The second of those is an outright inversion, since a grader saying the submission contradicts the expert answer is scored as a correct answer. The function's own docstring promises the opposite, stating that a verdict outside the offered set "is a grade-parse failure and leaves the sample unscored". Direction is strictly upward on measured capability and compliance. Fixed on upstream main, which looks up spelled-out grades and treats any other multi-character verdict as a parse failure.

2. **The choice scorer scores CORRECT when the target is empty and the model did not answer.** An empty target produces no target positions, and a completion that does not parse leaves no choice marked correct, so an equality test between two empty lists succeeds. The scoring is inverted rather than merely wrong: with a blank target, refusing scores CORRECT and answering scores INCORRECT. There is no guard, warning, or unscored path. Still present on upstream main. Any dataset row with a missing answer column becomes a free point for refusals, which on a safety multiple-choice set rewards non-compliance.

3. **The choice scorer splits multi-character numeric targets one character at a time,** so a task with 36 or more choices mis-scores in both directions: the correct answer at index 35 is marked wrong, and one specific wrong pair is credited instead. The solver side handles these targets correctly, so only the scorer disagrees. Fixed on upstream main, which tokenises first and raises on out-of-range targets.

4. **The multiple-choice solver rejects the decorated answer formats models actually emit.** Bold, parenthesised, and dollar-delimited letters all fail to parse, and the sample is then scored INCORRECT rather than unscored, so it stays in the denominator at zero. The prompt template itself uses a dollar-sign placeholder, which invites one of the rejected forms. The bias is downward and uneven across models, since a model that bolds its answer can lose everything while one that does not loses nothing, which makes cross-model comparisons on the 35 affected packages unsafe. Fixed on upstream main.

5. **The reducer documented as a majority vote is a plurality with declaration-order tie-breaking.** Three separate documentation passages call it a majority vote. With two graders it is not a vote at all but "the first grader decides unless it abstains", because ties break by insertion order; with three graders it degrades to that whenever one grader fails to parse, since an unscored grader is dropped from the count rather than withholding a vote. Upstream main adds a strict majority reducer and makes it the default for grader panels.

6. **Version drift with no pin and no version bump.** The eval library requires the framework at or above one version with no upper bound, and the two commits I compared disagree on scoring for the same inputs: decorated letters, 36-choice targets, and off-menu grader verdicts all score differently. Two runs of the same eval at the same library commit, in environments built weeks apart, can produce different accuracies with nothing in the log to distinguish them beyond the framework version string.

Lower-severity items in the full audit: a target that is not a bare letter silently scores zero rather than raising, which is the failure most easily mistaken for a weak model; the numeric matcher strips punctuation from the target but not the completion when the target is not itself numeric, so an identical answer cannot match; the line-answer pattern is broken by a trailing full stop or trailing spaces; the F1 scorer returns a perfect score for an empty completion when the target normalises to no tokens; the clustered standard error reports zero for a single cluster and silently merges cluster identifiers that differ only by type; the bootstrap standard error is unseeded; and a helper for un-shuffling overwrites the model's real completion, including its reasoning, contrary to its own docstring.

## Documented but worth knowing

The text matcher defaults to a suffix test on raw text, so a completion ending in the target's characters is credited; the any-location matcher and the substring scorer credit a completion that lists every option; and a no-answer verdict counts as zero in the denominator, so refusals and format failures are indistinguishable from wrong answers in accuracy. All three are documented, and the last is the reason a refusal-heavy model can look merely inaccurate.

## Proposed fixes

For the maintainers: validate the grader's verdict before truncating it, or adopt the upstream fix and tell users which released versions are affected; raise or return unscored when the choice target is empty; and carry the upstream tokenisation and decoration-stripping fixes into a release. For the eval library: pin an upper bound on the framework version, or record the framework commit alongside each published baseline, because otherwise no published number is reproducible.
