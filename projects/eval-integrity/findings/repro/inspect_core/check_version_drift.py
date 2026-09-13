"""Show that the same completion parses differently on two inspect_ai commits.

Run twice from the audit root:

  inspect_evals/.venv/bin/python findings/repro/inspect_core/check_version_drift.py
  PYTHONPATH=inspect_ai_src/src inspect_evals/.venv/bin/python \
      findings/repro/inspect_core/check_version_drift.py

The first run uses the installed 0.3.260.dev154+gce5617d35; the second uses the
upstream main clone (inspect_ai_src, commit f6719bb). inspect_evals pins only
"inspect_ai >= 0.3.259", so which behaviour an eval gets depends on the day the
environment was built.
"""

import asyncio
import math

import tiktoken

import inspect_ai.solver._multiple_choice as mc
from inspect_ai.model import ModelName, ModelOutput
from inspect_ai.scorer import Target, choice
from inspect_ai.solver import TaskState

FOUR = ["Paris", "Berlin", "London", "Rome"]


def state(completion: str, choices: list[str]) -> TaskState:
    return TaskState(
        choices=choices,
        epoch=0,
        input=[],
        messages=[],
        model=ModelName(model="fake/model"),
        output=ModelOutput.from_content(model="model", content=completion),
        sample_id=0,
    )


def score(completion: str, target: str, choices: list[str] = FOUR) -> str:
    st = state(completion, choices)
    answers = mc.parse_answers(st, len(target.replace(",", "").strip()) > 1)
    if answers:
        mc.set_choices_based_on_generated_response(st, answers)
    return str(asyncio.run(choice()(st, Target(target))).value)


print("module:", mc.__file__)
for completion, target in [
    ("ANSWER: B", "B"),
    ("ANSWER: (B)", "B"),
    ("ANSWER: **B**", "B"),
    ("ANSWER: $B$", "B"),
]:
    print(f"  {completion!r:18} target {target!r} -> {score(completion, target)}")

THIRTY_SIX = [f"opt{i}" for i in range(36)]
print(f"  {'ANSWER: 10'!r:18} target '10' (36 choices) -> {score('ANSWER: 10', '10', THIRTY_SIX)}")
print(f"  {'ANSWER: Z,1'!r:18} target '10' (36 choices) -> {score('ANSWER: Z,1', '10', THIRTY_SIX)}")
print(f"  {'I refuse.'!r:18} target ''   -> {score('I refuse.', '')}")


# --- model_graded_qa grade extraction (finding 1) ---------------------------


class _Enc:
    def encode(self, text, **kwargs):  # noqa: ANN001, ANN003
        return text.split()


tiktoken.get_encoding = lambda name: _Enc()  # type: ignore[assignment]

from inspect_ai.model import ChatMessageUser, ModelOutput, get_model  # noqa: E402
from inspect_ai.scorer import model_graded_qa  # noqa: E402


def grade(grader_completion: str) -> str:
    grader = get_model(
        "mockllm/model",
        custom_outputs=[ModelOutput.from_content("mockllm/model", grader_completion)],
    )
    st = TaskState(
        choices=None,
        epoch=0,
        input="What is the capital of France?",
        messages=[ChatMessageUser(content="What is the capital of France?")],
        model=ModelName(model="fake/model"),
        output=ModelOutput.from_content(model="model", content="Paris"),
        sample_id=0,
    )
    v = asyncio.run(model_graded_qa(model=grader)(st, Target("Paris"))).value
    return "UNSCORED" if isinstance(v, float) and math.isnan(v) else str(v)


print()
for completion in [
    "GRADE: C",
    "GRADE: Correct",
    "GRADE: Cannot determine",
    "GRADE: Contradicts the expert answer",
    "GRADE: Close enough",
    "GRADE: Insufficient information",
]:
    print(f"  {completion!r:40} -> {grade(completion)}")
