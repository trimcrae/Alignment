## Summary

Fixes #159. The results guide currently passes `inspect_petri/audit_judge` to `inspect score --scorer`, but `audit_judge` is registered as a Scout scanner. Replace that command with the supported `scout scan` workflow and a Python equivalent using `scan` and `transcripts_from`.

Explain that the workflow reads saved target timelines, including rollback branches, and writes separate Scout results without modifying the source `.eval` log. Document how to carry over custom dimensions and named-audit selection.

Add an end-to-end test that runs a Petri audit with a rollback using mock models, saves the log, rescans it with a replacement judge, and verifies both branches reach that judge, the new score is persisted, and the original file is unchanged. The test also resolves the documented CLI scanner name and arguments through a dry run. No new scorer registration or runtime API is needed.

## Validation

- New end-to-end test passes locally; judge score changes from 1 in the original audit to the injected replacement score 7 in the separate scan results. No paid models or external datasets are used.
- Full Ruff lint and formatting checks pass (309 files).
- Changed-test Pyright passes. Full Pyright reports one error in untouched `_realism/approver.py:177` (`model_roles()` can now return `list[Model]`, which `get_model(default=...)` does not accept).
- Full local pytest completed: 754 passed and 6 failed. Five failures were Windows default-encoding errors in unchanged canary-coverage tests; all five passed on rerun with `PYTHONUTF8=1`. The remaining unchanged `test_rejects_symlink_escape` cannot create its symlink on this Windows account (`WinError 1314`). Thus 759 of the 760 collected tests passed across the run and encoding recheck; this is not a single fully green suite run.
- Upstream Build and PR Title Lint workflows await maintainer approval (`action_required`). A separate attempt to dispatch the existing Build workflow in the new fork returned 404; no fork CI result is claimed.
- Local Python 3.12.14, Inspect AI 0.3.263, Inspect Scout 0.5.2, pytest 9.1.1 differ from the project's locked Inspect AI 0.3.237 and Scout 0.4.39. Locked-environment CI validation remains pending.
- Quarto site rendering was not run.

Authored and tested by OpenAI Codex with the repository owner's authorization. Draft for review; no independent human review or maintainer acceptance is claimed.
