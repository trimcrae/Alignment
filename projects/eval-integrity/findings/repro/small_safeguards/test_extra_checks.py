"""Extra reproductions added on re-verification:

1. InstrumentalEval: the documented default grader (openai/gpt-5-nano) is a
   reasoning model, so inspect_ai DROPS the grader_temperature=0.0 the task sets.
2. make_me_pay: the con-artist system prompt is NOT identical to the reference;
   the port adds a sentence.
"""

import importlib.util
import os
import re

from inspect_ai.model import GenerateConfig

# ---------------------------------------------------------------------------
# 1. grader_temperature=0.0 is silently ignored for the default grader model.
#    The `openai` package is not installed in this venv, so the two real
#    module-level predicates are exec'd straight out of the shipped source and the
#    `reasoning_enabled` / temperature block is asserted verbatim against the
#    shipped file.  (Source-level check: no live API call is made.)
# ---------------------------------------------------------------------------
def test_grader_temperature_is_dropped_for_default_gpt5_nano_grader():
    import ast
    import inspect_ai
    from pathlib import Path

    root = Path(inspect_ai.__file__).parent
    openai_src = (root / "model/_openai.py").read_text()
    provider_src = (root / "model/_providers/openai.py").read_text()
    responses_src = (root / "model/_providers/openai_responses.py").read_text()

    # exec the two real module-level predicates without importing the openai package
    ns: dict = {"re": __import__("re")}
    tree = ast.parse(openai_src)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in (
            "is_gpt_5_model",
            "is_o_series_model",
        ):
            exec(compile(ast.Module(body=[node], type_ignores=[]), "<x>", "exec"), ns)
    is_gpt_5_model, is_o_series_model = ns["is_gpt_5_model"], ns["is_o_series_model"]

    # is_gpt_5_plus, as shipped (OpenAIAPI method)
    assert 'return "gpt-5." in name or self.is_latest()' in provider_src
    is_gpt_5_plus = lambda n: "gpt-5." in n  # is_latest() is False for a pinned name

    # the branch that drops sampling params, as shipped
    block = responses_src[responses_src.index("# models with reasoning enabled do not"
                                              if "# models with reasoning enabled do not" in responses_src
                                              else "# models with reasoning enabled don't do sampling params"):]
    assert "reasoning_enabled = (" in block
    assert "model_info.is_gpt_5() and not model_info.is_gpt_5_plus()" in block
    assert "do not support the 'temperature' parameter" in block

    from inspect_evals.instrumentaleval.instrumentaleval import instrumentaleval  # noqa: F401

    for name in ["gpt-5-nano", "gpt-4o", "gpt-5.1"]:
        reasoning_enabled = is_o_series_model(name) or (
            is_gpt_5_model(name) and not is_gpt_5_plus(name)
        )
        print(f"{name}: is_gpt_5={is_gpt_5_model(name)} is_gpt_5_plus={is_gpt_5_plus(name)} "
              f"reasoning_enabled={reasoning_enabled} -> "
              f"{'temperature DROPPED (warn_once)' if reasoning_enabled else 'temperature sent'}")
    assert is_gpt_5_model("gpt-5-nano") and not is_gpt_5_plus("gpt-5-nano")
    print("=> the task's documented default grader (openai/gpt-5-nano, grader_temperature=0.0) "
          "runs at temperature 1; the paper's grader was gpt-4o at temperature 0.")


# ---------------------------------------------------------------------------
# 2. make_me_pay con-artist prompt differs from the reference
# ---------------------------------------------------------------------------
def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_conartist_task_description_differs_from_reference():
    from pathlib import Path

    audit = Path(__file__).resolve().parents[3]
    ref = _load(audit / "openai_evals_official/evals/elsuite/make_me_pay/task_description.py", "ref_td")
    port = _load(audit / "inspect_evals/src/inspect_evals/make_me_pay/task_descriptions.py", "port_td")
    norm = lambda s: re.sub(r"\s+", " ", s).strip()

    for v in ["balanced", "guarded", "generous"]:
        assert norm(ref.task_description_dict[v]["mark"]) == norm(port.task_description_dict[v]["mark"]), v
    print("\nmark prompts (balanced/guarded/generous): identical to reference")

    a = norm(ref.task_description_dict["balanced"]["conartist"])
    b = norm(port.task_description_dict["balanced"]["conartist"])
    assert a != b
    tail_ref = a[a.index("To recieve"):]
    tail_port = b[b.index("To receive"):]
    print(f"conartist tail, reference: {tail_ref}")
    print(f"conartist tail, port     : {tail_port}")
    assert "You are not supposed to say this yourself." in b
    assert "You are not supposed to say this yourself." not in a
    print("=> the port adds the sentence 'You are not supposed to say this yourself.' "
          "(and fixes two 'recieve' typos); everything else is identical.")
    # the summary-model prompt exists only in the reference
    assert "summary" in ref.task_description_dict
    assert "summary" not in port.task_description_dict
    print("=> reference task_description_dict has a 'summary' entry; the port has none.")
