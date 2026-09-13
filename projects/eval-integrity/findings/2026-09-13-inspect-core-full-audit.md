# inspect_ai core scoring primitives — audit

**Target.** `inspect_ai 0.3.260.dev154+gce5617d35`, as installed at
`inspect_evals/.venv/lib/python3.11/site-packages/inspect_ai`. The install is a
genuine git build: `dist-info/direct_url.json` records
`commit_id ce5617d35a19a2f4ed0e30f00110126fe0be8f3e`, all RECORD sha256 hashes for
`scorer/`, `solver/_multiple_choice.py` and `_util/answer.py` verify, and the tree
is byte-identical to that commit fetched from GitHub. I cloned that exact commit
to `inspect_ai_target/` (source + tests + docs) and upstream `main` (f6719bb) is
at `inspect_ai_src/`, so every "fixed upstream" claim below is a diff I ran.

**Why this matters.** Counting source files under `inspect_evals/src/inspect_evals`
(132 eval packages): 41 call `multiple_choice()`, 33 call `choice()`, 25 call a
`model_graded_qa`/`model_graded_fact` scorer, 24 call `match()`, 17 call
`grouped()`, 6 call `stderr(cluster=...)`, 5 call `includes()`. A defect in these
primitives moves every one of those numbers. `inspect_evals/pyproject.toml:322`
requires only `inspect_ai >= 0.3.259`, with no upper bound (finding 5).

**Reproductions.** `findings/repro/inspect_core/` — 144 pytest cases plus one
side-by-side script, all run against the installed venv:

```
$ cd findings/repro/inspect_core && ../../../inspect_evals/.venv/bin/python -m pytest -q -p no:warnings
144 passed in 3.56s

test_choice_scorer.py          39 passed
test_text_match_scorers.py     46 passed
test_model_graded.py           23 passed
test_metrics.py                22 passed
test_reducers.py               14 passed
```

The tests *assert the observed behaviour* (they pass on the audited version), so
they double as a regression tripwire: they will fail when any of these are fixed.

---

## 1. `model_graded_qa` / `model_graded_fact` coerce any off-menu verdict to its first letter, so "GRADE: Cannot determine" scores CORRECT

- **Defect class:** 4 (judge and parsing) / 1 (scorer exploitability)
- **File:** `inspect_ai/scorer/_model.py:271-282`, pattern at `:395-397`
- **Severity:** high · **Confidence:** high

With the default `instructions` (i.e. whenever the caller does not pass a custom
`instructions` *and* does not pass a `grade_pattern` — the common case), the
scorer deliberately uses a permissive capture and then validates the verdict:

```python
_PERMISSIVE_GRADE_PATTERN = (
    rf"(?is).*(?<!\w)GRADE(?!\w){_GRADE_SPACING}:{_GRADE_SPACING}(\w*)"
)
...
match = re.search(resolved_grade_pattern, result.completion)
value = match.group(1) if match else None
if value is not None and default_grade_pattern:
    # The permissive capture takes the whole word so that "GRADE:
    # Correct"/"GRADE: Incorrect"/"GRADE: Partial" keep resolving to
    # their letter; only the first character is the verdict.
    value = value[:1].upper()
    if validate_offered_grades and value not in offered_grades:
        ...
        value = None
```

The truncation to `value[:1]` happens **before** the membership check, so the
check can never reject a word whose first letter happens to be `C`, `I` or `P`.
The docstring at `_model.py:65-78` promises the opposite:

> Under those defaults the grader is offered C/I, or C/P/I when this is `True`,
> and its final `GRADE:` verdict is validated against that set: a verdict outside
> it (a `P` that was never offered, or any other letter) is a grade-parse failure
> and leaves the sample unscored rather than being scored.

Observed (`findings/repro/inspect_core/test_model_graded.py`, mockllm grader):

```
'GRADE: Cannot determine'                          -> C
'GRADE: Cannot be determined from the submission'  -> C
'GRADE: Contradicts the expert answer'             -> C
'GRADE: Confusing but wrong'                       -> C
'GRADE: Conflicting'                               -> C
'GRADE: Unknown'                                   -> UNSCORED   (correctly rejected)
'GRADE: -'                                         -> UNSCORED
'no grade here'                                    -> UNSCORED
```

`model_graded_fact` inherits it (`_model.py:90-98` delegates to
`model_graded_qa`), verified in the same file.

