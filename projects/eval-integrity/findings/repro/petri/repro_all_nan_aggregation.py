"""Repro: what the results table looks like when every judge call fails (all-NaN scores).

Exercises inspect_ai's `scorers_from_metric_dict` directly with the metric dict
`audit_judge` declares (`{"*": [mean(), stderr()]}`):

  mixed   one dict score + one NaN  -> per-dimension metrics, unscored_samples=1
  all_nan every sample NaN          -> a single EvalScore literally named '*'
                                       with mean=nan, and scored_samples=0

Run:  ../../../inspect_petri/.venv/bin/python repro_all_nan_aggregation.py
"""

from inspect_ai._eval.task.results import ScorerInfo, scorers_from_metric_dict
from inspect_ai.scorer import Score, mean, stderr
from inspect_ai.scorer._metric import SampleScore

metrics = {"*": [mean(), stderr()]}
info = ScorerInfo(name="audit_judge", metrics=metrics)


def run(label, scores):
    out = scorers_from_metric_dict(
        scorer_name="audit_judge",
        scorer_info=info,
        sample_scores=scores,
        metrics=metrics,
    )
    print(f"=== {label}")
    for es in out:
        ms = {k: round(v.value, 3) if v.value == v.value else "nan" for k, v in es.metrics.items()}
        print(f"   name={es.name!r} metrics={ms} scored={es.scored_samples} unscored={es.unscored_samples}")


nan = float("nan")
run(
    "mixed (sample A judged, sample B NaN)",
    [
        SampleScore(sample_id="A", score=Score(value={"concerning": 8, "auditor_failure": 2})),
        SampleScore(sample_id="B", score=Score(value=nan)),
    ],
)
run(
    "all_nan (every judge call failed)",
    [
        SampleScore(sample_id="A", score=Score(value=nan)),
        SampleScore(sample_id="B", score=Score(value=nan)),
    ],
)
