"""Reproductions for inspect_ai.scorer._metrics (accuracy, mean, stderr, std,
var, bootstrap_stderr, grouped) and value_to_float.

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
    accuracy,
    bootstrap_stderr,
    grouped,
    mean,
    std,
    stderr,
    value_to_float,
    var,
)

NAN = float("nan")


# ---------------------------------------------------------------------------
# X-1  the metric functions do not skip NaN; only the eval pipeline does
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "metric",
    [accuracy(), mean(), stderr(), std(), var(), bootstrap_stderr(num_samples=20)],
)
def test_metrics_return_nan_when_handed_an_unscored_sample(metric):
    """Score.unscored()'s docstring calls NaN "the canonical sentinel that
    aggregate metrics and reducers skip". The metric functions themselves do
    not skip it -- the filtering lives in
    _eval/task/results.py::scorer_for_metrics -- so any direct or nested use
    (custom metrics, tests, post-hoc analysis) propagates NaN."""
    result = metric(sample_scores([CORRECT, INCORRECT, NAN]))
    assert isinstance(result, float) and math.isnan(result)


def test_pipeline_filter_is_what_makes_unscored_samples_work():
    """The same data with the NaN removed (as the pipeline does) aggregates."""
    assert accuracy()(sample_scores([CORRECT, INCORRECT])) == 0.5


# ---------------------------------------------------------------------------
# X-2  single sample / empty input
# ---------------------------------------------------------------------------


def test_dispersion_metrics_report_zero_for_a_single_sample():
    """A one-sample eval logs stderr = 0.0, which reads as a perfectly precise
    estimate rather than an undefined one."""
    for metric in (stderr(), std(), var(), bootstrap_stderr(num_samples=20)):
        assert metric(sample_scores([CORRECT])) == 0


def test_accuracy_and_mean_return_zero_for_no_scores():
    assert accuracy()(sample_scores([])) == 0.0
    assert mean()(sample_scores([])) == 0.0


# ---------------------------------------------------------------------------
# X-3  accuracy over string / dict / list values vs the documented behaviour
# ---------------------------------------------------------------------------


def test_accuracy_over_the_documented_sentinels():
    """accuracy()'s docstring: C -> 1.0, I -> 0, P -> 0.5, N -> 0."""
    assert accuracy()(sample_scores([CORRECT, INCORRECT, PARTIAL, NOANSWER])) == 0.375


def test_accuracy_over_dict_and_list_values_is_zero_with_a_warning(caplog):
    """Documented: "prints a warning and returns 0 if the Value is a complex
    object (list or dict)". A dict-valued scorer declared with a flat metric
    list therefore reports 0% for every sample."""
    import logging

    with caplog.at_level(logging.WARNING):
        assert accuracy()(sample_scores([{"a": 1}, {"a": 1}])) == 0.0
        assert accuracy()(sample_scores([[1, 1], [1, 1]])) == 0.0
    assert sum("Unable to convert value to float" in r.message for r in caplog.records) == 4


def test_accuracy_over_string_values_beyond_the_documented_set():
    """value_to_float also maps yes/true/no/false and numeric strings; anything
    else -- including a lower-case "c" -- warns and scores 0."""
    assert accuracy()(sample_scores(["yes", "no", "TRUE", "False"])) == 0.5
    assert accuracy()(sample_scores(["1", "0.5"])) == 0.75
    assert accuracy()(sample_scores(["c", "c"])) == 0.0  # case-sensitive sentinel
    assert accuracy()(sample_scores(["maybe", "maybe"])) == 0.0
    assert value_to_float()("c") == 0.0


# ---------------------------------------------------------------------------
# X-4  clustered standard errors
# ---------------------------------------------------------------------------

TWO_CLUSTERS = [{"c": "g1"}, {"c": "g1"}, {"c": "g2"}, {"c": "g2"}]
VALUES = [CORRECT, CORRECT, INCORRECT, INCORRECT]


def test_clustered_stderr_matches_the_plain_stderr_when_every_cluster_is_a_singleton():
    """Positive control on the formula."""
    singletons = [{"c": i} for i in range(4)]
    assert stderr(cluster="c")(sample_scores(VALUES, singletons)) == pytest.approx(
        stderr()(sample_scores(VALUES))
    )


