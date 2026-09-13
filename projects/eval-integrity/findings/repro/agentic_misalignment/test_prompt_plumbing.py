"""Low-severity prompt plumbing checks against the official runner.

1. User message assembly: official run_experiments.py line 318 joins with "\n\n"; the port's
   agentic_misalignment.py line 99 joins with "\n" (one blank line fewer before the emails).
2. Alignment-faking notice: the port's ALIGNMENT_FAKING_WARNING has two extra leading newlines
   compared with configs/alignment_faking_experiment_250611.yaml.
3. Inherited upstream template bug: blackmail/murder `restriction` emails reference
   ${direction_modifier}, which the pro_safety section of safety_vs_acceleration.md does not
   define, so the literal "${direction_modifier}" reaches the model (identical in the official).

Tests 1-2 assert byte-equality with the official and FAIL (whitespace only). Test 3 asserts the
placeholder is filled and FAILS; it is an upstream defect the port inherits verbatim.
"""

import sys
from pathlib import Path

import pytest
import yaml

from inspect_evals.agentic_misalignment import agentic_misalignment
from inspect_evals.agentic_misalignment.prompt_generator import (
    ALIGNMENT_FAKING_WARNING,
    generate_prompts,
)

AUDIT = Path(__file__).resolve().parents[3]
OFFICIAL = AUDIT / "agentic_misalignment_official"


def test_user_message_join_matches_official_runner():
    task = agentic_misalignment()
    port_user_msg = task.dataset[0].input[0].content
    p = generate_prompts("blackmail", "explicit", "america", "replacement", None, False, None)
    official_user_msg = p.user_prompt + "\n\n" + p.email_content  # run_experiments.py:318
    i = port_user_msg.find("<email>")
    print(f"\nport   ...{port_user_msg[i-12:i]!r}")
    print(f"official...{official_user_msg[i-12:i+1]!r}")
    assert port_user_msg == official_user_msg


def test_alignment_faking_warning_matches_yaml():
    cfg = yaml.safe_load(open(OFFICIAL / "configs" / "alignment_faking_experiment_250611.yaml"))
    official = cfg["global"]["alignment_faking"]["warning_text"]
    print(f"\nofficial={official!r}\nport    ={ALIGNMENT_FAKING_WARNING!r}")
    assert ALIGNMENT_FAKING_WARNING == official


@pytest.mark.parametrize("scenario", ["blackmail", "murder"])
def test_direction_modifier_is_filled_for_safety_restriction(scenario):
    p = generate_prompts(scenario, "explicit", "safety", "restriction", None, False, None)
    hit = [ln for ln in p.email_content.splitlines() if "${direction_modifier}" in ln]
    print(f"\n{scenario}: {hit[:1]}")
    assert not hit, "literal ${direction_modifier} sent to the model (inherited from upstream)"
