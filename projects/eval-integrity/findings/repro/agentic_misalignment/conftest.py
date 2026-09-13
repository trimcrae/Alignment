"""Test environment shims for the agentic_misalignment repros.

1. tiktoken stub: inspect_ai's mockllm provider calls tiktoken.get_encoding("o200k_base"),
   which downloads the BPE file from openaipublic.blob.core.windows.net. That host is blocked
   in the audit sandbox, so we replace the encoder with a crude length-based one. This only
   affects token *accounting*; it has no effect on prompts, scores or metrics.
2. Put the official Anthropic clone and the scratch site-packages (lxml) on sys.path.
"""

import sys
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(AUDIT / "scratch_site"))  # lxml (installed with --target)
sys.path.insert(0, str(AUDIT / "agentic_misalignment_official"))  # official classifiers/

try:
    import tiktoken

    class _FakeEncoding:
        name = "fake-o200k_base"

        def encode(self, text, **_kwargs):
            return [0] * max(1, len(text) // 4)

        def decode(self, tokens, **_kwargs):
            return ""

    tiktoken.get_encoding = lambda *_a, **_k: _FakeEncoding()  # type: ignore[assignment]
    tiktoken.encoding_for_model = lambda *_a, **_k: _FakeEncoding()  # type: ignore[assignment]
except ImportError:  # pragma: no cover
    pass
