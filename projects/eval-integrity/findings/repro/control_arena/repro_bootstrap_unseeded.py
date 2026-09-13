"""Repro: bootstrap confidence intervals are unseeded by default.

control_arena/analysis/_confidence_intervals.py:53 random_state: RandomState | None = None
control_arena/analysis/_monitor_metrics.py:56 MonitorAnalysisSettings.random_state = None
"""

import pandas as pd

from control_arena.analysis import (
    MonitorAnalysisSettings,
    compute_bootstrapped_confidence_interval,
    compute_classifier_roc_auc,
    compute_monitor_classification_metrics,
)

honest = pd.Series([0.0, 0.1, 0.1, 0.2, 0.2, 0.3, 0.3, 0.4, 0.5, 0.6])
attack = pd.Series([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.7, 0.8, 0.9, 1.0])

print("compute_bootstrapped_confidence_interval, default random_state=None:")
for i in range(3):
    print("  run", i, compute_bootstrapped_confidence_interval(
        honest, attack, compute_classifier_roc_auc))  # type: ignore[arg-type]

print("\nwith random_state=0:")
for i in range(3):
    print("  run", i, compute_bootstrapped_confidence_interval(
        honest, attack, compute_classifier_roc_auc, random_state=0))  # type: ignore[arg-type]

honest_df = pd.DataFrame({
    "eval_mode": ["honest"] * 10,
    "main_task_success": [True] * 10,
    "side_task_success": [None] * 10,
    "score_m": honest,
})
attack_df = pd.DataFrame({
    "eval_mode": ["attack"] * 10,
    "main_task_success": [True] * 10,
    "side_task_success": [True] * 10,
    "score_m": attack,
})
settings = MonitorAnalysisSettings(
    scorer_name="m", is_binary=False, target_fpr=0.1,
    confidence_intervals_level=0.95,
)
print("\ncompute_monitor_classification_metrics with the documented settings "
      "(no random_state):")
for i in range(3):
    m = compute_monitor_classification_metrics(honest_df, attack_df, settings)  # type: ignore[arg-type]
    print(f"  run {i}  tpr_ci={m.tpr_confidence_interval}  auc_ci={m.roc_auc_confidence_interval}")
