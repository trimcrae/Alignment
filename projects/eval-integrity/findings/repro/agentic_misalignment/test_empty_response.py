"""Repro: an empty model completion is graded and counted as harmful=0.

Official run_experiments.py (lines 438-453) discards empty completions: no response.json is
written, so compute_statistics.py never counts them (proportion_harmful = harmful / classified).
The port sends the empty transcript to the grader, records harmful=0 / classifier_verdict=0 and
includes the sample in `accuracy`, deflating the reported rate for models that return empty
output (content filters, API quirks).

This test asserts the official behaviour (empty completions excluded), so it FAILS on the
current port; the printed score/metrics are the reproduction.
"""

from inspect_ai import eval
from inspect_ai.model import ModelOutput, get_model

from inspect_evals.agentic_misalignment import agentic_misalignment


def test_empty_completion_not_counted_in_denominator(tmp_path):
    grader = get_model(
        "mockllm/model",
        custom_outputs=[
            ModelOutput.from_content(
                model="mockllm/model",
                content="<reasoning>There is no transcript to judge.</reasoning><answer>no</answer>",
            )
        ],
        memoize=False,
    )
    target = get_model(
        "mockllm/model",
        custom_outputs=[ModelOutput.from_content(model="mockllm/model", content="")],
        memoize=False,
    )
    log = eval(
        tasks=agentic_misalignment(grader_model=grader),
        model=target,
        log_dir=str(tmp_path),
        display="none",
    )[0]
    assert log.status == "success", log.error
    sample = log.samples[0]
    metrics = {
        s.name: {k: v.value for k, v in s.metrics.items()} for s in log.results.scores
    }
    print(f"\ncompletion={sample.output.completion!r}")
    print(f"sample score value={sample.scores['harmfulness_scorer'].value}")
    print(f"completed_samples={log.results.completed_samples} metrics={metrics}")
    assert log.results.completed_samples == 0, (
        "empty completion was scored (harmful=0) and counted in the accuracy denominator"
    )
