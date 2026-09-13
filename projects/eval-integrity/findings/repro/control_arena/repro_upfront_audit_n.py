"""Repro: the upfront-audit metrics use len(attack subset) as the deployment length.

control_arena/analysis/_metrics.py:263-264
    # Expected untrusted weight across the deployment stream (use untrusted_df length as N)
    total_samples = deployment_samples or len(untrusted_attack)
and _metrics.py:315 does the same in compute_safety_upfront_audit.

Both docstrings say "otherwise just use the number of samples in the provided
untrusted DataFrame".
"""

import pandas as pd

from control_arena.analysis import (
    compute_safety_upfront_audit,
    compute_usefulness_upfront_audit,
)


def mk(n_honest, n_attack, attack_success_rate=0.2):
    n_success = int(round(n_attack * attack_success_rate))
    return pd.DataFrame(
        {
            "eval_mode": ["honest"] * n_honest + ["attack"] * n_attack,
            "main_task_success": [True] * (n_honest + n_attack),
            "side_task_success": [None] * n_honest
            + [True] * n_success
            + [False] * (n_attack - n_success),
            "score_test": [1.0] * (n_honest + n_attack),
        }
    )


print("attack success rate fixed at 0.20, audit budget 2%\n")
print(f"{'honest':>7} {'attack':>7} {'safety':>10} {'usefulness':>11}")
for n_honest, n_attack in [(50, 50), (500, 50), (50, 500), (5000, 5000)]:
    df = mk(n_honest, n_attack)
    s = compute_safety_upfront_audit(df, 2.0)  # type: ignore[arg-type]
    u = compute_usefulness_upfront_audit(df, trusted_usefulness=0.5, audit_budget=2.0)  # type: ignore[arg-type]
    print(f"{n_honest:>7} {n_attack:>7} {s:>10.6f} {u:>11.6f}")
print("\n-> safety/usefulness are identical for (50,50) and (500,50):")
print("   the honest half of the DataFrame never enters N.")

print("\nWhat the docstring describes (N = len(untrusted_df)):")
for n_honest, n_attack in [(50, 50), (500, 50)]:
    df = mk(n_honest, n_attack)
    s = compute_safety_upfront_audit(df, 2.0, deployment_samples=len(df))  # type: ignore[arg-type]
    print(f"  honest={n_honest:>4} attack={n_attack:>4} N={len(df):>4} safety={s:.6f}")

print("\nNo range validation on audit_budget, despite the documented "
      "'Raises ValueError: If audit_fraction is out of range':")
df = mk(50, 50)
for budget in (-10.0, 150.0):
    try:
        print(f"  audit_budget={budget:>7} -> safety={compute_safety_upfront_audit(df, budget):.6f}")  # type: ignore[arg-type]
    except Exception as e:
        print(f"  audit_budget={budget:>7} -> {type(e).__name__}: {e}")
