"""Reproductions for the text-matching scorers.

inspect_ai.scorer._match (match, includes), _common (match_str),
_pattern (pattern), _answer (answer), _classification (exact, f1).

Target: inspect_ai 0.3.260.dev154+gce5617d35.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pytest  # noqa: E402
from _helpers import run_scorer, task_state  # noqa: E402

from inspect_ai.scorer import (  # noqa: E402
    CORRECT,
    INCORRECT,
    NOANSWER,
    answer,
    exact,
    f1,
    includes,
    match,
    pattern,
)

ENUMERATES_EVERYTHING = "The options are A) 3  B) 4  C) 9  D) 12"


def value(scorer, completion: str, target):
    return run_scorer(scorer, task_state(completion), target).value


# ---------------------------------------------------------------------------
# M-1  match(location="end") credits suffix coincidences (numeric=False default)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "completion,target",
    [
        ("The answer is 1234", "4"),
        ("the value is 25", "5"),
        ("the answer is 42", "2"),
        ("...ending in a banana", "a"),
        ("Rome", "e"),
    ],
)
def test_match_end_credits_a_wrong_answer_that_merely_ends_with_the_target(
    completion, target
):
    """match() is a suffix test on the raw text, so any completion whose last
    characters happen to be the target is CORRECT."""
    assert value(match(), completion, target) == CORRECT


@pytest.mark.parametrize(
    "completion,target,expected",
    [
        ("The answer is 1234", "4", INCORRECT),
        ("the value is 25", "5", INCORRECT),
        ("the answer is 42", "42", CORRECT),
    ],
)
def test_numeric_true_closes_the_digit_suffix_hole(completion, target, expected):
    assert value(match(numeric=True), completion, target) == expected


# ---------------------------------------------------------------------------
# M-2  a completion that lists every option
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("target", ["3", "4", "9", "12"])
def test_any_and_includes_credit_a_completion_that_lists_every_option(target):
    assert value(match("any"), ENUMERATES_EVERYTHING, target) == CORRECT
    assert value(includes(), ENUMERATES_EVERYTHING, target) == CORRECT
    assert value(match("any", numeric=True), ENUMERATES_EVERYTHING, target) == CORRECT


def test_match_end_only_credits_the_last_option_in_such_a_completion():
    assert value(match(), ENUMERATES_EVERYTHING, "12") == CORRECT
    for target in ["3", "4", "9"]:
        assert value(match(), ENUMERATES_EVERYTHING, target) == INCORRECT


# ---------------------------------------------------------------------------
# M-3  numeric=True strips punctuation from the target but not the completion
#      when the target is not itself a number
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "completion,target",
    [
        ("The price is 1,000 dollars", "1,000 dollars"),
        ("the variable is x_1", "x_1"),
    ],
)
def test_numeric_true_breaks_non_numeric_targets_containing_stripped_characters(
    completion, target
):
    """match_str() applies strip_numeric_punctuation to the target
    unconditionally, but to the completion only when the target parses as a
    number. A literally identical answer therefore fails to match."""
    assert value(match(numeric=True), completion, target) == INCORRECT
    assert value(match(), completion, target) == CORRECT  # numeric=False is fine


def test_numeric_comma_stripping_concatenates_a_list_of_digits():
    """'1,2,3' becomes '123', so a model listing three numbers is credited for
    the three-digit target."""
    assert value(match(numeric=True), "The digits are 1,2,3", "123") == CORRECT
    assert value(match(numeric=True), "The total is 1,234", "1234") == CORRECT


def test_numeric_does_not_accept_a_percentage(  # documented in the docstring
):
    assert value(match(numeric=True), "60%", "60") == INCORRECT


# ---------------------------------------------------------------------------
# M-4  pattern()
# ---------------------------------------------------------------------------


def test_pattern_with_no_capture_group_is_always_incorrect():
    """Documented ("at least one regex group is required"), but the failure mode
    is a silent INCORRECT on a pattern that did match."""
    assert value(pattern(r"Yes|No"), "Yes", "Yes") == INCORRECT
    assert value(pattern(r"(Yes|No)"), "Yes", "Yes") == CORRECT


def test_pattern_no_match_is_noanswer_which_still_counts_as_zero():
    from inspect_ai.scorer import value_to_float

    assert value(pattern(r"(Yes|No)"), "Maybe", "Yes") == NOANSWER
    assert value_to_float()(NOANSWER) == 0.0


# ---------------------------------------------------------------------------
# M-5  answer("line") is punctuation- and whitespace-sensitive
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "completion,expected",
    [
        ("ANSWER: Paris", CORRECT),
        ("ANSWER: Paris\n", CORRECT),
        ("ANSWER: Paris.", INCORRECT),  # a trailing full stop
        ("ANSWER: Paris  ", INCORRECT),  # trailing spaces
        ("ANSWER: Paris.\n", INCORRECT),
        ("ANSWER: Paris\nThanks!", NOANSWER),  # not the last line
    ],
)
def test_answer_line_is_sensitive_to_trailing_punctuation_and_spaces(
    completion, expected
):
    """ANSWER_PATTERN_LINE captures [^\\n]+ greedily and pattern() compares the
    capture to the target by equality, with no trimming."""
    assert value(answer("line"), completion, "Paris") == expected


@pytest.mark.parametrize(
    "completion,expected",
    [
        ("ANSWER: yes", CORRECT),
        ("ANSWER: yes.", CORRECT),  # WORD's lookahead absorbs one punctuation mark
        ("ANSWER: Yes", CORRECT),
        ("ANSWER: yes, definitely", NOANSWER),
    ],
)
def test_answer_word(completion, expected):
    assert value(answer("word"), completion, "yes") == expected


@pytest.mark.parametrize(
    "completion,expected",
    [
        ("ANSWER: A", CORRECT),
        ("ANSWER: A.", CORRECT),
        ("ANSWER: **A**", NOANSWER),
        ("ANSWER: AB", NOANSWER),
    ],
)
def test_answer_letter(completion, expected):
    assert value(answer("letter"), completion, "A") == expected


# ---------------------------------------------------------------------------
# M-6  exact()
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "completion,expected",
    [
        ("Paris", CORRECT),
        (" paris. ", CORRECT),  # normalisation strips case and edge punctuation
        ("the Paris", CORRECT),  # articles are removed
        ("The answer is Paris", INCORRECT),
    ],
)
def test_exact_requires_the_whole_normalised_completion(completion, expected):
    assert value(exact(), completion, "Paris") == expected


# ---------------------------------------------------------------------------
# M-7  f1()
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "completion,expected",
    [
        ("yes", 1.0),
        ("no", 0.0),
        ("yes no", 0.67),  # naming both labels
        ("yes or no", 0.5),
    ],
)
def test_f1_gives_partial_credit_for_naming_every_candidate_answer(completion, expected):
    """With a one-token target, an answer that enumerates both labels scores
    0.67 -- two thirds of a correct answer -- on every sample."""
    assert value(f1(), completion, "yes") == expected


@pytest.mark.parametrize("target", ["the", "a", "an", "."])
def test_f1_scores_an_empty_completion_1_0_when_the_target_normalises_to_nothing(target):
    """_f1() hardcodes precision=1.0 for an empty answer bag and recall=1.0 for
    an empty target bag, so empty-vs-empty is a perfect score."""
    assert value(f1(), "", target) == 1.0
    assert value(f1(), "Paris", target) == 0.0


def test_f1_empty_completion_against_a_real_target_is_zero():
    assert value(f1(), "", "Paris") == 0.0
