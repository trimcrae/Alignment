"""Sampling configuration of the evaluated model vs the reference implementations."""

from inspect_ai.model import GenerateConfig

from inspect_evals.coconot.coconot import coconot
from inspect_evals.instrumentaleval.instrumentaleval import instrumentaleval
from inspect_evals.make_me_pay.make_me_pay import make_me_pay
from inspect_evals.makemesay.makemesay import makemesay


def _cfg(task):
    c = task.config
    return {k: v for k, v in c.model_dump().items() if v is not None} if c else {}


def test_evaluated_model_sampling_config_vs_reference():
    rows = [
        ("instrumentaleval", instrumentaleval,
         "main.py:21-23,97-98: temperature 0.0, max_tokens 1000 (judge: 0.0 / 50)"),
        ("coconot", coconot,
         "open-instruct-predict-and-refusal-evaluate.sh:59: --max_new_tokens 512"),
        ("make_me_pay", make_me_pay,
         "registry/solvers/make-me-pay.yaml: temperature 1.0, max_tokens 1000 (both roles)"),
        ("makemesay", makemesay,
         "openai/evals completion fns; no explicit sampling config in the elsuite"),
    ]
    print()
    for name, fn, ref in rows:
        # instrumentaleval needs no network to build; coconot/makemesay hit the dataset,
        # so only build the ones that can be built offline.
        try:
            t = fn()
        except Exception as e:  # dataset download blocked in this sandbox
            print(f"{name:17s} task could not be constructed offline ({type(e).__name__}); "
                  f"reading source instead")
            continue
        print(f"{name:17s} port task config = {_cfg(t) or '{} (provider defaults)'}")
        print(f"{'':17s} reference          = {ref}")

    # The two facts asserted here do not need the dataset:
    import inspect

    ie_src = inspect.getsource(instrumentaleval.__wrapped__)
    assert "config=" not in ie_src.replace("config=GenerateConfig(temperature=grader_temperature)", "")
    print("\ninstrumentaleval: Task(...) has no `config=`; the only GenerateConfig is the "
          "grader's temperature -> the EVALUATED model runs at provider defaults "
          "(reference: temperature 0.0, max_tokens 1000).")

    mmp_src = inspect.getsource(make_me_pay.__wrapped__)
    assert "GenerateConfig" not in mmp_src
    print("make_me_pay: Task(...) has no `config=` either (reference pinned "
          "temperature 1.0 / max_tokens 1000 for con-artist and mark).")

    cn_src = inspect.getsource(coconot.__wrapped__)
    assert "GenerateConfig(temperature=0, max_tokens=256)" in cn_src
    print("coconot: config=GenerateConfig(temperature=0, max_tokens=256) "
          "(reference inference used --max_new_tokens 512).")

    mms_src = inspect.getsource(makemesay.__wrapped__)
    assert "GenerateConfig" not in mms_src
    print("makemesay: no `config=`.")
