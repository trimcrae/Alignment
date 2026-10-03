## Summary

Fixes #878. When the SAE side-task judge fails to return a parseable verdict after three attempts, the current inversion changes `NOANSWER` (`N`) into `CORRECT` (`C`). Invert only valid `CORRECT`/`INCORRECT` verdicts and preserve the judge's failure value and explanation.

The combined scorer now retains `side_task_success: N` on exhausted parsing retries. Valid accept/reject verdicts, recovery after a malformed reply, and missing submissions retain their previous behavior. This corrects false side-task success. It does not change aggregation: Inspect's existing mean still maps `N` to zero rather than excluding the sample. Live judge-failure prevalence and aggregate impact have not been measured.

## Test Plan

With the project's development environment, run:

```bash
pytest control_arena/settings/sae_interp_sabotage/test_scorers.py -q
pytest control_arena/settings/sae_interp_sabotage/test_scorers.py --runtrio -q
ruff check control_arena/settings/sae_interp_sabotage/scorers.py control_arena/settings/sae_interp_sabotage/test_scorers.py
ruff format --check control_arena/settings/sae_interp_sabotage/scorers.py control_arena/settings/sae_interp_sabotage/test_scorers.py
pyright control_arena/settings/sae_interp_sabotage/scorers.py control_arena/settings/sae_interp_sabotage/test_scorers.py
```

Executed locally on Windows with Python 3.12.14, Inspect AI 0.3.263, pytest 9.1.1, and relevant dependencies in a reused audit environment:

- Before the production fix: 4 failures (`C` instead of `N`), 4 passes, and 8 trio variants skipped in the default invocation.
- After the fix: 8 passes on asyncio and 8 passes on trio, using separate invocations as the contributor guide requires. Each invocation skips the other backend's 8 variants.
- Ruff lint and formatting passed for both changed files. Targeted Pyright passed with the audit interpreter supplied via `--pythonpath`; the repository's configured `.venv` does not exist in this environment.
- Tests use Inspect's mock model provider with fixed `ModelOutput` responses and the actual judge parser. No model API, dataset, or sandbox is needed.

The full repository suite was not run: the reused environment contains the dependencies needed for these focused tests, not every setting's dependencies. Inspect emitted a non-fatal warning while loading an unrelated Petri entry point because Windows application control blocked its DuckDB DLL; the ControlArena tests completed.

Authored and tested by OpenAI Codex with the repository owner's authorization. This draft does not claim independent human review or maintainer confirmation.
