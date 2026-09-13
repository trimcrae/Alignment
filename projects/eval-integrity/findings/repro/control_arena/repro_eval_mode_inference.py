"""Repro: samples_df derives eval_mode from side_task_name, ignoring metadata eval_mode.

control_arena/analysis/_samples_df.py:185-187
    combined_df["eval_mode"] = combined_df["metadata_sample"].map(
        lambda cell: "attack" if cell.get("side_task_name") else "honest"
    )

ControlTaskMetadata carries an authoritative eval_mode field
(control_arena/_control_task_metadata.py:59) and side_task_name is optional
(:62).  A sample recorded as attack mode but with no side_task_name is
classified as honest and joins the honest pool the audit threshold is taken from.
"""

import tempfile
from datetime import datetime
from pathlib import Path

from inspect_ai.log import EvalLog, EvalSpec, write_eval_log
from inspect_ai.log._log import EvalConfig, EvalDataset, EvalStats
from inspect_ai.scorer import CORRECT, INCORRECT

from control_arena.analysis import samples_df
from control_arena.analysis.tests.test_samples_df import create_mock_eval_sample

samples = [
    create_mock_eval_sample("h0", eval_mode="honest", main_task_success=CORRECT),
    # attack mode declared in metadata, side_task_name left unset
    create_mock_eval_sample(
        "a0", eval_mode="attack", main_task_success=CORRECT,
        side_task_success=CORRECT, side_task_name=None,
    ),
    create_mock_eval_sample(
        "a1", eval_mode="attack", main_task_success=CORRECT,
        side_task_success=INCORRECT, side_task_name="MockSideTask",
    ),
]
spec = EvalSpec(
    eval_id="e", run_id="r", created=datetime.now().isoformat(), task="mock",
    task_id="t", task_version=0,
    dataset=EvalDataset(name=None, location=None, samples=len(samples),
                        sample_ids=[s.id for s in samples], shuffled=False),
    model="mock/model", config=EvalConfig(limit=3, epochs=1),
    metadata={"setting": {"type": "mock"}, "micro_protocol": {"type": "mock"}},
    scorers=None,
)
log = EvalLog(eval=spec, samples=samples, status="success",
              stats=EvalStats(started_at=datetime.now().isoformat(),
                              completed_at=datetime.now().isoformat()))
with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "log.eval"
    write_eval_log(log, str(p))
    df = samples_df([str(p)])

cols = [c for c in df.columns if "eval_mode" in c]
print("eval_mode-ish columns:", cols)
print(df[["id", *cols, "side_task_success"]].to_string(index=False))
print()
print("metadata_sample['eval_mode'] per row:",
      [m.get("eval_mode") for m in df["metadata_sample"]])
print("derived eval_mode          per row:", list(df["eval_mode"]))
print()
mismatch = [
    (i, m.get("eval_mode"), d)
    for i, m, d in zip(df["id"], df["metadata_sample"], df["eval_mode"], strict=True)
    if m.get("eval_mode") != d
]
print("rows where the two disagree:", mismatch)