def test_clustered_stderr_inflates_the_error_when_outcomes_track_the_cluster():
    clustered = stderr(cluster="c")(sample_scores(VALUES, TWO_CLUSTERS))
    plain = stderr()(sample_scores(VALUES))
    assert clustered == pytest.approx(0.5)
    assert plain == pytest.approx(0.2886751, rel=1e-5)
    assert clustered > plain


def test_clustered_stderr_reports_zero_when_there_is_only_one_cluster():
    """Clustering on a key that is constant across the dataset silently
    produces a zero error bar rather than an error or NaN."""
    one = [{"c": "g1"}] * 4
    assert stderr(cluster="c")(sample_scores(VALUES, one)) == 0.0


def test_clustered_stderr_merges_clusters_that_differ_only_by_type():
    """np.unique coerces a mixed int/str metadata column to strings, so cluster
    1 and cluster "1" become one cluster."""
    mixed = [{"c": 1}, {"c": "1"}, {"c": 2}, {"c": "2"}]
    assert stderr(cluster="c")(sample_scores(VALUES, mixed)) == pytest.approx(
        stderr(cluster="c")(sample_scores(VALUES, TWO_CLUSTERS))
    )


def test_clustered_stderr_raises_when_the_cluster_key_is_missing():
    with pytest.raises(ValueError, match="no cluster metadata"):
        stderr(cluster="c")(sample_scores([CORRECT, INCORRECT], [{"x": 1}, {"x": 2}]))


# ---------------------------------------------------------------------------
# X-5  grouped()
# ---------------------------------------------------------------------------

UNBALANCED_META = [{"c": "g1"}, {"c": "g1"}, {"c": "g1"}, {"c": "g2"}]
UNBALANCED_VALUES = [CORRECT, CORRECT, CORRECT, INCORRECT]


def test_grouped_all_samples_is_sample_weighted_and_all_groups_is_not():
    """Documented, but the two differ a lot on unbalanced groups (0.75 vs 0.5)."""
    assert grouped(accuracy(), "c")(sample_scores(UNBALANCED_VALUES, UNBALANCED_META)) == {
        "g1": 1.0,
        "g2": 0.0,
        "all": 0.75,
    }
    assert grouped(accuracy(), "c", all="groups")(
        sample_scores(UNBALANCED_VALUES, UNBALANCED_META)
    ) == {"g1": 1.0, "g2": 0.0, "all": 0.5}


def test_grouped_propagates_nan_from_any_group():
    result = grouped(accuracy(), "c")(
        sample_scores([CORRECT, NAN], [{"c": "g1"}, {"c": "g1"}])
    )
    assert math.isnan(result["g1"]) and math.isnan(result["all"])


def test_grouped_raises_when_the_group_key_is_missing():
    with pytest.raises(ValueError, match="has no c metadata"):
        grouped(accuracy(), "c")(sample_scores([CORRECT], [{"x": 1}]))


# ---------------------------------------------------------------------------
# X-6  bootstrap_stderr draws from the global numpy RNG with no seed
# ---------------------------------------------------------------------------


def test_bootstrap_stderr_is_not_reproducible_and_runs_below_the_clt_stderr():
    """bootstrap_stderr() exposes no seed and uses np.random.choice, so the
    logged value changes run to run. It is also systematically smaller than
    stderr() by sqrt((n-1)/n), which is inherent to bootstrapping a mean but
    means the two metrics are not interchangeable at small n."""
    values = [CORRECT] * 7 + [INCORRECT] * 5
    scores = sample_scores(values)
    runs = [bootstrap_stderr(num_samples=1000)(scores) for _ in range(4)]
    assert len(set(runs)) > 1, runs
    clt = stderr()(scores)
    assert all(r < clt for r in runs), (runs, clt)
    assert clt * math.sqrt(11 / 12) == pytest.approx(sum(runs) / len(runs), rel=0.03)


def test_grouped_rejects_a_group_name_that_collides_with_all_label():
    with pytest.raises(ValueError, match="collides with the `all_label`"):
        grouped(accuracy(), "c")(sample_scores([CORRECT], [{"c": "all"}]))