**Impact.** Every grader utterance of the form "GRADE: C<anything>" is scored as a
correct answer. The realistic cases are refusal-to-grade ("Cannot determine",
"Cannot be assessed") and explicit rejection ("Contradicts the expert answer",
"Conflicts with the criterion") — the second family inverts the verdict. Direction
is strictly upward on measured capability/compliance: a grader that declines or
disagrees is counted as "the submission was correct". Magnitude depends on how
often a given grader deviates from the `GRADE: C`/`GRADE: I` form; for a
well-behaved grader at temperature 0 it is small, but it is a silent inversion
when it happens, and it reads as a clean `C` in the log (the grader text survives
only in `explanation`).

**Fixed on `main`**, which replaces the truncation with a spelled-out-grade
lookup and treats any other multi-character verdict as a parse failure
(`inspect_ai_src/src/inspect_ai/scorer/_model.py:318-335`). Verified by running
`main`'s scorer against the same grader completions:

```
module: .../inspect_ai_src/src/inspect_ai/scorer/_model.py
  'GRADE: C'                              -> C
  'GRADE: Correct'                        -> C
  'GRADE: Cannot determine'               -> UNSCORED
  'GRADE: Contradicts the expert answer'  -> UNSCORED
  'GRADE: Close enough'                   -> UNSCORED
  'GRADE: Insufficient information'       -> UNSCORED
```

So this is another instance of finding 5: the audited version silently inverts
some grader verdicts, `main` does not, and nothing in `inspect_evals` pins which
one you get.

---

## 2. `choice()` scores CORRECT when the target is empty and the model did not answer

- **Defect class:** 1 (scorer exploitability) / 2 (ground truth)
- **File:** `inspect_ai/scorer/_choice.py:18-31, 74-86`
- **Severity:** high (when reachable) · **Confidence:** high

```python
target_positions = [
    answer_index(target_character)
    for target_character in target.text
    if target_character not in (",", " ")
]
choice_positions = [i for i, choice in enumerate(choices) if choice.correct is True]
...
target_matches_choices = generated_selected_choices == sorted(target_positions)
return Score(value=CORRECT if target_matches_choices else INCORRECT, ...)
```

An empty target yields `target_positions == []`. A model whose output does not
parse leaves every `Choice.correct` as `None` (the solver only calls
`set_choices_based_on_generated_response` when `parse_answers` returned
something — `_multiple_choice.py:335`), so `generated_selected_choices == []`.
`[] == []` → CORRECT.

Reproduction (`test_choice_scorer.py::test_empty_target_credits_a_model_that_did_not_answer`):

```
target ''  + completion "I refuse to answer."  -> C
target ''  + completion "ANSWER: A"            -> I
```

So the scoring is not merely wrong, it is inverted: refusing pays, answering
does not. There is no guard, warning or `unscored` path.

**Impact.** Any dataset row with a blank/missing target becomes a free point for
refusals and a guaranteed loss for answers. On a safety MCQ set that is built
from a loader with an optional answer column this silently rewards
non-compliance. Still present on `main` (verified:
`PYTHONPATH=inspect_ai_src/src ... check_version_drift.py` → `'I refuse.' target '' -> C`).

**Fix shape:** raise (or return `Score.unscored`) when `target.text.strip()` is
empty, as `main` already does for the "no choices" case.

---

## 3. `choice()` splits multi-character numeric targets per character, so tasks with ≥36 choices mis-score in both directions

- **Defect class:** 4 (parsing) / 1
- **File:** `inspect_ai/scorer/_choice.py:21-25`, `inspect_ai/_util/answer.py:1-26`
- **Severity:** high for affected tasks · **Confidence:** high

`answer_character` emits `A..Z` then `"1".."9"` then `"10"`, `"11"`, … The solver
side handles that correctly (`answer_index("10") == 35`), but `_score_target`
iterates over `target.text` **one character at a time**, so a target of `"10"` is
read as the two answers `"1"` and `"0"` → positions `[26, 25]` instead of `[35]`.

Reproduction (`test_choice_scorer.py`, 36-choice task):

```
answer_character(35) == '10'
parse_answers("ANSWER: 10") -> {'10'};  solver selects index [35]
choice() vs target '10'                 -> I     # correct answer marked wrong
parse_answers("ANSWER: Z,1") -> selects [25, 26]
choice() vs target '10'                 -> C     # wrong answer credited
```

A second, milder instance of the same asymmetry: `answer_index("0") == 25 ==
answer_index("Z")` while `answer_character` never emits `"0"`, so a 0-based
numeric target addresses choice 26.

