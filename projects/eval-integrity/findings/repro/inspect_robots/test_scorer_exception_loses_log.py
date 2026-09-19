"""Reproduction: a scorer exception crashes eval() and loses the whole run's log.

Target: robocurve/inspect-robots commit 7e4d1b7 (2026-09-02), PyPI 0.58.0.

The 0.4.0 changelog ("Never lose the log") and src/inspect_robots/CLAUDE.md
promise that eval() always persists an EvalLog once rollouts have started and
that "scorer/reducer failures degrade to an error log, never a crash". The
reducer half holds (see the passing control test). The scorer half does not:
eval.py wraps reduce_scores() in try/except but calls scorer(record, target)
bare, so one raising scorer on trial N propagates out of eval(), on_eval_end
never fires, and JsonLogSink (which writes only at on_eval_end) writes nothing.

The two tests marked "documented contract" FAIL at 7e4d1b7; they pass once the
scorer call is guarded the way the reducer call already is.

Run:
  cd <audit>/inspect_robots && .venv/bin/python -m pytest ../findings/repro/inspect_robots -q
"""

from __future__ import annotations

from pathlib import Path

import pytest

from inspect_robots import eval, eval_set
from inspect_robots.mock import CubePickEmbodiment, ScriptedPolicy
from inspect_robots.scene import Scene
from inspect_robots.scorer import Score
from inspect_robots.task import Task


class _FlakyScorer:
    """Scores True until call number ``fail_on``, then raises once."""

    name = "flaky"

    def __init__(self, fail_on: int) -> None:
        self.fail_on = fail_on
        self.calls = 0

    def __call__(self, record, target) -> Score:
        self.calls += 1
        if self.calls == self.fail_on:
            raise RuntimeError("scorer bug")
        return Score(value=True)


class _CategoricalScorer:
    """A categorical score that the numeric ``mean`` reducer must reject."""

    name = "grade"

    def __call__(self, record, target) -> Score:
        return Score(value="A")


def _task(scorer, scenes: int = 6, **kw) -> Task:
    return Task(
        name="repro",
        scenes=[Scene(id=f"s{i}", instruction="reach", init_seed=i) for i in range(scenes)],
        scorer=scorer,
        max_steps=80,
        **kw,
    )


def _json_logs(log_dir: Path) -> list[str]:
    return sorted(p.name for p in log_dir.glob("*.json"))


def test_control_reducer_exception_degrades_to_error_log(tmp_path: Path) -> None:
    """Control: the reducer path honours the contract, so the fix has a template."""
    (log,) = eval(
        _task(_CategoricalScorer(), scenes=2),
        ScriptedPolicy(),
        CubePickEmbodiment(),
        log_dir=str(tmp_path),
    )
    assert log.status == "error"
    assert "reducer 'mean' failed" in (log.error or "")
    assert log.results.total_trials == 2
    assert _json_logs(tmp_path), "the reducer failure still produced a JSON log"


def test_documented_contract_scorer_exception_degrades_to_error_log(tmp_path: Path) -> None:
    """Documented contract: scorer failures degrade to an error log, never a crash."""
    scorer = _FlakyScorer(fail_on=5)
    logs = eval(_task(scorer), ScriptedPolicy(), CubePickEmbodiment(), log_dir=str(tmp_path))
    (log,) = logs
    assert log.status == "error"
    assert log.results.total_trials == 6, "every trial that ran is recorded"
    assert _json_logs(tmp_path), "a JSON log reached disk"


def test_documented_contract_eval_set_keeps_trial_data(tmp_path: Path) -> None:
    """Under eval_set the crash is caught, but as a log with zero samples: data lost."""
    scorer = _FlakyScorer(fail_on=5)
    success, logs = eval_set(
        [_task(scorer)], ScriptedPolicy(), CubePickEmbodiment(), log_dir=str(tmp_path)
    )
    (log,) = logs
    assert success is False
    assert log.status == "error"
    assert log.results.total_trials == 6, "the five scored trials must not vanish"
    assert len(log.samples) == 6
    assert _json_logs(tmp_path), "a JSON log reached disk"


def test_observed_behaviour_at_7e4d1b7(tmp_path: Path) -> None:
    """Tripwire: records what actually happens today. Fails once the defect is fixed."""
    scorer = _FlakyScorer(fail_on=5)
    with pytest.raises(RuntimeError, match="scorer bug"):
        eval(_task(scorer), ScriptedPolicy(), CubePickEmbodiment(), log_dir=str(tmp_path))
    assert scorer.calls == 5, "four trials were scored before the fifth raised"
    assert _json_logs(tmp_path) == [], "no eval log was written"
    # The default-on action side-cars (one per trial, written after scoring)
    # survive for the four trials scored before the failure; the fifth has none.
    (run_dir,) = (tmp_path / "actions").iterdir()
    assert sorted(p.name for p in run_dir.iterdir()) == [
        "s0-e0.jsonl",
        "s1-e0.jsonl",
        "s2-e0.jsonl",
        "s3-e0.jsonl",
    ]
