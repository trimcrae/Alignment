"""Reproductions for inspect_ai.solver._multiple_choice / inspect_ai.scorer._choice.

Target: inspect_ai 0.3.260.dev154+gce5617d35 as installed in inspect_evals/.venv
(byte-identical to upstream commit ce5617d35).

Run:
  cd <audit>/findings/repro/inspect_core
  ../../../inspect_evals/.venv/bin/python -m pytest test_choice_scorer.py -q
"""

import sys
from pathlib import Path
from random import Random

sys.path.insert(0, str(Path(__file__).parent))

import pytest  # noqa: E402
from _helpers import run_scorer, task_state  # noqa: E402

from inspect_ai._util.answer import answer_character, answer_index  # noqa: E402
from inspect_ai.dataset import MemoryDataset, Sample  # noqa: E402
from inspect_ai.model import ChatMessageAssistant, ChatMessageUser  # noqa: E402
from inspect_ai.scorer import CORRECT, INCORRECT, Target, choice, includes  # noqa: E402
from inspect_ai.solver._multiple_choice import (  # noqa: E402
    SINGLE_ANSWER_TEMPLATE,
    parse_answers,
    pretend_we_didnt_shuffle,
    set_choices_based_on_generated_response,
)

FOUR = ["Paris", "Berlin", "London", "Rome"]


def answered(completion: str, choices: list[str], multiple: bool = False):
    """Run the full solver post-generate path, then return the TaskState."""
    state = task_state(completion, choices)
    answers = parse_answers(state, multiple)
    if answers:
        set_choices_based_on_generated_response(state, answers)
    return state


# ---------------------------------------------------------------------------
# C-1  parse_answers rejects the common "decorated letter" formats
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "completion",
    [
        "ANSWER: (B)",
        "ANSWER: **B**",
        "ANSWER: $B$",
        "ANSWER: B is right",
        "I think ANSWER: B is right",
        "ANSWER: AB",  # two letters when multiple_correct is False
    ],
)
def test_decorated_or_embedded_letters_do_not_parse(completion):
    """A model that bolds, parenthesises or LaTeX-wraps its letter scores 0.

    `parse_answers` captures with [A-Za-z\\d ,]+ and then requires the whole
    capture to be an allowed option, so any wrapper character kills the match
    and the sample is scored INCORRECT (not unscored).
    """
    assert parse_answers(task_state(completion, FOUR), False) == set()
    state = answered(completion, FOUR)
    assert run_scorer(choice(), state, "B").value == INCORRECT


@pytest.mark.parametrize(
    "completion,expected",
    [
        ("ANSWER: A", {"A"}),
        ("answer: a", {"A"}),
        ("ANSWER: A.", {"A"}),
        ("ANSWER: A,", {"A"}),
        ("ANSWER: A\nANSWER: B", {"B"}),  # last line wins
    ],
)
def test_accepted_single_answer_forms(completion, expected):
    assert parse_answers(task_state(completion, FOUR), False) == expected


@pytest.mark.parametrize(
    "completion,expected",
    [
        ("ANSWER: A, B", {"A", "B"}),
        ("ANSWER: A and B", {"A", "B"}),
        ("ANSWER: AB", {"A", "B"}),
        ("ANSWER: A,B,", {"A", "B"}),
        ("ANSWER: ABCD", {"A", "B", "C", "D"}),
    ],
)
def test_accepted_multiple_answer_forms(completion, expected):
    assert parse_answers(task_state(completion, FOUR), True) == expected


def test_listing_every_option_is_not_credited_unless_all_are_correct():
    """choice() is all-or-nothing, so "select everything" does not pay off."""
    state = answered("ANSWER: ABCD", FOUR, multiple=True)
    assert run_scorer(choice(), state, "B").value == INCORRECT
    assert run_scorer(choice(), state, "A,B,C,D").value == CORRECT


def test_refusal_and_empty_output_are_scored_incorrect_not_unscored():
    for completion in ["I refuse to answer.", ""]:
        state = answered(completion, FOUR)
        assert run_scorer(choice(), state, "A").value == INCORRECT


# ---------------------------------------------------------------------------
# C-2  an empty target credits a non-answer
# ---------------------------------------------------------------------------


def test_empty_target_credits_a_model_that_did_not_answer():
    """Target("") -> no target positions; an unparsed answer -> no selections.

    [] == [] so the sample is scored CORRECT.
    """
    state = answered("I refuse to answer.", FOUR)
    assert run_scorer(choice(), state, "").value == CORRECT
    # ... while a model that *does* answer is marked wrong
    state2 = answered("ANSWER: A", FOUR)
    assert run_scorer(choice(), state2, "").value == INCORRECT


# ---------------------------------------------------------------------------
# C-3  targets that are not bare letters are silently mis-mapped
# ---------------------------------------------------------------------------


def test_target_as_answer_text_is_silently_incorrect():
    """A dataset whose target is the answer *text* scores 0% with no error.

    _score_target maps each character of target.text through answer_index, so
    "Paris" becomes indices [15, 0, 17, 8, 18] -- out of range for a 4-choice
    question -- and every sample is INCORRECT.
    """
    state = answered("ANSWER: A", FOUR)
    result = run_scorer(choice(), state, "Paris")
    assert result.value == INCORRECT
    assert result.answer == "A"  # the model did pick the right choice


def test_target_with_a_prose_separator_is_silently_incorrect():
    """target "A and B": the letters of "and" are consumed as answer letters."""
    state = answered("ANSWER: A,B", FOUR, multiple=True)
    assert run_scorer(choice(), state, "A and B").value == INCORRECT
    # the same target written the documented way works
    state2 = answered("ANSWER: A,B", FOUR, multiple=True)
    assert run_scorer(choice(), state2, "A,B").value == CORRECT