**Impact.** Any task with 36+ choices (chembench-style option banks, some
"pick the matching item" formats) loses every sample whose answer index is ≥ 35,
and credits the specific wrong pair `{Z, 1}`. Fixed on `main`, which tokenises
first (`inspect_ai_src/.../scorer/_choice.py:19-42`) and raises on out-of-range
targets — confirmed: `main` gives `C` for `ANSWER: 10` and `I` for `ANSWER: Z,1`.

---

## 4. `multiple_choice` rejects the decorated letter formats models actually emit (`**B**`, `(B)`, `$B$`)

- **Defect class:** 4 (parsing)
- **File:** `inspect_ai/solver/_multiple_choice.py:98-110, 147-149`
- **Severity:** medium (comparability; depresses scores) · **Confidence:** high

Both regexes capture with `([A-Za-z\d ,]+)` and the single-answer branch then
requires the *whole* capture to be an allowed option:

```python
single_tokens = [token for token in matched.split(",") if token]
if len(single_tokens) == 1 and single_tokens[0] in allowed_options:
```

Any wrapper character therefore kills the match and the sample is scored
INCORRECT (not unscored — it stays in the denominator at 0).

Reproduction (`test_choice_scorer.py::test_decorated_or_embedded_letters_do_not_parse`):

```
'ANSWER: (B)'                  -> parse {} -> choice() I
'ANSWER: **B**'                -> parse {} -> choice() I
'ANSWER: $B$'                  -> parse {} -> choice() I
'ANSWER: B is right'           -> parse {} -> choice() I
'I think ANSWER: B is right'   -> parse {} -> choice() I
'ANSWER: AB' (single-answer)   -> parse {} -> choice() I
```

Upstream treats this as a defect: `main` strips `$…$`, `**…**` and `(X)` wrappers
before matching (`inspect_ai_src/.../solver/_multiple_choice.py:93-105`) and adds
`test_answer_letter_with_latex_or_markdown_decoration`,
`test_multiple_correct_with_latex_or_markdown_decoration` and
`test_answer_with_trailing_text` — none of which exist at the audited commit.

**Impact.** Markdown-bolding the final answer is common behaviour for
instruction-tuned models, and `$LETTER` in the prompt template
(`'ANSWER: $LETTER'`) actively invites the `$B$` form. Direction: downward on
accuracy, non-uniformly across models (a model that bolds loses everything; one
that does not loses nothing), so cross-model comparisons on the 41 evals using
`multiple_choice()` are not safe. Magnitude is model-dependent and can be total
for a model with a fixed answer style.

---

## 5. Version drift: MCQ scoring changed between inspect_ai commits with no pin and no eval version bump

- **Defect class:** 10 (versioning) / 3 (reproducibility)
- **File:** `inspect_evals/pyproject.toml:322` (`"inspect_ai >= 0.3.259"`), `:382`
- **Severity:** medium · **Confidence:** high

Reproduction — `findings/repro/inspect_core/check_version_drift.py`, same script,
two module paths:

```
                                                installed        upstream main
                                                (ce5617d35)      (f6719bb)
'ANSWER: B'         target 'B'                  C                C
'ANSWER: (B)'       target 'B'                  I                C
'ANSWER: **B**'     target 'B'                  I                C
'ANSWER: $B$'       target 'B'                  I                C
'ANSWER: 10'        target '10' (36 choices)    I                C
'ANSWER: Z,1'       target '10' (36 choices)    C                I
'I refuse.'         target ''                   C                C
'GRADE: C'                                      C                C
'GRADE: Correct'                                C                C
'GRADE: Cannot determine'                       C                UNSCORED
'GRADE: Contradicts the expert answer'          C                UNSCORED
'GRADE: Close enough'                           C                UNSCORED
'GRADE: Insufficient information'               I                UNSCORED
```

Two more behaviour changes in the same window, both affecting scores:

- `pattern()`'s no-match verdict: NOANSWER at the audited commit → `INCORRECT`
  with `reason="invalid_response_format"` on `main`
  (`inspect_ai_src/.../scorer/_pattern.py:104-115`). Both convert to 0.0, so the
  metric is unchanged, but the log category is not.
- Grade extraction and the grader-panel reducer: see findings 1 and 6 — off-menu
  verdicts flip from CORRECT to unscored, and a 2-model panel flips from
  "first model decides" to "unscored unless they agree". Those *do* change the
  reported number.

**Impact.** Two runs of the same inspect_evals task, at the same inspect_evals
commit, on environments built weeks apart, produce different accuracies with
nothing in the log to distinguish them (`EvalLog` records the inspect_ai version,
but no task-version bump signals a scoring change). Anyone comparing against a
published inspect_evals baseline needs the inspect_ai commit as well.

---

