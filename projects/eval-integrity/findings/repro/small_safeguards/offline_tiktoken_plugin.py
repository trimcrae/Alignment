"""pytest plugin form of conftest.py's tiktoken shim, for re-running the upstream
test suites offline:

    PYTHONPATH=findings/repro/small_safeguards RUN_SLOW_TESTS=1 \
      .venv/bin/python -m pytest tests/makemesay ... -p offline_tiktoken_plugin

See conftest.py for why this is needed in this sandbox.
"""

import pytest
import tiktoken


class _DummyEncoding:
    name = "dummy-whitespace"

    def encode(self, text, *args, **kwargs):
        return text.split()

    def decode(self, tokens, *args, **kwargs):
        return " ".join(tokens)


@pytest.fixture(autouse=True)
def _offline_tiktoken(monkeypatch):
    monkeypatch.setattr(tiktoken, "get_encoding", lambda *a, **k: _DummyEncoding())
    monkeypatch.setattr(
        tiktoken, "encoding_for_model", lambda *a, **k: _DummyEncoding()
    )
    yield
