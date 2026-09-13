"""Repro: control_arena.scorers._metrics.accuracy keeps NOANSWER samples in the denominator.

The module docstring says these metrics are "adapted to handle NOANSWER in
responses" and to_floats() returns [] for NOANSWER so it is dropped from the
numerator -- but accuracy() divides by len(scores), i.e. the NOANSWER samples
are still counted. The paired stderr() divides by len(valid_scores).
"""

from inspect_ai.scorer import CORRECT, INCORRECT, NOANSWER, SampleScore, Score

from control_arena.scorers._metrics import accuracy, stderr


def ss(value):
    return SampleScore(score=Score(value=value), sample_id="x")


def test_noanswer_is_counted_as_incorrect_by_accuracy():
    acc = accuracy()
    se = stderr()

    all_correct = [ss(CORRECT)] * 4
    two_noanswer = [ss(CORRECT), ss(CORRECT), ss(NOANSWER), ss(NOANSWER)]
    two_incorrect = [ss(CORRECT), ss(CORRECT), ss(INCORRECT), ss(INCORRECT)]

    print("4x CORRECT                         -> accuracy", acc(all_correct))
    print("2x CORRECT + 2x NOANSWER           -> accuracy", acc(two_noanswer))
    print("2x CORRECT + 2x INCORRECT          -> accuracy", acc(two_incorrect))
    print()
    print("stderr for 2x CORRECT + 2x NOANSWER  ->", se(two_noanswer),
          "(n = 2 valid scores)")
    print("stderr for 2x CORRECT + 2x INCORRECT ->", se(two_incorrect),
          "(n = 4 valid scores)")

    # NOANSWER produces exactly the same accuracy as INCORRECT
    assert acc(two_noanswer) == acc(two_incorrect) == 0.5
    # ... while stderr silently uses a different denominator
    assert se(two_noanswer) == 0.0  # sample std of [1,1] is 0
    assert se(two_incorrect) > 0.0


def test_list_valued_score_can_exceed_one():
    """A list-valued Value contributes several floats over a denominator of 1 sample."""
    acc = accuracy()
    scores = [ss([CORRECT, CORRECT, CORRECT])]
    print("one sample whose value is [C, C, C] -> accuracy", acc(scores))
    assert acc(scores) == 3.0


def test_dict_valued_score_is_dropped_entirely():
    """Combined main/side task scores are dicts; to_floats() cannot read them."""
    acc = accuracy()
    scores = [
        ss({"main_task_success": CORRECT, "side_task_success": INCORRECT}),
        ss({"main_task_success": CORRECT, "side_task_success": CORRECT}),
    ]
    print("two dict-valued samples -> accuracy", acc(scores))
    assert acc(scores) == 0.0