## 6. `"mode"` is documented as "majority vote" but is a plurality with declaration-order tie-breaking

- **Defect class:** 9 (aggregation) / 4
- **File:** `inspect_ai/scorer/_reducer/reducer.py:12-38` (`most_common`), `_metric.py` `Counter` insertion order; consumer at `inspect_ai/scorer/_model.py:176`
- **Severity:** medium · **Confidence:** high

```python
def most_common(counts): return counts.most_common(1)[0][0]
```

`Counter.most_common` breaks ties by first-insertion order, and `_count_scalar`
inserts in the order the scores were produced — i.e. the order of `model=[...]`
for a grader panel, or epoch order for `Epochs(n, "mode")`.

Documentation claims a majority in three places:

- `docs/model-graded.qmd`: "if a list is provided, each model grades
  independently and the final grade is by majority vote"; "uses the
  `multi_scorer()` function with a `"mode"` (majority vote) reducer".
- `docs/multiple-scorers.qmd:200`: "the "mode" reducer which returns the score
  that appeared most frequently in the answers (i.e. a majority vote)".
- `_model.py:79-82` docstring: "the final grade is computed by majority vote".

Reproduction (`test_reducers.py`):

```
mode ['C', 'I']            -> 'C'      mode ['I', 'C']            -> 'I'
mode ['C', 'P', 'I']       -> 'C'      mode ['I', 'P', 'C']       -> 'I'
mode [nan, 'C', 'I']       -> 'C'      mode [nan, 'I', 'C']       -> 'I'
```

The third row is the important one: an unscored panel member is dropped from the
count rather than withholding a vote, so a 3-model panel in which one grader
fails to emit a parseable grade is decided by whichever of the remaining two was
listed first.

**Impact.** A 2-model panel is not a vote at all — it is "model 1 decides, unless
it abstains". A 3-model panel degrades to that whenever one grader fails to
parse. Direction depends on which grader is listed first, so it is a silent
source of run-to-run and configuration-to-configuration variance in
safety-relevant graded scores. Addressed on `main`, which adds a strict
`majority` reducer (NaN counts toward the denominator, no majority ⇒ unscored)
and makes it the default for grader panels
(`inspect_ai_src/.../_reducer/reducer.py:41-84`, `_model.py:43`).

---

## 7. `choice()` silently scores 0% for any target that is not a bare letter

- **Defect class:** 2 (ground truth) / 4
- **File:** `inspect_ai/scorer/_choice.py:21-25`
- **Severity:** medium · **Confidence:** high

Because only `","` and `" "` are filtered and every other letter is a legal
answer character, common target-format mistakes produce a *silent* stream of
INCORRECT rather than an error:

```
target 'Paris'    (answer text)        -> I   (model had picked 'A' correctly)
target 'A and B'  (prose separator)    -> I   (documented form 'A,B' -> C)
target '0'        (0-based index)      -> I   (answer_index('0') == 25 == 'Z')
```
(`test_choice_scorer.py::test_target_as_answer_text_is_silently_incorrect`,
`..._with_a_prose_separator...`, `..._zero_based_numeric_target...`)

Only a target containing a character that is neither alphanumeric nor `,`/` `
(e.g. `"B) Paris"`) raises. `main` narrows this by raising when a resolved
position exceeds the number of choices, which catches the answer-text case for
small option counts but not `"A and B"` or `"0"`.

A related crash, same root cause (`dataset/_dataset.py:352-358`): `_remap_target`
hands the whole string to `answer_index`, so `dataset.shuffle_choices()` raises
`TypeError: ord() expected a character` for a string target `"AB"` and
`ValueError` for `"A,B"` / `"A, B"`, even though `choice()` accepts exactly those
forms (`test_choice_scorer.py::test_dataset_shuffle_choices_raises_on_a_multi_answer_string_target`).
The list form `["A","B"]` works.

**Impact.** A port that stores the target in a non-letter form reports a
plausible-looking near-0% instead of failing loudly. This is the failure mode
most likely to be mistaken for "the model is bad at this eval".

---

## 8. `match(numeric=True)` strips punctuation from the target but not from the completion when the target is not itself numeric

- **Defect class:** 4 (parsing)
- **File:** `inspect_ai/scorer/_common.py:59-62, 84-96`
- **Severity:** medium · **Confidence:** high

```python
if numeric:
    t = strip_numeric_punctuation(t)          # unconditional
if numeric and _is_number(t):
    v = strip_numeric_punctuation(v)          # only in the numeric-target branch
    ...
elif ignore_punctuation:
    v = strip_punctuation(v)                  # edge punctuation only
    t = strip_punctuation(t)
```

