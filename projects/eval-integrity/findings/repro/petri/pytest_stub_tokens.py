"""pytest plugin: replace tiktoken-based token estimates with a char heuristic.

The Petri e2e tests drive `mockllm/model` through its iterator path, which calls
`ModelAPI.count_tokens()` -> tiktoken -> download of `o200k_base.tiktoken` from
openaipublic.blob.core.windows.net. That host is blocked in this sandbox, so
146 tests fail with a ProxyError before exercising anything Petri-specific.

Usage (from the inspect_petri checkout):
  PYTHONPATH=../findings/repro/petri .venv/bin/python -m pytest tests -o addopts="" -p pytest_stub_tokens
"""

from __future__ import annotations


def pytest_configure(config):  # type: ignore[no-untyped-def]
    from inspect_ai.model._model import ModelAPI

    async def _count_text_tokens(self, text: str) -> int:  # type: ignore[no-untyped-def]
        return len(text) // 4 + 1

    ModelAPI.count_text_tokens = _count_text_tokens  # type: ignore[method-assign]
