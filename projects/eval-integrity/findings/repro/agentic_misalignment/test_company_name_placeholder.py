"""Repro: extra_system_instructions leaves a literal "{company_name}" in the system prompt.

prompt_generator.generate_system_prompt builds the extra instructions with str.format-style
braces ("{company_name}") but fills them with string.Template.safe_substitute, which only
understands "$name"/"${name}". No template variable named company_name exists anyway.

These tests assert the *intended* behaviour, so they FAIL on the current port; the failure
output is the reproduction.
"""

import pytest

from inspect_evals.agentic_misalignment.prompt_generator import generate_prompts

COMPANY = {"blackmail": "SummitBridge", "leaking": "NovaStar", "murder": "SummitBridge"}


@pytest.mark.parametrize("scenario", ["blackmail", "leaking", "murder"])
@pytest.mark.parametrize("extra", ["dont", "goal"])
def test_extra_instructions_name_the_company(scenario, extra):
    p = generate_prompts(
        scenario=scenario,
        goal_type="explicit",
        goal_value="america",
        urgency_type="replacement",
        extra_system_instructions=extra,
        prod_flag=False,
        alignment_faking_warning=None,
    )
    line = next(
        ln for ln in p.system_prompt.splitlines()
        if "company_name" in ln or COMPANY[scenario] in ln and ("disclose" in ln or "welfare" in ln)
    )
    print(f"\n[{scenario}/{extra}] system prompt line: {line!r}")
    assert "{company_name}" not in p.system_prompt, (
        f"literal placeholder emitted to the model: {line!r}"
    )
