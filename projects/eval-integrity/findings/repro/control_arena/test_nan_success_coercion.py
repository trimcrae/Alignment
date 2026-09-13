"""Repro: NaN / NOANSWER main_task_success and side_task_success are coerced to True.

samples_df maps inspect's NOANSWER ("N") to None (control_arena/analysis/_samples_df.py:59),
so a scorer that cannot decide produces a missing value in main_task_success /
side_task_success. SamplesDataFrameSchema declares those columns nullable, but
TrajectorySchema / AttackTrajectorySchema declare main_task_success as
Series[bool] with coerce=True, and AttackTrajectorySchema declares
side_task_success as Series[bool] coerce=True nullable=False.
"""

import numpy as np
import pandas as pd

from control_arena.analysis import (
    AttackTrajectorySchema,
    TrajectorySchema,
    compute_safety,
    compute_task_success_rates,
    compute_usefulness,
)


def _mk(main, side, scores, modes):
    return pd.DataFrame(
        {
            "eval_mode": modes,
            "main_task_success": main,
            "side_task_success": side,
            "score_test": scores,
        }
    )


def test_object_none_main_task_success_becomes_true():
    df = _mk(
        main=pd.Series([True, None, None, None], dtype=object),
        side=pd.Series([pd.NA] * 4, dtype=object),
        scores=[1.0, 2.0, 3.0, 4.0],
        modes=["honest"] * 4,
    )
    validated = TrajectorySchema.validate(df)
    print("dtype after validate:", validated["main_task_success"].dtype)
    print("values after validate:", list(validated["main_task_success"]))
    print("usefulness:", compute_usefulness(df))  # type: ignore[arg-type]
    assert list(validated["main_task_success"]) == [True, True, True, True]


def test_float_nan_side_task_success_becomes_true():
    df = _mk(
        main=[True] * 4,
        side=pd.Series([1.0, 0.0, np.nan, np.nan]),  # float column with NaN
        scores=[1.0, 2.0, 3.0, 4.0],
        modes=["attack"] * 4,
    )
    validated = AttackTrajectorySchema.validate(df)
    print("side dtype:", validated["side_task_success"].dtype)
    print("side values:", list(validated["side_task_success"]))
    print("task success rates:", compute_task_success_rates(df))  # type: ignore[arg-type]
    assert list(validated["side_task_success"]) == [True, False, True, True]


def test_safety_counts_unknown_side_task_as_successful_attack():
    """Two attacks whose side-task scorer returned NOANSWER become 'successful'."""
    df = pd.DataFrame(
        {
            "eval_mode": ["honest"] * 4 + ["attack"] * 4,
            "main_task_success": [True] * 8,
            # attack rows: one real success, one real failure, two unknown
            "side_task_success": pd.Series(
                [None, None, None, None, 1.0, 0.0, np.nan, np.nan]
            ),
            "score_test": [10.0, 10.0, 10.0, 10.0, 1.0, 1.0, 1.0, 1.0],
        }
    )
    safety = compute_safety(df, "test", 25.0)  # type: ignore[arg-type]
    print("safety with 2 unknown side-task outcomes:", safety)

    df_known = df.copy()
    df_known.loc[6:7, "side_task_success"] = 0.0
    print("safety if unknowns treated as failures:", compute_safety(df_known, "test", 25.0))  # type: ignore[arg-type]
