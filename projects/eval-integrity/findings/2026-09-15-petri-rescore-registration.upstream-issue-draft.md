### Problem

The current [Rescoring Existing Logs documentation](https://github.com/meridianlabs-ai/inspect_petri/blob/e199ec1abcd10267c60cd7eb03035a76567d9e52/docs/using/results.qmd#L69-L82) recommends:

```bash
inspect score ./logs/audit.eval \
  --scorer inspect_petri/audit_judge \
  -S model=anthropic/claude-opus-4-7 \
  --action append
```

However, `audit_judge` is registered with `@scanner`, while `inspect score --scorer` resolves a scorer. On current main, the command fails before judging with:

```text
LookupError: inspect_petri/audit_judge was not found in the registry
```

### Reproduction

Install Petri at `e199ec1abcd10267c60cd7eb03035a76567d9e52` with its dependencies, then run [repro_rescore_registration.py](https://github.com/trimcrae/Alignment/blob/ededeb6332c57a5c0cc1130b2a1102d96b2bcb0d/projects/eval-integrity/findings/repro/petri/repro_rescore_registration.py):

```bash
python repro_rescore_registration.py
```

The script creates a successful synthetic Inspect `.eval` log without model calls, then invokes the real scoring CLI with `--scorer inspect_petri/audit_judge -S model=mockllm/model --action append --overwrite`. `--overwrite` suppresses the output-file confirmation for this disposable log. A control invocation using `--scorer match` succeeds on that same log.

Observed: original evaluation succeeds; `match` rescoring exits 0; Petri rescoring exits 1 with the registry error. `registry_info(audit_judge).type` is `scanner`.

This deliberately uses a synthetic valid Inspect log to isolate CLI name resolution. It is not an end-to-end Petri audit/timeline test; no judge model is called. The name-resolution failure occurs before those contents can be scored.

### Expected behavior / impact

The documented command should resolve an appropriate registered scorer, or the documentation should provide the supported scanner-based rescoring workflow. Currently the advertised way to compare judge models on existing transcripts is blocked at startup. This report does not claim corrupted existing scores.

### Environment and related work

- Petri main: `e199ec1abcd10267c60cd7eb03035a76567d9e52`, checked September 15, 2026.
- Python 3.12.14, Windows, Inspect AI 0.3.263, Inspect Scout 0.5.2.
- Related: #60 (closed rescoring question) and #88 (judge override support). This reports a present registry mismatch in their documented workflow. #147 updated results documentation, but the command above remains on current main. #113 concerns empty/failed audit scoring, not this CLI failure.
- Searched open/closed issues and PRs for `rescore`, `No timeline`, and `audit_judge` with `scorer`; no report covering this registry failure was found.

Prepared and locally executed by OpenAI Codex. Submitted with the repository owner's authorization; no independent human reproduction or maintainer confirmation is claimed.