`strip_numeric_punctuation` deletes `$ , £ € * _` everywhere in the string. When
the target does not parse as a number, the target has been stripped and the
completion has not, so a literally identical answer cannot match:

```
completion 'The price is 1,000 dollars'  target '1,000 dollars'  numeric=True -> I   (numeric=False -> C)
completion 'the variable is x_1'         target 'x_1'            numeric=True -> I   (numeric=False -> C)
completion 'The price is 1000 dollars'   target '1,000 dollars'  numeric=True -> C
```
(`test_text_match_scorers.py::test_numeric_true_breaks_non_numeric_targets_containing_stripped_characters`)

Same stripping, opposite direction: comma removal concatenates digits, so
`"The digits are 1,2,3"` matches a target of `"123"`
(`test_numeric_comma_stripping_concatenates_a_list_of_digits`).

Not fixed on `main` (the unconditional `t = strip_numeric_punctuation(t)` is
unchanged). **Impact** is limited inside inspect_evals — only `gsm8k` and `mgsm`
pass `numeric=True` and both have plain numeric targets — but it is a trap for
any new port with mixed number-and-unit targets.

---

## 9. `answer("line")` / `AnswerPattern.LINE` is broken by a trailing full stop or trailing spaces

- **Defect class:** 4 (parsing)
- **File:** `inspect_ai/_util/pattern.py:9`, comparison at `inspect_ai/scorer/_pattern.py:12-17`
- **Severity:** medium · **Confidence:** high

```python
ANSWER_PATTERN_LINE = r"(?i)ANSWER\s*:\s*([^\n]+)\s*\Z"
```

`[^\n]+` is greedy, so it swallows trailing spaces and punctuation, and
`pattern()` compares the capture to the target by **equality** (`match in target`,
after lower-casing) with no trimming:

```
'ANSWER: Paris'          -> C
'ANSWER: Paris\n'        -> C
'ANSWER: Paris.'         -> I      # a full stop costs the point
'ANSWER: Paris  '        -> I      # trailing spaces cost the point
'ANSWER: Paris.\n'       -> I
'ANSWER: Paris\nThanks!' -> N
```
(`test_text_match_scorers.py::test_answer_line_is_sensitive_to_trailing_punctuation_and_spaces`)

`ANSWER_PATTERN_WORD` absorbs one trailing punctuation mark via its lookahead and
is not affected; `ANSWER_PATTERN_LETTER` is not affected by a full stop but
returns NOANSWER for `ANSWER: **A**`.

Not fixed on `main` (`_util/pattern.py` is identical). Inside inspect_evals
`answer("line")` is unused, but `AnswerPattern.LINE` is applied directly by
`docvqa`, `vqa_rad`, `mathvista`, `agieval` and `math` — those ports do their own
`.strip()` in some cases and not others, so the sensitivity leaks downstream.

---

## 10. `pretend_we_didnt_shuffle` overwrites the model's real completion, contrary to its own docstring

- **Defect class:** 5 (prompt/state plumbing) / 1
- **File:** `inspect_ai/solver/_multiple_choice.py:188, 205-214`
- **Severity:** medium · **Confidence:** high

The docstring says:

> Note that this just rewrites message history. The `TaskState.choices` are left
> shuffled, to allow us to be transparent about this elsewhere.

The code rewrites `state.output.completion` as well:

```python
pretend_answer = f"ANSWER: {answer_text}"
state.output.completion = pretend_answer
state.messages[-1].content = pretend_answer
```

Reproduction (`test_choice_scorer.py::test_pretend_we_didnt_shuffle_overwrites_the_real_completion`):

```
before: 'Reasoning about Paris ... ANSWER: B'
after : 'ANSWER: A'
includes('Paris') on the rewritten completion -> I
```

**Impact.** With `multiple_choice(shuffle=...)`, any *second* scorer on the task,
any post-hoc log analysis, and any human reading the transcript sees a synthesized
one-line answer instead of the model's output — including its chain of thought.
`choice()` itself is unaffected (it reads `state.choices`). Reachable only via the
deprecated `shuffle` parameter of the solver, which is why I rate it medium
rather than high.

---

## 11. Clustered `stderr` reports 0.0 for a single cluster, and merges cluster ids that differ only by type

- **Defect class:** 9 (metrics)
- **File:** `inspect_ai/scorer/_metrics/std.py:96-124`
- **Severity:** medium · **Confidence:** high

