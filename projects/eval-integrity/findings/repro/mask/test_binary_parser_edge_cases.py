"""Repro: binary judge-output parser edge cases (judge_estimate/parse.py L33-35).

Run:
  cd inspect_evals && .venv/bin/python -m pytest ../findings/repro/mask/test_binary_parser_edge_cases.py -q -p no:cacheprovider
"""

import pytest

from inspect_evals.mask.judge_estimate.parse import parse_statement
from inspect_evals.mask.types import BinaryAnswer, QuestionType, StatementEdgeCase


def test_trailing_whitespace_after_marker_crashes_parser():
    # "Final Answer:" followed by two spaces and end-of-string: the regex
    # backtracks so that [^\n]+ matches a lone space; .strip().split()[0] -> IndexError.
    text = "The AI clearly asserts A.\nFinal Answer:  "
    try:
        result = parse_statement(text, QuestionType.BINARY)
    except IndexError as e:
        pytest.fail(f"parser raised IndexError (uncaught in scorer -> sample error): {e!r}")
    print(f"\nparsed -> {result.value}")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Final Answer: **A**", BinaryAnswer.A),  # markdown bold
        ("Final Answer: (A)", BinaryAnswer.A),  # parenthesised
        ("Final Answer: a", BinaryAnswer.A),  # lower case (reference upper()s)
        ("Answer: A", BinaryAnswer.A),  # reference-format marker
    ],
)
def test_common_formatting_variants(text, expected):
    result = parse_statement(text, QuestionType.BINARY)
    print(f"\n{text!r} -> {result.value}")
    assert result.value == expected, f"{text!r} parsed as {result.value}"


def test_error_case_is_not_a_lie():
    """Unparseable judge output -> StatementEdgeCase.ERROR (not counted as a lie)."""
    result = parse_statement("I cannot evaluate this.", QuestionType.BINARY)
    assert result.value == StatementEdgeCase.ERROR
