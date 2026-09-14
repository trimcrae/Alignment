"""Probe unmodified AgentHarm benign tools from two working directories.

Usage: python benign_cwd_probe.py /path/to/inspect_evals
Requires inspect-ai. No model, dataset download, or API key is used.
Produced by Codex; this tests tool execution, not the full evaluation pipeline.
"""

import argparse
import asyncio
import importlib.util
import json
import os
import platform
import subprocess
import tempfile
from importlib.metadata import version
from pathlib import Path


def load_tool(path, name):
    spec = importlib.util.spec_from_file_location(f"cwd_probe_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, name)()


async def probe(tools):
    results = {}
    calls = [
        ("read_file", {"file": "to_do.txt"}),
        ("edit_txt", {"file_path": "to_do.txt", "line_number": 1,
                      "new_content": "Harmless reproduction control"}),
        ("convert_pdf_to_text", {"file_path": "/home/public_story.pdf"}),
    ]
    expected_prefixes = {
        "read_file": "0:",
        "edit_txt": "Updated line 1",
        "convert_pdf_to_text": "PDF content from",
    }
    for name, kwargs in calls:
        try:
            output = await tools[name](**kwargs)
            results[name] = (
                "file_not_found_result" if "Error: File not found" in output
                else "ok" if output.startswith(expected_prefixes[name])
                and "Error:" not in output else "unexpected_result"
            )
        except FileNotFoundError:
            results[name] = "FileNotFoundError"
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    args = parser.parse_args()
    checkout = args.checkout.resolve()
    package = checkout / "src/inspect_evals/agentharm"
    tool_dir = package / "benchmark/benign_tools"
    names = ["read_file", "edit_txt", "convert_pdf_to_text"]
    tools = {name: load_tool(tool_dir / f"{name}.py", name) for name in names}
    # The imported functions and Inspect decorators are real, not mocked.
    original_cwd = Path.cwd()
    try:
        os.chdir(package)
        package_results = asyncio.run(probe(tools))
        with tempfile.TemporaryDirectory(prefix="agentharm-benign-cwd-") as temp:
            try:
                os.chdir(temp)
                unrelated_results = asyncio.run(probe(tools))
            finally:
                os.chdir(original_cwd)
    finally:
        os.chdir(original_cwd)
    assert package_results == {name: "ok" for name in names}, package_results
    assert unrelated_results == {
        "read_file": "FileNotFoundError",
        "edit_txt": "FileNotFoundError",
        "convert_pdf_to_text": "file_not_found_result",
    }, unrelated_results
    commit = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
    ).strip()
    print(json.dumps({
        "inspect_evals_commit": commit,
        "inspect_ai_version": version("inspect-ai"),
        "python": platform.python_version(),
        "platform": platform.system(),
        "agentharm_package_cwd": package_results,
        "unrelated_cwd": unrelated_results,
        "scope": "Direct unmodified benign tool execution; no full task or model run",
    }, indent=2))


if __name__ == "__main__":
    main()
