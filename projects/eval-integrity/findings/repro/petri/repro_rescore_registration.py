"""Reproduce the documented Petri rescore command's registry failure.

Uses a synthetic Inspect log to isolate name resolution, not judge quality.
No model requests, datasets, or Docker. Authored by Codex.
Run in an environment containing inspect-ai, inspect-scout, and inspect-petri.
"""

import json
import subprocess
import sys
import tempfile
from importlib.metadata import version

from inspect_ai import Task, eval
from inspect_ai._util.registry import registry_info
from inspect_ai.dataset import Sample
from inspect_ai.model import ModelOutput
from inspect_ai.scorer import match
from inspect_ai.solver import solver
from inspect_petri import audit_judge


@solver
def fixed_answer():
    async def solve(state, generate):
        state.output = ModelOutput.from_content("mockllm/model", "hello")
        return state

    return solve


def main():
    with tempfile.TemporaryDirectory(prefix="petri-rescore-registration-") as temp:
        logs = eval(
            Task(dataset=[Sample(input="hello", target="hello")],
                 solver=fixed_answer(), scorer=match()),
            model="mockllm/model", display="none", log_dir=temp,
        )
        assert logs[0].status == "success"
        control_command = [
            sys.executable, "-c", "from inspect_ai._cli.main import main; main()",
            "score", logs[0].location, "--scorer", "match", "--action", "append", "--overwrite",
        ]
        control = subprocess.run(control_command, capture_output=True, text=True, timeout=60)
        assert control.returncode == 0, (control.stdout + control.stderr)[-1000:]
        command = [
            sys.executable, "-c", "from inspect_ai._cli.main import main; main()",
            "score", logs[0].location, "--scorer", "inspect_petri/audit_judge",
            "-S", "model=mockllm/model", "--action", "append", "--overwrite",
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        error_lines = [line.strip() for line in output.splitlines()
                       if "not found" in line.lower() or "PrerequisiteError" in line]
        assert result.returncode != 0, output[-1000:]
        assert "inspect_petri/audit_judge" in output and "not found" in output.lower(), output[-1000:]
        print(json.dumps({
            "inspect_ai": version("inspect-ai"),
            "inspect_scout": version("inspect-scout"),
            "petri_registration_type": registry_info(audit_judge).type,
            "original_log_status": logs[0].status,
            "match_control_exit_code": control.returncode,
            "rescore_exit_code": result.returncode,
            "error": error_lines,
            "scope": "CLI name resolution on a synthetic valid Inspect log; no judge call",
        }, indent=2))


if __name__ == "__main__":
    main()
