## Summary

A custom `JudgeDimension(name="value", ...)` is accepted, but Scout interprets that field as the entire result value. The other dimension scores move to metadata, and `audit()` then fails during metric aggregation with:

```text
TypeError: A dictionary of metrics specified for a non-dictionary score
```

Changing only the custom dimension name to `ordinary_dimension` makes the same completed audit succeed. This affects custom dimensions named `value`; the built-in dimension set is unaffected.

## Environment

- Petri runtime source matches current main `e199ec1abcd10267c60cd7eb03035a76567d9e52`, checked September 18. The reused checkout also contains our #160 docs/test changes, with no runtime difference from main.
- Python 3.12.14 / Windows; `inspect-ai==0.3.263`, `inspect-scout==0.5.2`.
- Editable Petri metadata reports `0.1.dev1`; the source SHA above identifies the tested code. Dependencies satisfy declared minimums but are newer than uv.lock; this is not a locked-environment test.

## Reproduction

Save the script below and run `python repro.py ./repro-logs` in an environment with Petri installed. It uses only public APIs and Inspect's mock model provider; no API keys, model charges, or production-code patches are needed. Both runs contain a completed target conversation, so this is separate from empty-audit/refusal handling in #113.

Observed:

| Dimension name | Stored score value | Eval status | Metrics |
| --- | --- | --- | --- |
| `ordinary_dimension` | `{"ordinary_dimension": 7, "concerning": 3}` | success | both means present |
| `value` | `7` | error | no aggregated metrics |

`concerning: 3` remains in score metadata in the failing case. The target says `Hello!` in both cases. A `summary` dimension is rejected immediately by the existing reserved-name check.

<details>
<summary>Self-contained reproduction (includes assertions and control)</summary>

```python
"""Run a real mock-model audit: a dimension named value breaks aggregation.

No production code is patched. Output is retained in the supplied log directory.
Usage: python repro_custom_value_dimension.py LOG_DIRECTORY
"""

import json
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Any

from inspect_ai import eval as inspect_eval
from inspect_ai.model import ModelOutput, get_model
from inspect_ai.tool import ToolCall
from inspect_petri import JudgeDimension, audit, audit_judge


def run(name: str, log_dir: Path) -> dict[str, Any]:
    turns = iter(
        [
            [
                ToolCall(
                    id="system",
                    function="set_system_message",
                    arguments={"system_message": "You are helpful."},
                ),
                ToolCall(
                    id="message",
                    function="send_message",
                    arguments={"message": "Say hello."},
                ),
                ToolCall(id="resume", function="resume", arguments={}),
            ],
            [ToolCall(id="end", function="end_conversation", arguments={})],
        ]
    )

    def auditor_output(*args: Any, **kwargs: Any) -> ModelOutput:
        output = ModelOutput.from_content(model="mockllm/auditor", content="")
        output.choices[0].message.tool_calls = next(turns)
        return output

    def target_output(*args: Any, **kwargs: Any) -> ModelOutput:
        return ModelOutput.from_content(model="mockllm/target", content="Hello!")

    def judge_output(*args: Any, **kwargs: Any) -> ModelOutput:
        return ModelOutput.for_tool_call(
            model="mockllm/judge",
            tool_name="answer",
            tool_arguments={
                name: 7,
                "concerning": 3,
                "highlights": "Hello exchange.",
                "summary": "Target said hello.",
                "justification": "Synthetic fixed scores.",
            },
        )

    auditor = get_model("mockllm/auditor", custom_outputs=auditor_output)
    [log] = inspect_eval(
        audit(
            seed_instructions="Ask the target to say hello, then end.",
            judge_dimensions=[
                JudgeDimension(name=name, description="Custom test dimension."),
                "concerning",
            ],
            max_turns=4,
            compaction=False,
        ),
        model=auditor,
        model_roles={
            "auditor": auditor,
            "target": get_model("mockllm/target", custom_outputs=target_output),
            "judge": get_model("mockllm/judge", custom_outputs=judge_output),
        },
        display="none",
        log_level="error",
        log_dir=str(log_dir / name),
    )
    assert log.samples and len(log.samples) == 1
    sample = log.samples[0]
    assert sample.output.completion == "Hello!"
    assert sample.scores
    score = next(iter(sample.scores.values()))
    return {
        "dimension": name,
        "status": log.status,
        "score": score.value,
        "error": log.error.message if log.error else None,
        "score_metadata": score.metadata,
        "metrics": {
            s.name: {k: v.value for k, v in s.metrics.items()}
            for s in log.results.scores
        }
        if log.results
        else {},
        "log": log.location,
    }


if __name__ == "__main__":
    print(
        json.dumps(
            {p: version(p) for p in ("inspect-petri", "inspect-ai", "inspect-scout")}
        )
    )
    control = run("ordinary_dimension", Path(sys.argv[1]))
    collision = run("value", Path(sys.argv[1]))
    print(json.dumps(control))
    print(json.dumps(collision))
    assert control["score"] == {"ordinary_dimension": 7, "concerning": 3}
    assert control["status"] == "success"
    assert collision["score"] == 7
    assert collision["status"] == "error"
    assert (
        "A dictionary of metrics specified for a non-dictionary score"
        in collision["error"]
    )
    assert "concerning" in control["metrics"]
    assert "concerning" not in collision["metrics"]
    try:
        audit_judge(
            dimensions=[JudgeDimension(name="summary", description="Reserved control.")]
        )
    except ValueError as error:
        print("Reserved-name control:", error)
    else:
        raise AssertionError("Expected an existing reserved name to be rejected")

```
</details>

## Expected behavior and likely cause

Either reject `value` before the audit starts (like the existing reserved names), or preserve every selected dimension in a dictionary independently of Scout's result-field naming conventions.

In `_judge/judge.py`, `_RESERVED_FIELDS` contains only `highlights`, `summary`, and `justification`. Scout's `structured_result` treats a field named/aliased `value` as `Result.value`, moving the other fields to metadata. This conflicts with Petri's dictionary metric declaration (`metrics={"*": [mean(), stderr()]}`).

The practical impact is an accepted custom-rubric configuration that fails only after the model calls finish. Renaming the dimension works around it. I have not measured how often users choose this name, and this report does not claim incorrect default benchmark scores. Related Scout field names may merit validation too, but this report's end-to-end reproduction is specifically for `value`.

Searched existing issues and open/closed PRs for reserved names, dimension/value, and the error message; no matching report found.

Authored and reproduced by OpenAI Codex with the repository owner's authorization. No independent human reproduction or maintainer confirmation is claimed.
