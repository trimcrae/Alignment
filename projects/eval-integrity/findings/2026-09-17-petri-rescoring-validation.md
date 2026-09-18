# Petri rescoring fix and validation

Authored and executed by OpenAI Codex with owner authorization on September 17, 2026 (America/New_York).

## Delivered

[Draft PR #160](https://github.com/meridianlabs-ai/inspect_petri/pull/160), head `8b1f2925dd116bda752ddcecc2ca0865b57ed6d7`, addresses [issue #159](https://github.com/meridianlabs-ai/inspect_petri/issues/159). Base: `e199ec1abcd10267c60cd7eb03035a76567d9e52`. It replaces the invalid `inspect score --scorer` instructions with `scout scan inspect_petri/audit_judge -T LOG -S model=MODEL --scans OUTPUT`, plus the equivalent Python API. It documents separate results, original-log preservation, dimension selection, and named timelines. No runtime API changes are needed.

The [submitted PR body](2026-09-17-petri-rescoring-pr.md) was updated after the full local test run. [Initial submission receipt](2026-09-17-petri-pr-submission.json) preserves the original posting time and source revision.

## End-to-end evidence

The new test creates an actual Petri `.eval` log using mock auditor, target, and judge models. The auditor creates one conversation, rolls back to the system message, creates a replacement conversation, and ends the audit. The initial judge assigns 1. The test then loads that persisted file through `transcripts_from`, scans it with a replacement `audit_judge`, and checks:

- Both the discarded and surviving target reply reach the replacement judge.
- The replacement judge runs once and the scan records `concerning: 7`.
- The original `.eval` bytes are unchanged.
- The documented scanner name, transcript input, model override, and output directory resolve through Scout's CLI in a dry run.

This tests saved timeline extraction and rescoring end to end, unlike the earlier generic-log registry reproduction. Model replies are synthetic; the test does not assess judge quality. CLI invocation is a dry run; Python performs the actual scan. The script executes no browser or UI.

One retained local evidence run is under `C:/Users/mcrae/.codex/review-workspaces/petri-rescore-test3-20260917/test_rescore_saved_audit_prese0/`, containing the original `.eval` and separate scan results. The source test is [tests/e2e/test_rescoring.py](https://github.com/trimcrae/inspect_petri/blob/8b1f2925dd116bda752ddcecc2ca0865b57ed6d7/tests/e2e/test_rescoring.py).

## Broader checks and limits

- New e2e test: passed.
- Full pytest: **754 passed, 6 failed**, 760 tests collected, 212.92 seconds with two workers.
- Five failures were CP1252 decoding errors in unchanged canary tests. Re-running those failures with `PYTHONUTF8=1` gave **5 passed**. The remaining test needs a symlink privilege unavailable on this account (`WinError 1314`, `test_rejects_symlink_escape`). Across the two runs, 759 tests passed; a single green full-suite run is not claimed.
- Full Ruff lint and format checks: passed, 309 Python files.
- Changed-test Pyright: passed. Full Pyright: one error in untouched `_realism/approver.py:177`, where the current Inspect API permits a model-role list but `get_model(default=...)` expects a single model. This patch does not alter that module.
- Quarto rendering was not run.
- Local environment: Python 3.12.14, Inspect AI 0.3.263, Scout 0.5.2, pytest 9.1.1. The repository lock uses Inspect AI 0.3.237 and Scout 0.4.39, so local success is not locked-environment validation.
- Upstream [Build run](https://github.com/meridianlabs-ai/inspect_petri/actions/runs/35290421695) and PR Title Lint require maintainer approval. The new fork lists zero registered workflows despite Actions being enabled; enable/dispatch calls for the existing `build.yaml` returned 404. No permissions or allowed-actions policy was changed, and no fork CI run started.

No independent human review, maintainer acceptance, model API measurement, or fully green hosted build is claimed.
