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
