"""AI-authored by OpenAI Codex. Finite combined-tree CPU validation only.

Run by the integration workflow inside a Linux network namespace. Existing
offline suites run unchanged; collectors' executable entrypoints are never run.
All receipt output is outside the tracked tree.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MANIFEST = json.loads((HERE / "source-manifest.json").read_text())
RECORDS = []
NODE_TOTAL = 0
PYTHON_TOTAL = 0


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def blob(raw):
    return hashlib.sha1(("blob " + str(len(raw))).encode() + b"\0" + raw).hexdigest()


def tree_entries(ref):
    raw = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "-r", "-z", ref],
                         check=True, capture_output=True).stdout
    result = {}
    for row in raw.split(b"\0"):
        if not row:
            continue
        meta, path = row.decode().split("\t", 1)
        mode, kind, sha = meta.split()
        assert kind == "blob"
        result[path] = {"mode": mode, "sha": sha}
    return result


def bindings():
    expected = {x["path"]: {"mode": x["mode"], "sha": x["sha"]}
                for x in MANIFEST["source_union_files"]}
    assert tree_entries(MANIFEST["source_union_commit"]) == expected
    assert git("rev-parse", MANIFEST["source_union_commit"] + "^{tree}") == MANIFEST["source_union_tree"]
    current = tree_entries("HEAD")
    manual = {x["path"]: x for x in MANIFEST["manual_trigger_retirements"]}
    for path, pin in expected.items():
        raw = (ROOT / path).read_bytes()
        assert current[path]["mode"] == pin["mode"], path
        if path in manual:
            original = subprocess.run(["git", "-C", str(ROOT), "cat-file", "blob", pin["sha"]],
                                      check=True, capture_output=True).stdout
            start, end = original.index(b"on:\n"), original.index(b"permissions:\n")
            wanted = original[:start] + b"on:\n  workflow_dispatch:\n" + original[end:]
            assert raw == wanted, path
        else:
            assert blob(raw) == pin["sha"], path
        assert blob(raw) == current[path]["sha"], path
    extras = set(current) - set(expected)
    assert all(p.startswith("projects/usage-sprint-2026-10-01-integration/") or
               p == ".github/workflows/completed-sprint-integration.yml" for p in extras), extras
    for source in MANIFEST["sources"]:
        sha = source["integration_merge"]
        assert git("rev-list", "--parents", "-n", "1", sha).split() == [sha] + source["integration_parents"]
        assert git("merge-base", *source["integration_parents"]) == source["merge_base"]
        subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", source["head"], "HEAD"], check=True)
    entry = json.loads((ROOT / "projects/model-safety-ledger/providers/meta-llama4/policy-entry/entry-evidence.json").read_text())
    raw = (ROOT / entry["source"]["path"]).read_bytes()
    assert len(raw) == entry["source"]["utf8_byte_count"]
    assert hashlib.sha256(raw).hexdigest() == entry["source"]["sha256"]
    assert blob(raw) == entry["source"]["git_blob_sha1"]
    for cite in entry["citations"]:
        assert raw[cite["start_byte"]:cite["end_byte"]] == cite["quote"].encode(), cite["id"]
    assert len(entry["citations"]) == 5
    print("INTEGRATION BINDINGS: 237 source-union file/mode bindings, 9 two-parent merges, 5 reused Meta policy-entry quote spans passed", flush=True)
    return {"source_union_file_bindings": len(expected), "two_parent_merges": 9,
            "manual_trigger_retirements": 3, "meta_policy_entry_quotes": 5,
            "tracked_files": current}


def run(label, cmd, expected_node=None, expected_python=None):
    global NODE_TOTAL, PYTHON_TOTAL
    print("\nCHECK: " + label, flush=True)
    started = time.monotonic()
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=180)
    print(result.stdout, end="", flush=True)
    print(result.stderr, end="", flush=True)
    record = {"label": label, "command": cmd, "exit_code": result.returncode,
              "seconds": round(time.monotonic() - started, 3),
              "stdout_sha256": hashlib.sha256(result.stdout.encode()).hexdigest(),
              "stderr_sha256": hashlib.sha256(result.stderr.encode()).hexdigest()}
    RECORDS.append(record)
    assert result.returncode == 0, label
    if expected_node is not None:
        out = json.loads(result.stdout)
        count = out.get("checks", out.get("passed"))
        assert count == expected_node, (label, count, expected_node)
        record["observed_node_checks"] = count
        NODE_TOTAL += count
    if expected_python is not None:
        found = re.search(r"Ran (\d+) tests? in ", result.stdout + result.stderr)
        assert found and int(found.group(1)) == expected_python, label
        record["observed_python_tests"] = int(found.group(1))
        PYTHON_TOTAL += int(found.group(1))


def main(receipt):
    document = {"schema": "completed-sprint-execution-v1",
                "authorship": "OpenAI Codex AI agent",
                "source_commit": git("rev-parse", "HEAD"), "source_tree": git("rev-parse", "HEAD^{tree}"),
                "github_sha": os.environ.get("GITHUB_SHA"), "run_id": os.environ.get("GITHUB_RUN_ID"),
                "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"), "event": os.environ.get("GITHUB_EVENT_NAME"),
                "commands": RECORDS, "result": "RUNNING",
                "limits": "CPU/source-consistency only; no scientific model validation, inference, source reacquisition or human-review claim."}
    try:
        interfaces = [name for _, name in socket.if_nameindex()]
        assert set(interfaces) == {"lo"}, interfaces
        document["network_namespace_interfaces"] = interfaces
        print("NETWORK: separate namespace has loopback only; provider networking unavailable", flush=True)
        document["bindings"] = bindings()
        for label, cmd in [("Node runtime", ["node", "--version"]), ("Python runtime", [sys.executable, "--version"]),
                           ("Bash runtime", ["bash", "--version"]), ("Git runtime", ["git", "--version"]),
                           ("pypdf runtime", [sys.executable, "-c", "import pypdf;print(pypdf.__version__)"])]:
            run(label, cmd)
        syntax_files = [ROOT / p for p in document["bindings"]["tracked_files"]
                        if p.endswith(".py") and (p.startswith("projects/model-safety-ledger/") or
                        p == "projects/eval-integrity/env/test_audit_env_pins.py" or p.startswith(str(HERE.relative_to(ROOT)) + "/"))]
        for path in syntax_files:
            ast.parse(path.read_text(), filename=str(path))
        print("PYTHON SYNTAX: " + str(len(syntax_files)) + " files passed", flush=True)
        for path in document["bindings"]["tracked_files"]:
            if path.endswith(".mjs"):
                run("Node syntax " + path, ["node", "--check", path])
        run("Integration runner syntax", [sys.executable, "-c", "import ast,pathlib;ast.parse(pathlib.Path('" + str(HERE.relative_to(ROOT)) + "/run-offline.py').read_text())"])
        run("Audit helper Bash syntax", ["bash", "-n", "projects/eval-integrity/env/setup-audit-env.sh"])
        follow = "projects/eval-integrity/follow-up/ledger-tool.mjs"
        run("Follow-up ledger evidence", ["node", follow, "validate"])
        run("Follow-up ledger regressions", ["node", follow, "test"], expected_node=41)
        model = "projects/model-safety-ledger/ledger-tool.mjs"
        run("OpenAI native evidence", ["node", model, "validate"])
        run("OpenAI native regressions", ["node", model, "test"], expected_node=84)
        run("OpenAI scoped unknown summary", ["node", model, "summary"])
        timing = "projects/model-safety-ledger/release-timing/tool.mjs"
        run("Release timing bindings", ["node", timing, "validate"])
        run("Release timing regressions", ["node", timing, "test"], expected_node=50)
        run("Release timing file hashes", ["node", timing, "hashes"])
        anth = "projects/model-safety-ledger/providers/anthropic-claude4/"
        run("Anthropic native evidence", ["node", anth + "tool.mjs", "validate"])
        run("Anthropic native regressions", ["node", anth + "tool.mjs", "test"], expected_node=70)
        run("Anthropic mocked collector tests", [sys.executable, anth + "test_collect.py"], expected_python=15)
        run("Anthropic scoped unknown summary", ["node", anth + "tool.mjs", "summary"])
        rsp = anth + "rsp-version/"
        run("RSP inherited-source supplement", ["node", rsp + "tool.mjs", "validate"])
        run("RSP temporal regressions", ["node", rsp + "tool.mjs", "test"], expected_node=49)
        run("RSP mocked selector tests", [sys.executable, rsp + "test_collect.py"], expected_python=22)
        run("RSP finite gap summary", ["node", rsp + "tool.mjs", "summary"])
        google = "projects/model-safety-ledger/providers/google-deepmind-gemini-pro/"
        run("Google unknown/source regressions", ["node", google + "test.mjs"], expected_node=60)
        run("Google mocked collector tests", [sys.executable, google + "test-collect.py"], expected_python=27)
        run("Google mocked exact-stage tests", [sys.executable, google + "test-card-html.py"], expected_python=5)
        run("Google retained-source verification", [sys.executable, google + "verify-source.py"])
        run("Google partial source summary", ["node", google + "validate.mjs"])
        meta = "projects/model-safety-ledger/providers/meta-llama4/"
        run("Meta native/source regressions", ["node", meta + "test.mjs"], expected_node=81)
        run("Meta UTF8 source tests", [sys.executable, meta + "test-source.py"], expected_python=10)
        run("Meta retained-source verification", [sys.executable, meta + "verify-source.py"])
        run("Meta partial native summary", ["node", meta + "validate.mjs"])
        run("Audit original/prior/final Bash Git fixtures", [sys.executable, "projects/eval-integrity/env/test_audit_env_pins.py"], expected_python=31)
        run("Clean tracked diff", ["git", "diff", "--exit-code"])
        assert git("status", "--porcelain") == ""
        assert NODE_TOTAL == 435 and PYTHON_TOTAL == 110
        document["observed_totals"] = {"node_checks": NODE_TOTAL, "python_tests": PYTHON_TOTAL,
                                      "python_syntax_files": len(syntax_files)}
        document["tracked_tree"] = "CLEAN"
        document["result"] = "PASS"
        print("COMBINED TOTALS: 435 distinct Node checks; 110 Python tests (including 31 real Bash/Git fixture tests); clean tracked tree", flush=True)
    except Exception as error:
        document["result"] = "FAIL"
        document["error"] = str(error)
        raise
    finally:
        Path(receipt).write_text(json.dumps(document, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", required=True)
    main(parser.parse_args().receipt)