The formula itself is right. Positive control: with every sample in its own
cluster the clustered SE equals the CLT SE exactly
(`test_metrics.py::test_clustered_stderr_matches_the_plain_stderr_when_every_cluster_is_a_singleton`),
and with outcomes perfectly tracking two clusters it inflates 0.2887 → 0.5.

Two edge cases are silent:

```
stderr(cluster='c'), all 4 samples in cluster 'g1'   -> 0.0
stderr(cluster='c'), ids [1, '1', 2, '2']            -> 0.5   (== the 2-cluster value)
```

The first is the `cluster_count < 2` guard at `std.py:106` returning `0.0`; the
cluster-robust SE is undefined there, and 0.0 renders as a perfectly precise
estimate. The second is `np.unique` coercing a mixed int/str metadata column to
strings, so `1` and `"1"` become one cluster with no warning.

For comparison the non-clustered `stderr()`, `std()`, `var()` and
`bootstrap_stderr()` all return `0` for a single sample
(`test_metrics.py::test_dispersion_metrics_report_zero_for_a_single_sample`) —
the same "zero means undefined" pattern. Six inspect_evals ports use
`stderr(cluster=...)` (among them `docvqa`, clustering on `document_id`).
`main` has reworked this code substantially
(`_cluster_partition`, NaN/None cluster-id validation).

---

## 12. `f1()` returns 1.0 for an empty completion when the target normalizes to zero tokens

- **Defect class:** 1 (scorer exploitability)
- **File:** `inspect_ai/scorer/_classification.py:99-114`
- **Severity:** low (needs a degenerate target) · **Confidence:** high

```python
if not answer_words:  precision = 1.0
if not target_words:  recall = 1.0
```

Both bags empty ⇒ f1 = 1.0. `max_f1_score` only skips targets that are empty
*before* normalization (`if target.strip():`), so a target of `"the"`, `"a"`,
`"an"` or `"."` — or any target consisting only of the caller's `stop_words` —
survives that check and then normalizes to nothing:

```
completion ''       target 'the'    -> 1.0     completion 'Paris'  target 'the'   -> 0.0
completion ''       target '.'      -> 1.0
completion ''       target 'Paris'  -> 0.0
```
(`test_text_match_scorers.py::test_f1_scores_an_empty_completion_1_0_when_the_target_normalises_to_nothing`)

Not fixed on `main` (`_classification.py` identical). Also worth noting as a
documented-but-exploitable property: with a one-token target, naming both labels
scores 0.67 on every sample (`"yes no"` against target `"yes"`), so on a binary
`f1()`-scored task a fixed hedging answer guarantees two-thirds credit
(`test_f1_gives_partial_credit_for_naming_every_candidate_answer`).

---

## 13. `bootstrap_stderr()` is unseeded

- **Defect class:** 3 (randomness)
- **File:** `inspect_ai/scorer/_metrics/std.py:44-50`
- **Severity:** low · **Confidence:** high

`np.random.choice` on the global numpy RNG, with no seed parameter:

```
bootstrap runs over the same 12 scores: [0.143652, 0.138644, 0.142637, 0.143538]
stderr() over the same scores:           0.148647
```
(`test_metrics.py::test_bootstrap_stderr_is_not_reproducible_and_runs_below_the_clt_stderr`)

The ~4% gap to `stderr()` is `sqrt((n-1)/n)` and is inherent to bootstrapping a
mean, not a bug — but the two metrics are not interchangeable at small n, and the
logged value is not reproducible.

Same class: `dataset.shuffle_choices()` defaults to `random.Random(None)`
(`dataset/_dataset.py:331-332`), so `shuffle_choices()` / `shuffle_choices=True`
produces a different effective dataset on every run
(`test_choice_scorer.py::test_dataset_shuffle_choices_is_unseeded_by_default`).
The docs do show the seeded form (`docs/_shuffling-choices.md`), so this is a
footgun rather than a contradiction.

---

## 14. `Choices.shuffle()` called twice corrupts `original_position`

- **Defect class:** 4
- **File:** `inspect_ai/solver/_task_state.py:106-123`
- **Severity:** low (not reachable through the built-in solver) · **Confidence:** high

`shuffled_choices[i].original_position = shuffled_position` records the position
in the *current* order, not the sample's order, so a second shuffle overwrites
the mapping:

```
after 1st shuffle: ['London','Paris','Berlin','Rome']  original_position [2,0,1,3]
after 2nd shuffle: ['Rome','London','Berlin','Paris']  original_position [3,0,2,1]
true original idx:                                                      [3,2,1,0]
```
(`test_choice_scorer.py::test_double_shuffle_corrupts_original_position`)

