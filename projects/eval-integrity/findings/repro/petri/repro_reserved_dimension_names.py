"""Repro: custom dimension names `value` / `label` / `explanation` are not rejected but break the score.

`_alignment_answer_type` reserves only {highlights, summary, justification}. inspect_scout's
structured_result() gives special meaning to fields named (or aliased) `value`, `label` and
`explanation`: a `value` field *replaces* the whole score dict, `label` is stripped into
Result.label, and `explanation` collides with the justification alias.

Run:  ../../../inspect_petri/.venv/bin/python repro_reserved_dimension_names.py
"""

from __future__ import annotations

import json

from inspect_ai.model import ModelOutput
from inspect_petri._judge.dimensions import JudgeDimension
from inspect_petri._judge.judge import _alignment_answer_type  # pyright: ignore[reportPrivateUsage]
from inspect_scout import AnswerStructured
from inspect_scout._llm_scanner.generate import parse_answer


def parsed(dim_name: str) -> object:
    dims = [JudgeDimension(name=dim_name, description="custom dim"), JudgeDimension(name="concerning", description="c")]
    try:
        answer_type = _alignment_answer_type(dims)
    except Exception as ex:  # noqa: BLE001
        return f"_alignment_answer_type raised {type(ex).__name__}: {ex}"
    args = {"highlights": "h", "summary": "s", "justification": "j", dim_name: 7, "concerning": 3}
    output = ModelOutput.for_tool_call(model="mockllm", tool_name="answer", tool_arguments=args)
    output.completion = json.dumps(args)
    try:
        result = parse_answer(output, AnswerStructured(answer_type), lambda _t: [])
    except Exception as ex:  # noqa: BLE001
        return f"parse_answer raised {type(ex).__name__}: {str(ex)[:120]}"
    return {"value": result.value, "label": result.label, "explanation": result.explanation, "metadata": result.metadata}


def main() -> None:
    for name in ("value", "label", "explanation", "ordinary_dim"):
        print(f"dimension named {name!r:16s} ->", parsed(name))

    # end-to-end: a dimension named `value` through audit() + eval()
    import sys
    import tempfile
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))
    from common import auditor_turn, by_marker, judge_answer, reply, run_audit, tc

    seed = "SEED-V reserved name end to end"
    auditor = by_marker(
        {
            seed: [
                auditor_turn(
                    tc("set_system_message", system_message="SYS-V You are a helpful assistant."),
                    tc("send_message", message="Hello"),
                    tc("resume"),
                ),
                auditor_turn(tc("end_conversation")),
            ]
        }
    )
    target = by_marker({"SYS-V": [reply("Hi there!")]})

    def judge(input, tools, tool_choice, config):
        return judge_answer(tools, {"value": 7, "concerning": 3})

    with tempfile.TemporaryDirectory() as tmp:
        try:
            log = run_audit(
                seeds=seed, auditor=auditor, target=target, judge=judge, log_dir=Path(tmp),
                judge_dimensions=[JudgeDimension(name="value", description="custom"), "concerning"],
            )
            assert log.samples is not None
            [sample] = log.samples
            print("\nend-to-end with a dimension named 'value':")
            print("  status:", log.status, "| error:", log.error.message.splitlines()[-1] if log.error else None)
            print("  sample score value:", sample.scores["audit_judge"].value if sample.scores else None)
            print("  results.scores:", [(s.name, {k: v.value for k, v in s.metrics.items()}) for s in (log.results.scores if log.results else [])])
            print("  logged package versions:", log.eval.packages)
        except Exception as ex:  # noqa: BLE001
            print("\nend-to-end with a dimension named 'value' raised:", type(ex).__name__, str(ex)[:200])


if __name__ == "__main__":
    main()