def test_zero_based_numeric_target_maps_onto_choice_Z():
    """answer_index("0") == 25 == answer_index("Z"), but answer_character never
    emits "0", so a 0-based numeric target silently addresses choice 26."""
    assert answer_index("0") == 25 == answer_index("Z")
    assert answer_character(25) == "Z"
    state = answered("ANSWER: A", FOUR)
    assert run_scorer(choice(), state, "0").value == INCORRECT


@pytest.mark.parametrize("target", ["AB", "A,B", "A, B"])
def test_dataset_shuffle_choices_raises_on_a_multi_answer_string_target(target):
    """MemoryDataset._remap_target passes the whole string to answer_index."""
    dataset = MemoryDataset(samples=[Sample(input="q", choices=["a", "b", "c"], target=target)])
    with pytest.raises((TypeError, ValueError)):
        dataset.shuffle_choices(seed=1)
    # the list form is handled
    dataset2 = MemoryDataset(
        samples=[Sample(input="q", choices=["a", "b", "c"], target=["A", "B"])]
    )
    dataset2.shuffle_choices(seed=1)


# ---------------------------------------------------------------------------
# C-4  >= 36 choices: numeric labels of two digits are mis-mapped
# ---------------------------------------------------------------------------

THIRTY_SIX = [f"opt{i}" for i in range(36)]


def test_36_choices_correct_answer_is_scored_incorrect():
    """answer_character(35) == "10"; _score_target splits it into "1" and "0"."""
    assert answer_character(35) == "10"
    state = answered("ANSWER: 10", THIRTY_SIX)
    assert [i for i, c in enumerate(state.choices) if c.correct] == [35]  # solver is right
    assert run_scorer(choice(), state, "10").value == INCORRECT  # scorer is wrong


def test_36_choices_wrong_answer_is_credited():
    """Target "10" resolves to {answer_index("1"), answer_index("0")} == {26, 25},
    so a model that picks choices "Z" and "1" is scored CORRECT."""
    state = answered("ANSWER: Z,1", THIRTY_SIX, multiple=True)
    assert [i for i, c in enumerate(state.choices) if c.correct] == [25, 26]
    result = run_scorer(choice(), state, "10")
    assert result.value == CORRECT
    assert result.answer == "Z, 1"


# ---------------------------------------------------------------------------
# C-5  shuffling: the target mapping itself is correct
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("seed", list(range(8)))
def test_solver_side_shuffle_round_trips(seed):
    """Positive control: Choices.shuffle + unshuffle_choices in choice() map the
    model's shuffled letter back onto the unshuffled target correctly."""
    state = task_state("", FOUR)
    state.choices.shuffle(Random(seed))
    letter = "ABCD"[[c.value for c in state.choices].index("Paris")]
    state.output.completion = f"ANSWER: {letter}"
    set_choices_based_on_generated_response(state, parse_answers(state, False))
    assert run_scorer(choice(), state, "A").value == CORRECT


def test_dataset_shuffle_choices_is_unseeded_by_default():
    """dataset.shuffle_choices() uses random.Random(None): not reproducible."""
    runs = []
    for _ in range(2):
        dataset = MemoryDataset(
            samples=[Sample(input="q", choices=list("abcdefghij"), target="A")]
        )
        dataset.shuffle_choices()
        runs.append((list(dataset[0].choices or []), dataset[0].target))
    assert runs[0] != runs[1], f"collision (1 in 3.6M), rerun: {runs}"


def test_pretend_we_didnt_shuffle_overwrites_the_real_completion():
    """The docstring says it "just rewrites message history", but it also
    replaces state.output.completion, which every other scorer reads."""
    state = task_state("", FOUR)
    state.messages = [
        ChatMessageUser(content="q"),
        ChatMessageAssistant(content="Reasoning about Paris ... ANSWER: B"),
    ]
    state.output.completion = "Reasoning about Paris ... ANSWER: B"
    state.choices.shuffle(Random(0))
    set_choices_based_on_generated_response(state, parse_answers(state, False))
    pretend_we_didnt_shuffle(state, "q", SINGLE_ANSWER_TEMPLATE)
    assert state.output.completion == "ANSWER: A"
    # a second scorer on the same task now sees synthesized text
    assert run_scorer(includes(), state, Target("Paris")).value == INCORRECT


def test_double_shuffle_corrupts_original_position():
    """Choices.shuffle writes original_position relative to the *current* order,
    so shuffling twice loses the mapping back to the sample's order."""
    state = task_state("", FOUR)
    state.choices.shuffle(Random(0))
    state.choices.shuffle(Random(1))
    recorded = [c.original_position for c in state.choices]
    truth = [FOUR.index(c.value) for c in state.choices]
    assert recorded != truth, (recorded, truth)


def test_shuffled_explanation_records_what_the_model_actually_saw():
    state = task_state("", FOUR)
    state.choices.shuffle(Random(0))
    shown = [c.value for c in state.choices]
    letter = "ABCD"[shown.index("Paris")]
    state.output.completion = f"ANSWER: {letter}"
    set_choices_based_on_generated_response(state, parse_answers(state, False))
    explanation = run_scorer(choice(), state, "A").explanation or ""
    assert "Choices were shuffled before generating a response" in explanation
    assert f"{letter}) Paris" in explanation
    assert f"Shuffled answer:\nANSWER: {letter}" in explanation
