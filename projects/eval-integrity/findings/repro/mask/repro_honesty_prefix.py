"""Compare current MASK classifier with the pinned reference on synthetic inputs.

Run: python repro_honesty_prefix.py INSPECT_EVALS_CHECKOUT REFERENCE_METRIC_PY
Loads unmodified classifier modules without importing the dataset/task entry point.
Authored by Codex; this measures a synthetic discrepancy, not model prevalence.
"""

import argparse
import importlib.util
import itertools
import json
import subprocess
import sys
import types
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    parser.add_argument("reference", type=Path)
    args = parser.parse_args()
    source = args.checkout.resolve() / "src/inspect_evals"
    for name, path in [
        ("inspect_evals", source),
        ("inspect_evals.mask", source / "mask"),
    ]:
        package = types.ModuleType(name)
        package.__path__ = [str(path)]
        sys.modules[name] = package

    from inspect_evals.mask.classify import compute_honesty_at_n
    from inspect_evals.mask.models import Belief, Statement
    from inspect_evals.mask.types import (
        BinaryAnswer,
        Honesty,
        QuestionArchetype,
        QuestionType,
    )

    spec = importlib.util.spec_from_file_location(
        "mask_reference_metric", args.reference
    )
    reference = importlib.util.module_from_spec(spec)
    saved_argv = sys.argv
    try:
        sys.argv = [str(args.reference)]  # Reference parses CLI arguments on import.
        spec.loader.exec_module(reference)
    finally:
        sys.argv = saved_argv

    belief = Belief(proposition_type=QuestionType.BINARY, value=BinaryAnswer.A)
    rows = []
    for replies in itertools.product("AB", repeat=2):
        statements = [
            Statement(proposition_type=QuestionType.BINARY, value=BinaryAnswer(x))
            for x in replies
        ]
        row = {"eval_belief": "A", "run1": replies[0], "run2": replies[1]}
        actual = [
            compute_honesty_at_n(
                belief,
                statements,
                QuestionType.BINARY,
                QuestionArchetype.KNOWN_FACTS,
                n,
                0.05,
            ).value
            for n in (1, 2)
        ]
        expected = [
            "honest"
            if reference.aggregate_eval_honesty(
                row, ["run1", "run2"][:n], "eval_belief"
            )
            == "1"
            else "lie"
            for n in (1, 2)
        ]
        single = compute_honesty_at_n(
            belief,
            statements[:1],
            QuestionType.BINARY,
            QuestionArchetype.KNOWN_FACTS,
            1,
            0.05,
        )
        assert single.value == expected[0]
        assert actual[1] == expected[1]
        rows.append(
            {
                "statements": "".join(replies),
                "inspect_honesty_1": actual[0],
                "reference_honesty_1": expected[0],
                "honesty_2_both": actual[1],
            }
        )

    actual_rate = sum(
        r["inspect_honesty_1"] == Honesty.HONEST.value for r in rows
    ) / len(rows)
    reference_rate = sum(
        r["reference_honesty_1"] == Honesty.HONEST.value for r in rows
    ) / len(rows)
    print(
        json.dumps(
            {
                "inspect_evals_commit": subprocess.check_output(
                    ["git", "-C", str(args.checkout), "rev-parse", "HEAD"], text=True
                ).strip(),
                "reference_commit": "25e0b1201e6c928ebe69f7c5aad6fa9063a377ea",
                "cases": rows,
                "equal_weight_synthetic_honesty_1": {
                    "inspect": actual_rate,
                    "reference": reference_rate,
                    "difference_percentage_points": 100
                    * (actual_rate - reference_rate),
                },
                "single_statement_control": "all four cases match reference",
                "scope": "Unmodified binary classifier and reference aggregation; no model calls or dataset, not empirical prevalence",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
