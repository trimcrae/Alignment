"""Reproductions for inspect_ai.scorer._reducer (epoch / panel reduction).

Target: inspect_ai 0.3.260.dev154+gce5617d35.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pytest  # noqa: E402
from _helpers import sample_scores  # noqa: E402

from inspect_ai.scorer import (  # noqa: E402
    CORRECT,
    INCORRECT,
    NOANSWER,
    PARTIAL,
    Score,
    accuracy,
)
from inspect_ai.scorer._reducer import create_reducers  # noqa: E402

NAN = float("nan")


def reduce(name: str, values: list):
    return create_reducers(name)[0]([Score(value=v) for v in values]).value


# ---------------------------------------------------------------------------
# R-1  "mode" is a plurality with first-seen tie-breaking, not a majority
# ---------------------------------------------------------------------------


def test_mode_tie_is_broken_by_declaration_order_not_by_a_majority():
    """model-graded.qmd: "the final grade is chosen by majority vote ... uses
    the multi_scorer() function with a "mode" (majority vote) reducer".
    With an even panel (or an all-distinct panel) the first entry simply wins.
    """
    assert reduce("mode", [CORRECT, INCORRECT]) == CORRECT
    assert reduce("mode", [INCORRECT, CORRECT]) == INCORRECT
    assert reduce("mode", [CORRECT, PARTIAL, INCORRECT]) == CORRECT
    assert reduce("mode", [INCORRECT, PARTIAL, CORRECT]) == INCORRECT


def test_mode_lets_one_grader_decide_when_the_others_fail_to_parse():
    """An unscored panel member is dropped from the count, so a 3-model panel
    with one parse failure and a 1-1 split is decided by list order."""
    assert reduce("mode", [NAN, CORRECT, INCORRECT]) == CORRECT
    assert reduce("mode", [NAN, INCORRECT, CORRECT]) == INCORRECT
    assert reduce("mode", [NAN, NAN, CORRECT]) == CORRECT


def test_mode_with_a_real_majority_behaves():
    assert reduce("mode", [CORRECT, CORRECT, INCORRECT]) == CORRECT
    assert reduce("mode", [INCORRECT, CORRECT, INCORRECT]) == INCORRECT


def test_mode_ties_per_key_for_dict_values():
    assert reduce("mode", [{"a": CORRECT}, {"a": INCORRECT}]) == {"a": CORRECT}


# ---------------------------------------------------------------------------
# R-2  the default "mean" reducer converts categorical values to floats
# ---------------------------------------------------------------------------


def test_mean_reducer_replaces_the_C_I_label_with_a_float():
    assert reduce("mean", [CORRECT, INCORRECT]) == 0.5
    assert reduce("mean", [NOANSWER, CORRECT]) == 0.5
    assert reduce("median", [CORRECT, INCORRECT]) == 0.5


def test_mean_reducer_silently_zeroes_a_categorical_scorer(caplog):
    """A scorer whose values are category names (not C/I/P/N, yes/no or
    numbers) is reduced to 0.0 with a warning per epoch -- the default epoch
    reducer destroys the score."""
    import logging

    with caplog.at_level(logging.WARNING):
        assert reduce("mean", ["refusal", "refusal"]) == 0.0
    assert any("Unable to convert value to float" in r.message for r in caplog.records)


def test_max_reducer_returns_the_first_value_when_none_convert(caplog):
    import logging

    with caplog.at_level(logging.WARNING):
        assert reduce("max", ["refusal", "compliance"]) == "refusal"
    assert reduce("max", [INCORRECT, CORRECT]) == CORRECT


# ---------------------------------------------------------------------------
# R-3  NaN epochs are dropped, changing the per-sample denominator
# ---------------------------------------------------------------------------


def test_unscored_epochs_are_dropped_so_one_epoch_can_carry_the_sample():
    """With epochs=3 and two unscored epochs, the reduced score is whatever the
    single scored epoch said -- full credit, not 1/3 credit."""
    assert reduce("mean", [NAN, CORRECT]) == 1.0
    assert reduce("mean", [NAN, NAN, CORRECT]) == 1.0
    assert math.isnan(reduce("mean", [NAN, NAN, NAN]))
    assert reduce("max", [NAN, INCORRECT]) == INCORRECT


def test_at_least_k_counts_only_scored_epochs():
    assert reduce("at_least_1", [NAN, NAN, CORRECT]) == 1
    assert reduce("at_least_2", [NAN, NAN, CORRECT]) == 0


def test_pass_at_k_is_unscored_when_fewer_than_k_epochs_scored():
    assert math.isnan(reduce("pass_at_2", [NAN, NAN, CORRECT]))
    assert math.isnan(reduce("pass_at_3", [CORRECT, INCORRECT]))
    assert reduce("pass_at_2", [CORRECT, INCORRECT]) == 1.0


# ---------------------------------------------------------------------------
# R-4  dict / list values
# ---------------------------------------------------------------------------


def test_dict_values_are_reduced_per_key():
    assert reduce(
        "mean", [{"a": CORRECT, "b": INCORRECT}, {"a": INCORRECT, "b": INCORRECT}]
    ) == {"a": 0.5, "b": 0}
    assert reduce("mean", [{"a": CORRECT}, {"a": NAN}]) == {"a": 1.0}
    assert reduce("mean", [{"a": CORRECT}, NAN]) == {"a": 1.0}


def test_mismatched_dict_keys_and_list_lengths_raise():
    with pytest.raises(ValueError, match="mismatched keys"):
        reduce("mean", [{"a": CORRECT}, {"b": CORRECT}])
    with pytest.raises(ValueError, match="mismatched lengths"):
        reduce("mean", [[1, 0], [1, 1, 1]])
    with pytest.raises(ValueError, match="non-dictionary value"):
        reduce("mean", [{"a": CORRECT}, CORRECT])


def test_list_values_are_reduced_per_index():
    assert reduce("mean", [[1, 0], [1, 1]]) == [1.0, 0.5]
    assert reduce("mode", [[CORRECT, INCORRECT], [INCORRECT, INCORRECT]]) == [
        CORRECT,
        INCORRECT,
    ]


# ---------------------------------------------------------------------------
# R-5  the "collect" reducer is incompatible with the default metrics
# ---------------------------------------------------------------------------


def test_collect_reducer_makes_accuracy_report_zero(caplog):
    """Epochs(n, "collect") produces a list value; accuracy()/stderr() warn and
    score every sample 0."""
    import logging

    collected = reduce("collect", [CORRECT, INCORRECT, NAN])
    assert collected == [CORRECT, INCORRECT]
    with caplog.at_level(logging.WARNING):
        assert accuracy()(sample_scores([collected, collected])) == 0.0
    assert any("Unable to convert value to float" in r.message for r in caplog.records)
