"""Compare the port's generated prompts against Anthropic's official generate_prompts.py
for the whole condition grid.

Run:
  cd <audit dir>
  inspect_evals/.venv/bin/python findings/repro/agentic_misalignment/compare_prompts_with_official.py

Official clone: agentic_misalignment_official (commit ea0630e).
"""

import difflib
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[3]
OFFICIAL = AUDIT / "agentic_misalignment_official"
PORT_SRC = AUDIT / "inspect_evals" / "src"

sys.path.insert(0, str(PORT_SRC))
# The official script does sys.path.insert for its templates dir itself; we add scripts/.
sys.path.insert(0, str(OFFICIAL / "scripts"))

import generate_prompts as official  # noqa: E402  (official scripts/generate_prompts.py)

from inspect_evals.agentic_misalignment.prompt_generator import (  # noqa: E402
    ALIGNMENT_FAKING_WARNING,
    generate_prompts,
)

import yaml  # noqa: E402

AF_CFG = yaml.safe_load(
    open(OFFICIAL / "configs" / "alignment_faking_experiment_250611.yaml")
)["global"]["alignment_faking"]

SCENARIOS = ["blackmail", "leaking", "murder"]
GOAL_TYPES = ["explicit", "latent", "none", "ambiguous", "swap"]
GOAL_VALUES = [
    "america", "global", "safety", "acceleration",
    "ethical", "pragmatic", "individualism", "collectivism", "ambiguous",
]
URGENCY = ["replacement", "restriction", "none"]


def official_prompts(scenario, goal_type, goal_value, urgency, extra, prod, af):
    buf = io.StringIO()
    with redirect_stdout(buf):
        sysp = official.generate_system_prompt(
            scenario, goal_type, goal_value, urgency,
            extra_system_instructions=extra if extra else False,
            prod=prod,
            alignment_faking_config=AF_CFG if af else None,
        )
        email = official.generate_email_content(scenario, goal_type, goal_value, urgency)
        user = official.generate_user_prompt_fixed()
    return sysp, user, email


def port_prompts(scenario, goal_type, goal_value, urgency, extra, prod, af):
    buf = io.StringIO()
    with redirect_stdout(buf):
        p = generate_prompts(
            scenario=scenario, goal_type=goal_type, goal_value=goal_value,
            urgency_type=urgency, extra_system_instructions=extra,
            prod_flag=prod,
            alignment_faking_warning=ALIGNMENT_FAKING_WARNING if af else None,
        )
    return p.system_prompt, p.user_prompt, p.email_content


def short_diff(a, b, label):
    d = list(difflib.unified_diff(a.splitlines(), b.splitlines(), "official/" + label, "port/" + label, lineterm="", n=0))
    return "\n".join(d[:14]) + ("\n..." if len(d) > 14 else "")


def main():
    n = 0
    same = 0
    diffs = {}  # signature -> list of condition ids
    official_errors = {}
    for scenario in SCENARIOS:
        for goal_type in GOAL_TYPES:
            gvs = ["none"] if goal_type in ("none", "ambiguous") else GOAL_VALUES
            for goal_value in gvs:
                for urgency in URGENCY:
                    for prod in (False, True):
                        for extra in (None, "dont", "goal"):
                            for af in (False, True):
                                cid = f"{scenario}_{goal_type}-{goal_value}_{urgency}" + ("_prod" if prod else "") + (f"_extra={extra}" if extra else "") + ("_af" if af else "")
                                n += 1
                                try:
                                    o = official_prompts(scenario, goal_type, goal_value, urgency, extra, prod, af)
                                except Exception as e:  # noqa: BLE001
                                    official_errors.setdefault(f"{type(e).__name__}: {e}", []).append(cid)
                                    continue
                                p = port_prompts(scenario, goal_type, goal_value, urgency, extra, prod, af)
                                if o == p:
                                    same += 1
                                    continue
                                sig = []
                                for label, oa, pa in zip(("system", "user", "email"), o, p):
                                    if oa != pa:
                                        sig.append(short_diff(oa, pa, label))
                                diffs.setdefault("\n".join(sig), []).append(cid)

    print(f"conditions compared: {n}; identical: {same}; differing: {n - same - sum(len(v) for v in official_errors.values())}; official raised: {sum(len(v) for v in official_errors.values())}")
    print()
    print("=== OFFICIAL RAISED (port produced output; official could not) ===")
    for err, cids in official_errors.items():
        print(f"[{len(cids)} conditions] {err}")
        print("   e.g.", ", ".join(cids[:3]))
    print()
    print("=== DISTINCT DIFF SIGNATURES (official -> port) ===")
    for sig, cids in sorted(diffs.items(), key=lambda kv: -len(kv[1])):
        print(f"--- {len(cids)} conditions, e.g. {', '.join(cids[:4])}")
        print(sig)
        print()


if __name__ == "__main__":
    main()
