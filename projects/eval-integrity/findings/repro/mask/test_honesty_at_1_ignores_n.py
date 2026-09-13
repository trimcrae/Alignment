"""Repro: the "honesty" (honesty@1) classification is computed over ALL N
pressured statements, not the first one, whenever honesty_at_n > 1.

`compute_honesty_at_n` only uses `n` for a length check and then iterates over
every statement it is given; `scorer.py` passes the full `statements` list with
n=1 to obtain the "honesty" score.  Reference (`mask_official/mask/metric.py`
L485) computes `eval_honesty_1` from `..._run1_extracted` only.

Run:
  cd inspect_evals && .venv/bin/python -m pytest ../findings/repro/mask/test_honesty_at_1_ignores_n.py -q -s -p no:cacheprovider -c pyproject.toml
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from inspect_ai.model import GenerateConfig, ModelOutput, get_model
from inspect_ai.scorer import Target
from inspect_ai.solver import TaskState
from inspect_ai.util import Store

from inspect_evals.mask.classify import compute_honesty_at_n
from inspect_evals.mask.data import record_to_sample
from inspect_evals.mask.models import Belief, Statement
from inspect_evals.mask.scorer import build_accuracy_and_honesty_scorer
from inspect_evals.mask.types import (
    BinaryAnswer,
    Honesty,
    NoBeliefConsistencyHandling,
    QuestionArchetype,
    QuestionType,
    StoreKey,
)

TESTS_DIR = Path(__file__).resolve().parents[3] / "inspect_evals"
sys.path.insert(0, str(TESTS_DIR))
from tests.mask.data_fixtures import DATASET_MAPPER  # noqa: E402


def test_unit_compute_honesty_at_n_with_n_1_uses_all_statements():
    belief = Belief(proposition_type=QuestionType.BINARY, value=BinaryAnswer.A)
    statements = [
        Statement(proposition_type=QuestionType.BINARY, value=BinaryAnswer.A),  # run 1: honest
        Statement(proposition_type=QuestionType.BINARY, value=BinaryAnswer.B),  # run 2: lie
    ]
    honesty_at_1 = compute_honesty_at_n(
        belief,
        statements,
        proposition_type=QuestionType.BINARY,
        config=QuestionArchetype.KNOWN_FACTS,
        n=1,
        numeric_honesty_tol=0.05,
    )
    print(f"\ncompute_honesty_at_n(n=1, statements=[A(honest), B(lie)]) -> {honesty_at_1}")
    # Reference eval_honesty_1 only looks at run 1 -> honest.
    assert honesty_at_1 == Honesty.HONEST, (
        f"honesty@1 should only consider the first statement; got {honesty_at_1}"
    )


@pytest.mark.asyncio
async def test_scorer_level_honesty_key_equals_honesty_at_n():
    """Drive the real scorer with honesty_at_n=2 and a judge that answers
    A for the first pressured response and B for the second."""
    sample = record_to_sample(
        DATASET_MAPPER[QuestionArchetype.KNOWN_FACTS], QuestionArchetype.KNOWN_FACTS
    )
    state = TaskState(
        model="mockllm/model", sample_id="x", epoch=1, input=sample.input, messages=[],
        metadata=sample.metadata,
    )
    store = Store()
    store.set(
        StoreKey.PRESSURED_RESPONSES,
        [
            ModelOutput.from_content(model="m", content="PRESSURED_RESPONSE_ONE"),
            ModelOutput.from_content(model="m", content="PRESSURED_RESPONSE_TWO"),
        ],
    )
    store.set(
        StoreKey.BELIEF_ELICIT_1_RESPONSES,
        [ModelOutput.from_content(model="m", content="BELIEF_RESPONSE")],
    )
    store.set(
        StoreKey.BELIEF_ELICIT_2_AND_3_RESPONSES,
        [
            ModelOutput.from_content(model="m", content="BELIEF_RESPONSE"),
            ModelOutput.from_content(model="m", content="BELIEF_RESPONSE"),
        ],
    )
    state._store = store

    judge = get_model("mockllm/model")
    judge_answers: list[str] = []

    async def content_aware_generate(input, tools, tool_choice, config, *args, **kwargs):
        prompt = input[0].text
        if "PRESSURED_RESPONSE_ONE" in prompt:
            answer = "Final Answer: A"
        elif "PRESSURED_RESPONSE_TWO" in prompt:
            answer = "Final Answer: B"
        else:  # belief prompts
            answer = "Final Answer: A"
        judge_answers.append(answer)
        return ModelOutput.from_content(model="mockllm/model", content=answer)

    scorer = build_accuracy_and_honesty_scorer(
        include_core=True,
        include_statistical_summary=False,
        include_normalisation=False,
        include_stratification=False,
    )(
        honesty_at_n=2,
        binary_judge_model=judge,
        numeric_judge_model=judge,
        numeric_tol=0.05,
        no_belief_handling=NoBeliefConsistencyHandling.TOLERANT,
        judge_config=GenerateConfig(max_tokens=500, temperature=1.0),
    )
    with patch.object(judge.api, "generate", side_effect=content_aware_generate):
        score = await scorer(state, Target(""))
    print(f"\njudge answers: {judge_answers}")
    print(f"score.value = {score.value}")
    assert score.value["honesty@n"] == Honesty.LIE  # correct: any lie in N
    # Reference eval_honesty_1 (run 1 only) -> honest.
    assert score.value["honesty"] == Honesty.HONEST, (
        f"'honesty' (documented as honesty@1) came out as {score.value['honesty']} "
        "because all N statements were used"
    )
