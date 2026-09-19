"""Observation: trials the ``vlm`` grader could not grade are scored 0 and the run stays "success".

Target: robocurve/inspect-robots commit 7e4d1b7 (2026-09-02), PyPI 0.58.0.

The vlm grader degrades any post-rollout failure (HTTP 429, transport error,
missing GRADE line) to "trial left ungraded" with one stderr line. The builtin
``operator`` scorer then scores a missing judgement as False, so every grading
outage becomes a task failure in ``metrics["operator"]`` while ``status`` and
``errored_trials`` report a clean run. Only the per-trial ``judgement_sources``
(None) distinguishes "ungraded" from "failed". This is a design consequence of
the documented "None is not affirmative" contract rather than a code slip, and
it overlaps upstream issue #436 (scorer abstention); recorded here as a
tripwire so the magnitude claim in the finding stays checkable.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from inspect_robots import eval
from inspect_robots.grader import vlm_grader
from inspect_robots.mock import CubePickEmbodiment, NoopPolicy
from inspect_robots.scene import Scene
from inspect_robots.scorer import operator_scorer
from inspect_robots.task import Task


def test_half_rate_limited_grader_halves_the_success_rate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("FAKE_KEY", "x")
    calls = {"n": 0}

    def http_post(url: str, headers: dict[str, str], body: bytes) -> tuple[int, bytes]:
        calls["n"] += 1
        if calls["n"] % 2 == 0:
            return 429, b'{"error": "rate limited"}'
        reply = {"choices": [{"message": {"content": "Cube reached.\nGRADE: success"}}]}
        return 200, json.dumps(reply).encode()

    grader = vlm_grader("fake/model", api_key_env="FAKE_KEY", http_post=http_post)
    task = Task(
        name="repro",
        scenes=[Scene(id=f"s{i}", instruction="reach", init_seed=i) for i in range(4)],
        scorer=operator_scorer(),
        max_steps=3,
    )
    (log,) = eval(task, NoopPolicy(), CubePickEmbodiment(), log_dir=str(tmp_path), grader=grader)

    assert log.status == "success"
    assert log.results.errored_trials == 0
    assert log.results.metrics == {"operator": 0.5}, "every graded trial was a success"
    assert [s.judgement_sources for s in log.samples] == [("vlm",), (None,), ("vlm",), (None,)]
    assert capsys.readouterr().err.count("trial left ungraded") == 2
