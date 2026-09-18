# Petri custom dimension `value`: accepted configuration fails after scoring

Authored and reproduced by OpenAI Codex with the owner's explicit September 18 authorization to find and file another distinct Petri issue. No independent human reproduction or maintainer acceptance is claimed.

Submitted as [Petri #161](https://github.com/meridianlabs-ai/inspect_petri/issues/161) by `trimcrae` on September 18 at 14:37:19 UTC. Posted body was read back and exactly matched the prepared report. [Receipt](2026-09-18-petri-custom-value-submission.json).

## Verification

`git ls-remote` confirmed upstream main is `e199ec1abcd10267c60cd7eb03035a76567d9e52` on September 18. Reused the existing editable checkout at `8b1f2925dd116bda752ddcecc2ca0865b57ed6d7`; its only differences from main are our rescoring documentation and test, not runtime code. Python 3.12.14, Inspect AI 0.3.263, Inspect Scout 0.5.2, Windows. Editable Petri package metadata reports `0.1.dev1`, so use the source SHA rather than treating that as a released version. These dependencies satisfy Petri's declared minimums but differ from uv.lock; the locked environment was not rerun.

The [self-contained reproduction](repro/petri/repro_custom_value_dimension.py) uses public `audit`, `JudgeDimension`, Inspect `eval`, and mock-model APIs. No production functions, renderer, parser, or metrics are patched. Both cases run the same completed hello conversation and return fixed judge scores 7 and 3.

| Custom dimension | Sample score | Eval status | Metrics |
|---|---|---|---|
| `ordinary_dimension` | `{ordinary_dimension: 7, concerning: 3}` | success | means 7 and 3 |
| `value` | `7` | error | none |

Error: `TypeError('A dictionary of metrics specified for a non-dictionary score')`.

The other dimension's score (`concerning: 3`) remains in score metadata; it is not irretrievably lost, but is absent from the score dictionary and ordinary metric aggregation. Both target responses are `Hello!`, ruling out an empty-audit failure. As a validation control, constructing `audit_judge` with `summary` correctly raises a reserved-name ValueError before generation.

The first reproduction assumed the historical aggregation behavior would still succeed with a scalar; that assertion failed. The final reproduction explicitly asserts the current late aggregation error, so this report does **not** claim silent success on the tested versions. All final assertions, focused Ruff lint, and formatting checks pass.

Root cause: Petri's `_alignment_answer_type` only reserves `highlights`, `summary`, and `justification`. Scout's structured answer handling gives a field named `value` the meaning of the entire result value, moving other fields to metadata. Petri still declares dictionary metrics. Rejecting this name at configuration time, or isolating dimension names from Scout result fields, would prevent the mismatch.

## Scope and deduplication

This is a custom-rubric configuration defect. Built-in dimension names are unaffected. No live-model prevalence, production impact, or benchmark-score change is measured. An affected audit may finish its model calls before failing during aggregation. Renaming the dimension is a workaround.

Reviewed the repository's issue list and 100 recently updated open/closed PRs. Targeted issue and PR searches covered `reserved`, `dimension value`, `dimension label`, `non-dictionary`, `reserved fields`, and `dimension names`. No matching report/fix was found. #109 is provenance; #113/#105 are missing/refused audit scoring; #112 is transcript rendering; #133 rejects empty tag selections. Those are separate mechanisms. Historical candidates already covered there were not refiled.

Local evidence logs: `C:/Users/mcrae/.codex/review-workspaces/petri-value-repro-20260918/` (four tiny logs from initial and final runs, total 116,411 bytes). Disk free space was 8.49 GiB, so no checkout, runtime, dependency download, or large artifact was created; the existing checkout and environment were reused.

## Related status

Our earlier Petri #159 is explicitly addressed by merged Inspect core [PR #5466](https://github.com/UKGovernmentBEIS/inspect_ai/pull/5466), merged September 18 at 06:58 UTC. Our draft Petri #160 remains open and should be reassessed against the core fix before advancing. Release availability and an independent retest of the new core fix have not been established here.
