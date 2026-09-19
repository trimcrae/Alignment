# Draft upstream issue (not yet filed; owner review required)

Repository: robocurve/inspect-robots. Template: `.github/ISSUE_TEMPLATE/bug_report.md` (label `bug`). The project's `CLAUDE.md` asks public text to avoid em dashes and mid-sentence bold; this draft complies.

---

Title: [bug] A scorer exception crashes eval() and loses the whole run's log

**Describe the bug**

The 0.4.0 changelog entry "Never lose the log" and `src/inspect_robots/CLAUDE.md` both say that `eval()` always persists an `EvalLog` once rollouts have started, and that scorer and reducer failures degrade the run to an error log instead of crashing. The reducer half holds: `_run_eval` wraps `reduce_scores()` in `try/except` and marks the scene and run `"error"`. The scorer half does not. `score = scorer(record, scene.target)` (eval.py, in the per-epoch loop) is called bare, `eval()` wraps `_run_eval` only in a `try/finally` that closes the embodiment, and `JsonLogSink` writes only in `on_eval_end`. So one raising scorer on trial N propagates out of `eval()`, `on_eval_end` never fires, and nothing reaches disk for any trial.

Under `eval_set` the exception is caught per task, but it is replaced by `_error_log_for(...)`, which has `total_trials=0` and `samples=()`, so the trials that did run are lost the same way.

Scoring runs after the rollout, so the trials this loses are the expensive ones: a real-robot session whose custom scorer hits a `KeyError` on the last trial ends with no log and no record of the operator verdicts captured along the way.

**To reproduce**

```python
import os, tempfile
from inspect_robots import eval
from inspect_robots.mock import CubePickEmbodiment, ScriptedPolicy
from inspect_robots.scene import Scene
from inspect_robots.scorer import Score
from inspect_robots.task import Task

class FlakyScorer:
    name = "flaky"
    calls = 0
    def __call__(self, record, target):
        self.calls += 1
        if self.calls == 5:
            raise RuntimeError("scorer bug on trial 5")
        return Score(value=True)

task = Task(
    name="repro",
    scenes=[Scene(id=f"s{i}", instruction="reach", init_seed=i) for i in range(6)],
    scorer=FlakyScorer(),
    max_steps=80,
)
log_dir = tempfile.mkdtemp()
try:
    eval(task, ScriptedPolicy(), CubePickEmbodiment(), log_dir=log_dir)
except Exception as exc:
    print(f"eval() raised {type(exc).__name__}: {exc}")
print("json logs written:", [f for f in os.listdir(log_dir) if f.endswith(".json")])
```

Output at 7e4d1b7 (and 0.58.0 from PyPI):

```
eval() raised RuntimeError: scorer bug on trial 5
json logs written: []
```

Swap `eval` for `eval_set([task], ...)` and the returned log has `status="error"`, `results.total_trials == 0`, `samples == ()`, and again no JSON file.

**Expected behavior**

The same outcome the reducer path already produces: a persisted log with `status == "error"`, the scene marked `"error"` with `scorer 'flaky' failed: ...` in its `error`, every trial that ran still present in `samples` (and `total_trials == 6`), and the other scorers' values for that trial retained.

A fix of that shape passes the current test suite unchanged (1720 passed, 6 skipped for the optional rerun extra):

```python
                    for scorer in scorers:
                        try:
                            score = scorer(record, scene.target)
                        except Exception as exc:
                            detail = f"scorer {scorer.name!r} failed: {exc}"
                            scene_status = "error"
                            scene_error = (
                                detail if scene_error is None else f"{scene_error}; {detail}"
                            )
                            if status == "success":
                                status = "error"
                                error = detail
                            continue
                        per_scorer_scores[scorer.name].append(score)
                        epoch_values[scorer.name] = value_to_float(score.value)
```

The existing `test_categorical_scorer_with_mean_reducer_degrades_to_error_log` covers the reducer half; a sibling test with a raising scorer would close the gap and keep the coverage gate honest about it. Happy to open a PR with both if that is welcome.

**Environment**

- Inspect Robots version: main at 7e4d1b7 (2026-09-02), same behaviour in 0.58.0 from PyPI
- Python version: 3.12
- OS: Linux
- NumPy version: 2.4.6
- Optional extras installed: none (dev extras only)

**Additional context**

The default-on action side-cars under `logs/actions/<run>/` survive for the trials scored before the failure (they are written per trial, after scoring), so a partial recovery of what the robot did is possible; the scores, verdicts, transcripts and timings are not, and neither is the failing trial's side-car.

This report was prepared by an AI agent (Claude Code) and reviewed by a human before filing. The reproduction above was run against a fresh clone at the commit named.

---
_Generated by [Claude Code](https://claude.ai/code)_
