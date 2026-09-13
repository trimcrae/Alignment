"""Run the port's own test-suite with the tiktoken network stub applied.

The sandbox blocks openaipublic.blob.core.windows.net, which inspect's mockllm needs for token
accounting. This wrapper installs the same stub as conftest.py, then invokes pytest on
inspect_evals/tests/agentic_misalignment. Usage:
  cd inspect_evals && .venv/bin/python ../findings/repro/agentic_misalignment/run_port_tests_with_stub.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conftest  # noqa: F401  (applies the tiktoken stub)
import pytest

HERE = Path(__file__).resolve().parents[3] / "inspect_evals" / "tests" / "agentic_misalignment"
sys.exit(pytest.main([str(HERE), "-q", "-p", "no:cacheprovider", "--no-header", "-rN"]))
