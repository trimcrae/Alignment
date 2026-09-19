# Inspect Robots: a scorer exception loses the whole run's log, plus two provenance and grading items

```
Target:            robocurve/inspect-robots (the framework behind inspectrobots.org), core package
Version:           commit 7e4d1b7 (2026-09-02, main), identical to PyPI inspect-robots 0.58.0 for the files cited
Defect class:      9 (metrics and aggregation, data loss), 10 (versioning and provenance), 4 (judge handling)
Summary:           eval() guards the epoch reducer against exceptions but not the scorers, so one raising scorer on trial N propagates out of eval(), on_eval_end never fires, and the JSON sink writes nothing: the run's log is lost, contradicting the 0.4.0 changelog's "Never lose the log" guarantee. Two smaller items: the git provenance field drops its "-dirty" marker when `git status` times out or fails, and trials the VLM grader could not grade are scored as failures inside a run that reports status "success".
Reproduction:      repro/inspect_robots/ (10 tests: 4 assert the documented contract and fail at 7e4d1b7, 6 pass as controls and tripwires)
Impact:            Finding 1 destroys data rather than changing a number: an attended real-robot run whose custom scorer hits an exception on the last trial has no EvalLog for any trial (the per-trial action side-cars survive for the trials scored before the failure; camera frames do too if --store-frames was on). Under eval_set the same exception is caught but reported as an error log with total_trials=0 and no samples, so the data is equally lost. Finding 2 mislabels provenance: a log can name a clean commit for code that was modified. Finding 3 deflates metrics["operator"] by one full trial per grading outage while status stays "success" and errored_trials stays 0.
Severity:          Finding 1 medium (reproducibility: the run cannot be analysed at all; it does not alter a reported score). Finding 2 low to medium (provenance claim is wrong in a documented edge case). Finding 3 medium by the rubric (changes a safety-relevant score, downward), but the framing is contested: it follows from the documented "no judgement is not affirmative" contract and overlaps open upstream issue #436.
Confidence:        Finding 1 high (reproduced two ways, and a candidate fix passes the upstream suite). Finding 2 high (mocked subprocess; the docstring states the opposite of the behaviour). Finding 3 high on mechanism, low on novelty.
Disclosure:        drafted 2026-09-19; awaiting repo-owner review before anything is filed. No exploit content; nothing here lets an evaluated policy score without doing the task, so the finding is public in this repo.
```

Produced by an AI agent (Claude Code) on 2026-09-19 at the repo owner's request to add inspectrobots.org to the contribution targets and find one reportable issue. The maintainers' own agent guide (`CLAUDE.md`) and `CONTRIBUTING.md` were read first; the project asks for the `CubePick` mock world in reproductions and for no em dashes in public text, and the issue draft follows both.

## What Inspect Robots is

