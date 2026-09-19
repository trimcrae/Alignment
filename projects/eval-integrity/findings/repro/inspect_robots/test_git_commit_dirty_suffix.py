"""Reproduction: _git_commit() drops the ``-dirty`` suffix when ``git status`` fails.

Target: robocurve/inspect-robots commit 7e4d1b7 (2026-09-02), PyPI 0.58.0.

eval.py::_git_commit documents: "A -dirty suffix is appended when the working
tree has uncommitted changes, so a log never silently claims a clean commit."
The implementation runs ``git status --porcelain`` with a 2 second timeout and,
when that call times out or exits non-zero, records the bare commit hash. So a
dirty tree in a large repository (or one whose logs/frames directory is not
ignored) is logged as a clean commit: exactly the silent claim the docstring
rules out. The test marked "documented contract" FAILS at 7e4d1b7.
"""

from __future__ import annotations

import importlib
import subprocess

import pytest

_eval_mod = importlib.import_module("inspect_robots.eval")


def _fake_run(status_outcome: str):
    def run(cmd, **kwargs):
        if cmd[:2] == ["git", "rev-parse"]:
            return subprocess.CompletedProcess(cmd, 0, stdout="abc123\n", stderr="")
        assert cmd[:2] == ["git", "status"]
        if status_outcome == "timeout":
            raise subprocess.TimeoutExpired(cmd, kwargs.get("timeout"))
        if status_outcome == "nonzero":
            return subprocess.CompletedProcess(cmd, 128, stdout="", stderr="fatal: index lock")
        return subprocess.CompletedProcess(cmd, 0, stdout=" M src/x.py\n", stderr="")

    return run


def test_control_dirty_tree_is_flagged(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_eval_mod.subprocess, "run", _fake_run("dirty"))
    assert _eval_mod._git_commit() == "abc123-dirty"


@pytest.mark.parametrize("outcome", ["timeout", "nonzero"])
def test_documented_contract_unknown_tree_state_never_claims_clean(
    monkeypatch: pytest.MonkeyPatch, outcome: str
) -> None:
    """If the tree state is unknown, the log must not read as a clean commit."""
    monkeypatch.setattr(_eval_mod.subprocess, "run", _fake_run(outcome))
    assert _eval_mod._git_commit() != "abc123"


@pytest.mark.parametrize("outcome", ["timeout", "nonzero"])
def test_observed_behaviour_at_7e4d1b7(monkeypatch: pytest.MonkeyPatch, outcome: str) -> None:
    """Tripwire: today a failed status check yields the bare, clean-looking hash."""
    monkeypatch.setattr(_eval_mod.subprocess, "run", _fake_run(outcome))
    assert _eval_mod._git_commit() == "abc123"
