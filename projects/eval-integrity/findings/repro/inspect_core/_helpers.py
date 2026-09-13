"""Shared helpers for the inspect_ai core-scoring reproductions.

Everything here runs offline: scorers are awaited directly, no eval() and no
network-backed tokenizer.
"""

import asyncio
from typing import Any

from inspect_ai.model import ModelName, ModelOutput
from inspect_ai.scorer import Score, Target
from inspect_ai.scorer._metric import SampleScore
from inspect_ai.solver import TaskState


def task_state(model_output: str = "", choices: list[str] | None = None) -> TaskState:
    return TaskState(
        choices=choices,
        epoch=0,
        input=[],
        messages=[],
        model=ModelName(model="fake/model"),
        output=ModelOutput.from_content(model="model", content=model_output),
        sample_id=0,
    )


def run_scorer(scorer: Any, state: TaskState, target: Any) -> Score:
    if not isinstance(target, Target):
        target = Target(target)
    return asyncio.run(scorer(state, target))


def sample_scores(values: list[Any], metadata: list[dict] | None = None) -> list[SampleScore]:
    return [
        SampleScore(
            score=Score(value=v),
            sample_id=i,
            sample_metadata=(metadata[i] if metadata is not None else None),
        )
        for i, v in enumerate(values)
    ]


def stub_tokenizer() -> None:
    """Make mockllm usable offline.

    mockllm counts input tokens with tiktoken, which downloads its BPE table on
    first use. The sandbox has no network, so install a whitespace tokenizer.
    """
    import tiktoken

    class _Enc:
        def encode(self, text, **kwargs):  # noqa: ANN001, ANN003
            return text.split()

    tiktoken.get_encoding = lambda name: _Enc()  # type: ignore[assignment]
