# Focused upstream issue draft

Destination: `UKGovernmentBEIS/inspect_evals`. Status: prepared, not submitted. AI-authored by Codex; human review has not been established. Refresh duplicate searches before filing. Use the title and body below in the bug-report form.

Title: [Bug] AgentHarm benign file tools fail outside the package working directory

## Short description

AgentHarm's benign `read_file`, `edit_txt`, and `convert_pdf_to_text` tools locate bundled content relative to the process working directory. The same calls succeed from `src/inspect_evals/agentharm` but fail from an unrelated directory, although the bundled files exist.

## Steps to reproduce

With `inspect-ai==0.3.263` installed and an `inspect_evals` checkout at `360484a06383f9260279938262d78ed646ddbca1`, save this as `repro.py` and run `python repro.py /path/to/inspect_evals`:

```python
import asyncio
import importlib.util
import os
from pathlib import Path
import sys
import tempfile

package = Path(sys.argv[1]).resolve() / "src/inspect_evals/agentharm"
spec = importlib.util.spec_from_file_location(
    "benign_read_file", package / "benchmark/benign_tools/read_file.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
read_file = module.read_file()
original = Path.cwd()
try:
    os.chdir(package)
    assert asyncio.run(read_file(file="to_do.txt")).startswith("0:")
    with tempfile.TemporaryDirectory() as unrelated:
        try:
            os.chdir(unrelated)
            asyncio.run(read_file(file="to_do.txt"))  # FileNotFoundError
        finally:
            os.chdir(original)
finally:
    os.chdir(original)
```

This imports the unmodified tool module with real Inspect decorators. It does not load the evaluation dataset or call a model.

## Expected behavior

Bundled simulated file content resolves independently of the caller's working directory. Identical tool calls should succeed from either directory.

## Actual behavior

| Call | Package directory | Unrelated temporary directory |
| --- | --- | --- |
| `read_file(file="to_do.txt")` | Returns numbered content | Raises `FileNotFoundError` |
| `edit_txt(file_path="to_do.txt", line_number=1, new_content="Harmless reproduction control")` | Returns update message | Raises `FileNotFoundError` |
| `convert_pdf_to_text(file_path="/home/public_story.pdf")` | Returns simulated PDF content | Returns text containing `Error: File not found` |

## Environment

- Windows, Python 3.12.14, `inspect-ai==0.3.263`.
- `inspect_evals` source: `360484a06383f9260279938262d78ed646ddbca1` (upstream main when checked on 2026-09-14).
- Direct benign-tool execution; no API key, model, Docker, or dataset download. The table was reproduced with all three real tools. This report does not claim a measured change to aggregate evaluation results or a new full-task reproduction.

## Additional context

The relative paths are in [`benign_tools/read_file.py`](https://github.com/UKGovernmentBEIS/inspect_evals/blob/360484a06383f9260279938262d78ed646ddbca1/src/inspect_evals/agentharm/benchmark/benign_tools/read_file.py), [`edit_txt.py`](https://github.com/UKGovernmentBEIS/inspect_evals/blob/360484a06383f9260279938262d78ed646ddbca1/src/inspect_evals/agentharm/benchmark/benign_tools/edit_txt.py), and [`convert_pdf_to_text.py`](https://github.com/UKGovernmentBEIS/inspect_evals/blob/360484a06383f9260279938262d78ed646ddbca1/src/inspect_evals/agentharm/benchmark/benign_tools/convert_pdf_to_text.py). Resolving fixture paths from each module's `__file__` would remove the dependence on process CWD; a regression should run from an unrelated temporary directory. This report is limited to that path-resolution defect.

Written and reproduced by Codex, an AI agent, at the repository owner's request.
