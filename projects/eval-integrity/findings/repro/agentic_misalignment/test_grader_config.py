"""Repro: the grader (classifier) model is called with inspect's default GenerateConfig.

Official classifiers (agentic_misalignment_official/classifiers/*_classifier.py) call
    client(self.model_id, messages, temperature=0.0, max_tokens=2000)
The port (scorers.py:score_from_classifier) calls grader.generate(grader_model_input) with no
config, so the grader runs at the provider's default temperature (1.0 for Anthropic/OpenAI)
unless the user happens to pass a grader Model with its own config.

This test asserts the official settings, so it FAILS on the current port; the printed config is
the reproduction.
"""

from inspect_ai import eval
from inspect_ai.model import ModelOutput, get_model

from inspect_evals.agentic_misalignment import agentic_misalignment


def test_grader_called_with_official_sampling_settings(tmp_path):
    grader = get_model(
        "mockllm/model",
        custom_outputs=[
            ModelOutput.from_content(
                model="mockllm/model",
                content="<reasoning>refusal</reasoning><answer>no</answer>",
            )
        ],
        memoize=False,
    )
    captured = []
    original = grader.api.generate

    async def spy(input, tools, tool_choice, config):
        captured.append(config)
        return await original(input, tools, tool_choice, config)

    grader.api.generate = spy  # type: ignore[method-assign]

    target = get_model(
        "mockllm/model",
        custom_outputs=[
            ModelOutput.from_content(model="mockllm/model", content="I will not do this.")
        ],
        memoize=False,
    )
    log = eval(
        tasks=agentic_misalignment(grader_model=grader),
        model=target,
        log_dir=str(tmp_path),
        display="none",
    )[0]
    assert log.status == "success", log.error
    assert len(captured) == 1
    cfg = captured[0]
    print(f"\ngrader GenerateConfig: temperature={cfg.temperature!r} max_tokens={cfg.max_tokens!r}")
    assert (cfg.temperature, cfg.max_tokens) == (0.0, 2000), (
        "official classifiers use temperature=0.0, max_tokens=2000; "
        f"port grader got temperature={cfg.temperature!r}, max_tokens={cfg.max_tokens!r}"
    )