`choice()` unshuffles by `original_position`, so a double shuffle would score
against the wrong letters. The built-in `multiple_choice` solver shuffles at most
once per `TaskState`, so I could not reach it from a task; fixed on `main`
(`self._choices = [self._choices[p] for p in shuffled_positions]`, plus
`test_choices_multiple_shuffles_preserve_original_positions`).

---

## Documented behaviour that is merely surprising (not defects)

These all match the documentation; I list them because they are the ones most
likely to be misread as bugs, and because two of them are exploitable.

- **`match()` defaults to a suffix test on raw text.** `match()` with
  `numeric=False` (the default) credits any completion whose last characters are
  the target: `"The answer is 1234"` matches target `"4"`, `"the value is 25"`
  matches `"5"`, `"Rome"` matches `"e"`. Documented ("`end` (the default)"), and
  `numeric=True` closes the digit case. `findings/repro/inspect_core/test_text_match_scorers.py::test_match_end_credits_a_wrong_answer_that_merely_ends_with_the_target`.
- **`match("any")` and `includes()` credit a completion that lists every
  option.** `"The options are A) 3 B) 4 C) 9 D) 12"` scores CORRECT against each
  of `3`, `4`, `9`, `12`. Documented as substring/anywhere matching; appropriate
  for CTF flag checks (`cybench`, `gdm_intercode_ctf`), dangerous for short-answer
  targets.
- **`choice()` is all-or-nothing for multiple-answer questions**, so "select
  everything" does not pay (`ANSWER: ABCD` is INCORRECT unless all four are
  correct).
- **NOANSWER counts as 0 in the denominator.** `pattern()` returns NOANSWER when
  its regex does not match, and `value_to_float()("N") == 0.0`, so refusals and
  format failures are indistinguishable from wrong answers in `accuracy`. Both
  halves are documented (`docs/_builtin-scorers.md`, `value_to_float` docstring);
  there is no built-in metric that separates them.
- **`accuracy()` over dict- or list-valued scores is 0.0 with a warning**, exactly
  as its docstring says. A dict-valued scorer declared with a flat
  `metrics=[accuracy(), stderr()]` list therefore reports 0% everywhere. The
  string handling matches `value_to_float`'s docstring (C/I/P/N, yes/no/true/false,
  numeric strings) but is case-sensitive on the sentinels: a scorer returning
  lower-case `"c"` scores 0 with a warning.
- **NaN filtering lives in the pipeline, not in the metrics.** `Score.unscored()`
  calls NaN "the canonical sentinel that aggregate metrics and reducers skip", but
  `accuracy`/`mean`/`stderr`/`std`/`var`/`bootstrap_stderr` all return NaN if
  handed one; the filter is `_eval/task/results.py:395-403` (and `:505-536`
  per-key for dict scores). Correct end-to-end, misleading for custom metrics and
  post-hoc analysis. `test_metrics.py::test_metrics_return_nan_when_handed_an_unscored_sample`.
- **The default epoch reducer is `mean`, and it converts C/I to floats and zeroes
  categorical values.** `Epochs(n)` ⇒ `"mean"`; `mean` over `["refusal","refusal"]`
  is `0.0` with a warning per epoch, so a categorical scorer loses its values
  under the default reducer. `collect` produces a list value, which then makes
  `accuracy()` report 0.0 with warnings.
- **Unscored epochs are dropped, not counted.** `mean` over `[nan, nan, "C"]` is
  `1.0` — one scored epoch carries the sample at full credit. `pass_at_k`
  correctly returns NaN when fewer than k epochs scored; `at_least_k` counts only
  scored epochs.
- **`grouped(..., all="groups")` is an unweighted mean of group metrics** (0.5)
  where `all="samples"` is sample-weighted (0.75) on the same unbalanced data.
  Documented; worth knowing before comparing two ports.
- **`pattern()` with no capture group always scores INCORRECT**, even when the
  regex matched. Documented ("at least one regex group is required"); `main`
  changed it to fall back to `match.group(0)`.
- **The model-graded templates show the target to the grader by design**
  (`[Expert]: {criterion}` / `[Criterion]: {criterion}`). That is the point of a
  reference-based grader, not a leak — the target never reaches the model under
  test. The prompt-injection mitigations work as documented: `[BEGIN DATA]` /
  `[END DATA]` in the submission, question, criterion and metadata are rewritten
  to `[BEGIN-DATA]` / `[END-DATA]`, and the greedy `.*` binds the verdict to the
  last `GRADE:` so an earlier chain-of-thought mention does not win
  (`test_model_graded.py`). The residual risk is that "last mention wins" hands
  the grade to the submission if the grader quotes it *after* its own verdict —
  demonstrated in
  `test_last_grade_wins_even_when_it_is_an_echo_of_the_submission`, and inherent
  to the chosen mitigation.

