# Additional upstream triage — September 15, 2026 (America/New_York)

Authored and executed by OpenAI Codex. The owner requested additional filings in other repositories while awaiting AgentHarm feedback, superseding the earlier one-issue gate for this work. No independent human reproduction or maintainer confirmation is claimed.

## Filed

| Repository | Issue | Verified behavior |
|---|---|---|
| ControlArena | [#878](https://github.com/UKGovernmentBEIS/control-arena/issues/878) | Exhausted judge parsing returns `N`; SAE side-task scorer converts it to `C`. |
| Petri | [#159](https://github.com/meridianlabs-ai/inspect_petri/issues/159) | Documented `inspect score --scorer inspect_petri/audit_judge` fails registry resolution because the judge is a scanner. |

Posted as `trimcrae` at 2026-09-16 00:04:43/44 UTC (September 15 locally). API response bodies matched the prepared reports. Submission receipts: [ControlArena](2026-09-15-controlarena-submission.json), [Petri](2026-09-15-petri-submission.json). Exact report bodies: [ControlArena](2026-09-15-controlarena-judge-failure.upstream-issue-draft.md), [Petri](2026-09-15-petri-rescore-registration.upstream-issue-draft.md).

## Verification

Source revisions: ControlArena `b9d19de0c6142d6c62ae0e1dc13d9e62b8b12a3e`; Petri `e199ec1abcd10267c60cd7eb03035a76567d9e52`. Python 3.12.14, Windows, Inspect AI 0.3.263, Inspect Scout 0.5.2. Reused the existing audit environment and created sparse source checkouts after measuring disk headroom. Relevant dependencies were installed; this was not the complete ControlArena development environment or suite.

Executed [ControlArena runner](repro/control_arena/repro_sae_judge_failure.py) against the actual parser and scorer, replacing only model generation:

| Reply | Raw judge | Side task | Calls per path |
|---|---|---|---|
| Unparseable | N | C | 3 |
| Valid accept | C | I | 1 |
| Valid reject | I | C | 1 |

Executed [Petri runner](repro/petri/repro_rescore_registration.py): original synthetic log `success`; `match` control exit 0; Petri rescore exit 1 with `LookupError: inspect_petri/audit_judge was not found in the registry`; registration type `scanner`. The initial control required adding `--overwrite` to suppress Inspect's file confirmation; the final runner passed both control and failure assertions. This isolates CLI resolution, not a real Petri audit or timeline scoring run.

No live models, private exploit demonstrations, large datasets, or Docker were used. ControlArena can overstate successful sabotage under this failure condition; live prevalence and aggregate magnitude are unmeasured. Petri's report is a workflow defect, not evidence that existing scores are corrupted.

## Duplicate checks

ControlArena open/closed issue and PR searches used `NOANSWER`, `sae_interp_sabotage`, `score_side_task`, and SAE judge terms. Results about DTR metadata, monitors, and APPS addressed different code paths.

Petri searches used `rescore`, `No timeline`, and `audit_judge` with `scorer`. #60 is a closed rescoring question; #88 added judge override support; merged #147 updated documentation but current main still contains the failing command. #113 is the distinct known empty/failed-audit issue. No duplicate of the registry failure was found.

The prior Inspect empty-target candidate remains intended behavior per upstream tests; Petri empty-audit and MakeMeSay parser findings remain overlaps, not fresh issue candidates. AgentHarm #2439 remains pending. Future maintainer feedback may change these assessments.