An open-source evaluation framework for physical AI, described by its authors as "the Inspect AI for robotics": a `Task` of `Scene`s plus scorers runs any policy (a VLA, or a frontier LLM driving the arm through tool calls) on any embodiment (real arm, humanoid, simulator) and writes an immutable, schema-versioned `EvalLog`. It was released in July 2026 by Robocurve, whose business is independent real-world benchmarks for AI and robots, and it is MIT licensed with a 100 percent coverage gate, strict typing, and an active issue tracker (five issues closed as completed since early September, two open integrity reports from an outside contributor, #436 and #440). The scorer, grader, reducer and logging code audited here is the shared substrate every benchmark built on the framework inherits.

The site itself (inspectrobots.org, docs.inspectrobots.org) is unreachable from this sandbox; everything below comes from the GitHub repository, which is reachable.

## Finding 1. A raising scorer crashes `eval()` and loses the log

`src/inspect_robots/CLAUDE.md`, key invariants:

> `eval()` must always return/persist an `EvalLog` once rollouts have started — scorer/reducer failures degrade to an error log, never a crash.

`CHANGELOG.md`, 0.4.0, "Never lose the log":

> `eval()` always produces and persists an `EvalLog` once rollouts have started: scorer/reducer failures degrade the run to an error log instead of crashing

`src/inspect_robots/eval.py` at 7e4d1b7. The reducer call is guarded (lines 676-693):

```python
        reduced: dict[str, float] = {}
        for name, scene_scores in per_scorer_scores.items():
            if not scene_scores:
                continue
            try:
                reduced[name] = value_to_float(
                    reduce_scores(epoch_spec.reducer, scene_scores).value
                )
            except Exception as exc:
                # A reducer failure (e.g. pass_at_k over fewer epochs than k
                # after a halt, or mean over categorical scores) degrades to an
                # error log — it must never crash the eval and lose the log.
                detail = f"reducer {epoch_spec.reducer!r} failed for scorer {name!r}: {exc}"
                scene_status = "error"
                ...
```

The scorer call is not (lines 588-592):

```python
                    epoch_values: dict[str, float] = {}
                    for scorer in scorers:
                        score = scorer(record, scene.target)
                        per_scorer_scores[scorer.name].append(score)
                        epoch_values[scorer.name] = value_to_float(score.value)
```

`eval()` itself wraps `_run_eval` only in a `try/finally` that closes the embodiment, so the exception escapes. `JsonLogSink` writes exclusively in `on_eval_end`, which is never reached. Observed with a six-scene `CubePick` task and a scorer that raises on its fifth call:

```
eval() raised RuntimeError: scorer bug on trial 5
scorer calls: 5
json logs written: []
action side-cars written: s0-e0, s1-e0, s2-e0, s3-e0
```

The action side-cars (`logs/actions/<run>/<trial>.jsonl`, default on) are written per trial after scoring, so the four trials scored before the failure keep theirs and the fifth does not; they are the only surviving trial data, and they hold executed actions only, not scores, verdicts, transcripts or timings.

Under `eval_set`, the per-task `except Exception` catches it and substitutes `_error_log_for(...)`, which has `total_trials=0` and `samples=()`:

```
success: False status: error error: RuntimeError: scorer bug on trial 5
total_trials: 0 samples: 0
json logs written: []
```

So the 0.4.0 guarantee holds for reducers and for policy and embodiment failures inside a trial, but not for the scorer step, which is the one step a benchmark author writes themselves. The existing test `test_categorical_scorer_with_mean_reducer_degrades_to_error_log` covers the reducer half only, which is how 100 percent line coverage coexists with the gap.

Why it matters for an eval framework: scoring runs after the rollout, so the trials it loses are the expensive ones. A real-robot session of thirty trials whose scorer trips on trial thirty (a `KeyError` on an `info` field one embodiment does not emit, a division by zero on an empty distance list, anything) ends with no log at all, and the operator verdicts captured by the grader during those thirty trials are gone with it. This is the failure the framework's own "safe unattended" pitch is about.

Candidate fix, verified: wrap the scorer call in the same `try/except` shape as the reducer, record `scorer {name!r} failed: {exc}` on the scene and the run, mark both `"error"`, and continue. With that patch the two contract tests in `repro/inspect_robots/test_scorer_exception_loses_log.py` pass and the upstream suite still passes (1720 passed, 6 skipped for the optional `rerun` extra). Whether to also retain the scored values of the other scorers for that trial is the maintainers' call; the patch keeps them.

## Finding 2. `git_commit` provenance drops "-dirty" when `git status` fails

`eval.py` lines 149-176. Docstring:

> A `-dirty` suffix is appended when the working tree has uncommitted changes, so a log never silently claims a clean commit.

Implementation: `_git("status", "--porcelain")` runs with `timeout=2`; the helper returns `None` on `OSError` or `SubprocessError` (which includes `TimeoutExpired`), and the suffix is added only when `tree is not None and tree.returncode == 0 and tree.stdout.strip()`. On timeout or a non-zero exit the bare hash is recorded. Reproduced by patching `subprocess.run` in the module: a genuinely dirty checkout reports `7e4d1b7...-dirty` normally and `7e4d1b7...` when the status call times out.

Two seconds is short for `git status` on a large or cold checkout, and this tool's own default `logs/` directory (action side-cars per trial, PNG frames per camera per step with `--store-frames`) lives under the working tree unless the user ignores it, which is exactly the kind of tree that makes `git status` slow. The existing tests cover the OSError and non-zero paths for `rev-parse` but not for `status`. Suggested behaviour: record `-unknown` (or `-dirty`) when the tree state cannot be determined, so the log never reads as a clean commit by default.

## Finding 3. Ungraded trials are scored as failures inside a "success" run

`grader.py`: the `vlm` grader catches every post-rollout exception (HTTP 429, transport error, no `GRADE:` line in the reply) and prints one stderr line, `trial left ungraded`, leaving `operator_judgement` as `None`. `scorer.py`: `_OperatorScorer` returns `Score(value=False)` when the judgement is `None`, per the public `is_affirmative_verdict` contract that `None` is not affirmative. `eval.py` then averages that 0.0 into `metrics["operator"]`, and `status` stays `"success"` with `errored_trials == 0`. Reproduced with a stub endpoint that returns 429 on every second call over four trials the model would have graded as success:

```
status: success metrics: {'operator': 0.5} errored_trials: 0
  s0 success epochs= ({'operator': 1.0},) judgement= ('success',) source= ('vlm',)
  s1 success epochs= ({'operator': 0.0},) judgement= (None,)      source= (None,)
  ...
```

The only trace in the log is `judgement_sources` being `None` for those trials. The direction is conservative for a capability claim (it deflates success), but it silently breaks comparisons between runs or providers with different grader outage rates, and a grading outage is indistinguishable in the metrics from a robot that failed the task.

This is a design consequence rather than a code slip: the docstrings say exactly what happens. Upstream issue #436 (2026-09-05, open) asks for scorer abstention (`Score(value=None)`) and gives the same motivation, preserving "no verdict" against "failure verdict". The concrete grader-outage mechanism above is a useful addition to that thread rather than a new issue.

## Checked and found fine

Listed so the audit is auditable, per `METHODS.md`.

- Epoch reducers: `mean`, `median`, `max`, `min` coerce strictly and raise on categorical values, which `eval()` catches; `pass_at_k` implements the unbiased `1 - C(n-c, k) / C(n, k)` estimator and raises when `k > n`. `mode` breaks ties by `str(value)`, which favours `True` over `False` and `"1"` over `"0"` on a split vote; documented as deterministic, Inspect AI's equivalent breaks ties by insertion order, neither is unbiased, not reported.
- `EnsemblingController` weights: `exp(-m * i)` with `i = 0` for the oldest chunk, buffer sorted by query time. Matches the ACT paper's stated convention.
- `success_at_end` requires the embodiment's `termination_reason == "success"`; a policy-requested stop is recorded as a truncation and cannot self-declare success. The `agent` plugin's `done` tool description says "a scorer judges success". No privileged `info` fields reach the policy.
- Seeding: `derive_seed` distinguishes `None` from `0`; `eval(seed=None)` draws and records an OS seed.
- Rollout rejects non-finite actions before and after the approver; `ClampApprover` aborts on NaN; JSON sinks sanitize non-finite floats to `null` and keep `allow_nan=False` as a backstop.
- `fail_on_error` uses the planned trial count as the denominator, so the first error is not 1/1.
- The `vlm` grader takes the last `GRADE:` match, so a reply that quotes the instruction before answering is read correctly.
- Errored trials are recorded but never scored, and a run in which every trial errored is `"error"`. The partial case (one surviving trial keeps `status == "success"`) is already open upstream as #440.

## Suggested disclosure

1. File Finding 1 alone, using the maintainers' bug-report template; draft in `2026-09-19-inspect-robots.upstream-issue-draft.md`. It is a candidate for the step-1 calibration slot in `../NEXT-STEPS.md`: two lines of cause, a one-block fix that passes their suite, and maintainers who close issues within days.
2. File Finding 2 as a separate small issue after Finding 1 gets a response (different topic; same file).
3. Add Finding 3 as a comment on #436, not a new issue.
