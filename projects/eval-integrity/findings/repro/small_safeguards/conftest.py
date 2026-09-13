"""Test-environment shim only (no scoring logic is touched).

This sandbox cannot reach openaipublic.blob.core.windows.net, which tiktoken
contacts to fetch the ``o200k_base`` encoding that inspect_ai's ``mockllm``
provider uses for token *counting* (inspect_ai/model/_tokens.py:116-118).
Without the shim every ``inspect_ai.eval(...)`` with a mockllm model errors
before scoring.  Replace the encoder with a whitespace tokenizer so the
mockllm-based reproductions below can run offline.  Token counts are not used
by any of the scorers/metrics under test.
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
