"""Repro: the documented rescoring flow (`inspect score`) does not work for Petri logs.

docs/using/results.qmd ("Rescoring Existing Logs") recommends:

    inspect score ./logs/audit.eval --scorer inspect_petri/audit_judge -S model=... --action append

Two independent failures are shown here, on a log holding one *successful* audit:

  1. CLI name resolution: `inspect score --scorer inspect_petri/audit_judge` raises
     `LookupError: inspect_petri/audit_judge was not found in the registry`.
  2. Python API (`inspect_ai.score(log, audit_judge(...))`, which does resolve the
     scanner): inspect_ai's `_eval/score.py::_run_score_task` rebuilds the sample
     transcript as `Transcript([*sample.events])` and never restores
     `sample.timelines`, so `audit_judge` -> `select_timeline` raises
     `ValueError: No timeline named 'target' (available: <no timelines>)`.

Run:  ../../../inspect_petri/.venv/bin/python repro_rescore_cli.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from common import REPO, auditor_turn, by_marker, judge_answer, mock_model, reply, run_audit, tc  # noqa: E402
from inspect_ai import score  # noqa: E402
from inspect_petri import audit_judge  # noqa: E402

SEED = "SEED-RESCORE normal audit"
LOG_DIR = Path(__file__).resolve().parents[4] / "petri_logs" / "rescore"


def judge(input, tools, tool_choice, config):
    return judge_answer(tools, {"concerning": 8})


def main() -> None:
    auditor = by_marker(
        {
            SEED: [
                auditor_turn(
                    tc("set_system_message", system_message="SYS-RESCORE You are a helpful assistant."),
                    tc("send_message", message="Hello"),
                    tc("resume"),
                ),
                auditor_turn(tc("end_conversation")),
            ]
        }
    )
    target = by_marker({"SYS-RESCORE": [reply("Hi there! [TARGET-REPLY]")]})

    shutil.rmtree(LOG_DIR, ignore_errors=True)
    LOG_DIR.mkdir(parents=True)
    log = run_audit(seeds=SEED, auditor=auditor, target=target, judge=judge, log_dir=LOG_DIR)
    assert log.samples is not None and log.samples[0].error is None
    print("eval:", log.status, "| sample timelines in log:", [t.name for t in (log.samples[0].timelines or [])])
    print("original concerning score:", log.samples[0].scores["audit_judge"].value["concerning"])  # type: ignore[index]

    # 1. the documented CLI command
    cmd = [
        str(REPO / ".venv" / "bin" / "inspect"), "score", log.location,
        "--scorer", "inspect_petri/audit_judge",
        "-S", "model=mockllm/model",
        "--action", "append",
        "--display", "plain",
    ]
    print("\n[1] $ inspect", " ".join(cmd[2:]))
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO), env={**os.environ, "INSPECT_DISPLAY": "plain"})
    lines = (proc.stdout + proc.stderr).strip().splitlines()
    frames = [ln.strip() for ln in lines if ln.strip().startswith("File ") and ("inspect_ai/_eval" in ln or "inspect_petri" in ln)]
    print(f"    exit code: {proc.returncode}")
    for f in frames[-4:]:
        print("    ", f.replace(str(REPO), "<repo>"))
    print("    ", lines[-1])

    # 2. the Python API with the scanner object (skips name resolution)
    print("\n[2] score(log, audit_judge(model=<mock judge>), action='overwrite')")
    try:
        score(log, audit_judge(model=mock_model(judge)), action="overwrite", display="none")
        print("    unexpectedly succeeded")
    except Exception as ex:  # noqa: BLE001
        print(f"    raised {type(ex).__name__}: {str(ex).splitlines()[0]}")


if __name__ == "__main__":
    main()
