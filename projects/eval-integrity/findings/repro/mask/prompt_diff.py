"""Compare the port's judge prompt templates with the official MASK templates.

Run:  inspect_evals/.venv/bin/python findings/repro/mask/prompt_diff.py

For each template we (1) report whether the raw strings are identical, (2) strip
blank lines from both and report the remaining, non-whitespace differences as a
unified diff.
"""

import difflib
import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
AUDIT = HERE.parents[3]
REF = AUDIT / "mask_official" / "mask" / "prompts" / "evaluation_prompts.py"
PORT = (
    AUDIT
    / "inspect_evals"
    / "src"
    / "inspect_evals"
    / "mask"
    / "prompts"
    / "prompts.py"
)


def load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


ref = load(REF, "ref_prompts")
port = load(PORT, "port_prompts")

NAMES = [
    "BELIEF_BINARY_JUDGE_PROMPT_DIRECT",
    "BELIEF_BINARY_JUDGE_PROMPT_CONSISTENCY",
    "BINARY_JUDGE_PROMPT_TEMPLATE",
    "DISINFORMATION_RULES",
    "CONTINUATIONS_RULES",
    "DOUBLING_DOWN_BINARY_PROMPT",
    "NUMERICAL_JUDGE_PROMPT",
]


def strip_blank(s: str) -> list[str]:
    return [line.rstrip() for line in s.splitlines() if line.strip()]


exit_code = 0
for name in NAMES:
    r = getattr(ref, name)
    p = getattr(port, name)
    print(f"=== {name} ===")
    print(f"raw identical: {r == p}")
    rl, pl = strip_blank(r), strip_blank(p)
    print(
        f"blank lines: reference={sum(1 for l in r.splitlines() if not l.strip())}, "
        f"port={sum(1 for l in p.splitlines() if not l.strip())}"
    )
    diff = list(
        difflib.unified_diff(rl, pl, fromfile="reference", tofile="port", lineterm="", n=0)
    )
    if diff:
        exit_code = 1
        print("non-whitespace differences after removing blank lines:")
        for line in diff:
            print("  " + line)
    else:
        print("no non-whitespace differences after removing blank lines")
    print()

sys.exit(exit_code)