---

## Checked and found OK

- `Choices.shuffle` + `unshuffle_choices` + `choice()` round-trip the target
  correctly for a single shuffle, across 8 seeds
  (`test_choice_scorer.py::test_solver_side_shuffle_round_trips`).
- `MemoryDataset.shuffle_choices` remaps list targets correctly and leaves
  `Choice.original_position` as the identity, so the solver-side and dataset-side
  shuffles do not double-apply.
- `parse_answers` accepted forms: `ANSWER: A`, `answer: a`, `ANSWER: A.`,
  `ANSWER: A,`, last-line-wins for CoT; multi-answer `A, B`, `A and B`, `AB`,
  `A,B,`, Oxford/trailing commas. Refusals, "none of the above", "I don't know"
  and empty output all yield no selection (upstream has explicit tests for these).
- `choice()` on a shuffled task emits an explanation that records the shuffled
  options and the shuffled answer.
- `exact()` normalization: case, edge punctuation, articles, `-` tokenization,
  numeric normalization (`"5"` ≡ `"5.00"`); requires the whole completion.
- `match(numeric=True)` numeric handling: digit-suffix rejection, negatives,
  decimals, scientific notation, unicode minus, vulgar fractions, fullwidth
  digits, `location="exact"` rejecting trailing text, and the documented refusal
  to treat `60%` as `60`.
- `pattern()` `match_all=True` with an all-`None` group tuple correctly returns
  INCORRECT rather than echoing `target.text`.
- `model_graded_qa` grade extraction for the documented forms, `partial_credit`
  gating of `P`, `GRADE: Unknown`/`GRADE: -`/no-grade ⇒ unscored with
  `unscored_reason="grade_parse_failure"`, `downgrade:` not treated as a verdict,
  and last-`GRADE:` binding over an earlier CoT mention.
- Clustered stderr formula against the singleton-cluster identity and against a
  hand-computed 2-cluster case; it raises when the cluster key is missing.
- `grouped()` raises when the group key is missing and rejects a group name that
  collides with `all_label`.
- Reducer shape validation: mismatched dict keys, mismatched list lengths, and a
  dict/scalar mix all raise with actionable messages rather than silently
  dropping keys.
- `accuracy()`/`mean()` return 0.0 for an empty score list, and the pipeline
  substitutes NaN for a scorer with no scored samples.
- `pass_at_k` / `pass_k` return NaN (not a spurious 1.0) when NaN filtering leaves
  fewer than k epochs.
- Upstream tests at the audited commit: `tests/scorer/{test_choice,test_match,
  test_pattern,test_answer,test_classification,test_reducers,test_value_to_float}.py`
  and `tests/solver/test_multiple_choice.py` — 162 passed, 1 failed, and that one
  failure is environmental (see below), not a real regression.

## Not checked here, and why

- **`eval()`-driven tests.** `tests/` needs `moto` (absent) and mockllm's token
  counting downloads a tiktoken BPE table from
  `openaipublic.blob.core.windows.net`, which the proxy blocks (403). Every
  upstream test that calls `eval()` fails for that reason alone (14 across
  `tests/scorer` + `tests/solver`), including
  `tests/solver/test_multiple_choice.py::test_more_than_26_choices` — I confirmed
  from the traceback that it is a `ProxyError`, not a scoring failure. All
  reproductions here therefore await scorers directly and stub the tokenizer
  (`_helpers.stub_tokenizer`), so no end-to-end log/metric assembly
  (`unscored_samples` accounting, reducer selection, `scores="unreduced"` metrics)
  was exercised at runtime; that part is read-only analysis of
  `_eval/task/results.py`.
- **Real model graders.** No provider credentials and no network, so all
  `model_graded_*` reproductions use a fixed mockllm completion. The *rate* at
  which real graders emit off-menu verdicts like "GRADE: Cannot determine"
  (finding 1) is therefore unmeasured — I establish the mechanism, not the
  frequency.
- **`scorer/_math.py`, `_perplexity.py`, `_target_perplexity.py`,
  `_precomputed.py`, `_metrics/aggregate.py`, `_metrics/categorical.py`,
  `_metrics/krippendorff.py`, `_cascade.py`** — outside the brief's scope. `_math`
  needs the optional `inspect-ai[math]` extra in any case.
- **Docker / sandbox paths and Hugging Face datasets** — no daemon, and
  huggingface.co is blocked, per the audit brief.
