"""End-to-end behaviour of NOANSWER ("N") task scores in the analysis metrics.

Builds real EvalLogs with control_arena's own test helpers, runs
control_arena.analysis.samples_df, then calls the metric functions.
"""

import tempfile
from datetime import datetime
from pathlib import Path

from inspect_ai.log import EvalLog, EvalSpec, write_eval_log
from inspect_ai.log._log import EvalConfig, EvalDataset, EvalStats
from inspect_ai.scorer import CORRECT, INCORRECT, NOANSWER

from control_arena.analysis import (
    compute_safety,
    compute_task_success_rates,
    compute_usefulness,
    samples_df,
)
from control_arena.analysis.tests.test_samples_df import create_mock_eval_sample


def build_df(specs):
    samples = [
        create_mock_eval_sample(
            sample_id=f"s{i:03d}",
            eval_mode=mode,
            main_task_success=main,
            side_task_success=side,
            side_task_name="MockSideTask" if mode == "attack" else None,
        )
        for i, (mode, main, side) in enumerate(specs)
    ]
    spec = EvalSpec(
        eval_id="e1", run_id="r1", created=datetime.now().isoformat(),
        task="mock", task_id="t1", task_version=0,
        dataset=EvalDataset(name=None, location=None, samples=len(samples),
                            sample_ids=[s.id for s in samples], shuffled=False),
        model="mock/model", config=EvalConfig(limit=len(samples), epochs=1),
        metadata={"setting": {"type": "mock"}, "micro_protocol": {"type": "mock"}},
        scorers=None,
    )
    log = EvalLog(eval=spec, samples=samples, status="success",
                  stats=EvalStats(started_at=datetime.now().isoformat(),
                                  completed_at=datetime.now().isoformat()))
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "log.eval"
        write_eval_log(log, str(p))
        return samples_df([str(p)])


def show(label, fn):
    try:
        print(f"  {label}: {fn()}")
    except Exception as e:
        first = str(e).strip().splitlines()[0]
        print(f"  {label}: raised {type(e).__name__}: {first}")


print("=== A. NOANSWER on the MAIN task of one honest sample ===")
dfa = build_df(
    [("honest", CORRECT, None)] * 3 + [("honest", NOANSWER, None)]
    + [("attack", CORRECT, CORRECT), ("attack", CORRECT, INCORRECT)]
)
print("  main dtype:", dfa["main_task_success"].dtype, list(dfa["main_task_success"]))
show("compute_usefulness", lambda: compute_usefulness(dfa))
show("compute_task_success_rates", lambda: compute_task_success_rates(dfa))
show("compute_safety", lambda: compute_safety(dfa, "other_scorer", 25.0))

print()
print("=== B. NOANSWER on the SIDE task of two attack samples ===")
dfb = build_df(
    [("honest", CORRECT, None)] * 4
    + [("attack", CORRECT, CORRECT), ("attack", CORRECT, INCORRECT)]
    + [("attack", CORRECT, NOANSWER)] * 2
)
print("  side dtype:", dfb["side_task_success"].dtype, list(dfb["side_task_success"]))
show("compute_task_success_rates (all rows)", lambda: compute_task_success_rates(dfb))
show("compute_safety", lambda: compute_safety(dfb, "other_scorer", 25.0))

print()
print("=== C. baseline: no NOANSWER anywhere ===")
dfc = build_df(
    [("honest", CORRECT, None)] * 4
    + [("attack", CORRECT, CORRECT), ("attack", CORRECT, INCORRECT)]
    + [("attack", CORRECT, INCORRECT)] * 2
)
show("compute_usefulness", lambda: compute_usefulness(dfc))
show("compute_task_success_rates", lambda: compute_task_success_rates(dfc))
show("compute_safety", lambda: compute_safety(dfc, "other_scorer", 25.0))
