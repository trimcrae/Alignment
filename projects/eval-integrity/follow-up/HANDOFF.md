# Usage sprint handoff

Produced by OpenAI Codex (AI agent), session `usage-sprint-2026-10-01`. Collection and validation happened October 1, 2026 UTC. Base: `c79d38e9e49d9c2fd133b6c4faf6412760089afe`; existing triage artifacts: `7e9d49081993d029d1730dca8b95fc79c0e1623e` in pending Alignment PR #1. Branch: `codex/usage-sprint-2026-10-01-followup-ledger`.

## Completed and verified

- Collected 15 dated GitHub receipts for six actual follow-ups; no upstream outreach.
- Independently read ControlArena collaborator review 5337096299: explicit bug-and-fix confirmation.
- Verified #880 merged into an intermediate branch and #883 merged to main; comparison from #883 merge `5792fe40f7ee7fbf4537b79588872e28fd5dbce3` to inspected main `173c872f04ee661c7e1cf37f4fc610e0791ef0da` is ahead with zero commits behind and merge-base equal to the merge SHA.
- Read the pinned scorer: only CORRECT/INCORRECT invert; unparseable judge verdict is preserved.
- Executed 41 pure-JavaScript regression cases in the available V8 functions.exec isolate. The committed module bodies ran with their ESM import/export declarations removed solely for that execution; no production logic was substituted. Cases cover contradictory states, main/release inflation, timestamps, URLs, missing evidence, stale approval after head changes, HTTP failures, token redaction, and snapshot immutability.
- GitHub Actions run [36936107881](https://github.com/trimcrae/Alignment/actions/runs/36936107881), job 110616639788, completed successfully at first implementation commit `17a676edadde1c93d6441fd7dec19c07ad4800c2`. Logs show Node v22.23.3, CLI validation `valid: true`, and all original 36 cases passed. After review fixes, [run 36936407327](https://github.com/trimcrae/Alignment/actions/runs/36936407327), job 110617597386, succeeded at `c236e5d37747b407fff463f40c44c261cd1639bf`: Node v22.23.3, CLI `valid: true`, and all 40 cases passed. Core blob `741aacc9dc350c6237ff24cf48e76090389fcab6` and ledger blob `23a38f3c3ece66a85c2203b3b52d5fdd109d9376` were fetched back and exactly matched submitted content.
- Original Python reproductions, Quarto rendering, live Node fetch transport, and package release inclusion were not executed/verified in this sprint.

## Independent review

A separate AI reviewer independently checked the collaborator quote, the intermediate merge target, and the exact main source and existing regression test. The reviewer stressed keeping confirmation, approval, merge target, source observation, and release inclusion separate; the data and validator implement that separation. The reviewer also independently fetched the 13 then-current non-file receipts and pinned source; all fields matched, and injecting actual API payloads into the checker returned ten unchanged observations without errors. All original 36 committed regression cases passed independently.

The review found two schema gaps: inconsistent comparison counts/status could pass, and inspected source/ancestry head lacked a separate branch-head receipt. Both were fixed: status/count/merge-base consistency is enforced, and a dated branches/main receipt binds source and comparison to the actual observed default-branch head. Five regression cases were added (41 total), including merged-date/closure and merged-draft consistency. The reviewer independently reran all 40 cases at the first review-fix commit and verified both required gaps were closed. A final optional guard also rejects a diverged comparison with identical base/head SHAs; its regression passed with all 41 cases in V8. No human review or new Python execution is claimed.

## Source release check completed

The next bounded session executed the release/tag check described below. [Dated evidence](2026-10-01-controlarena-release-check.md) and [86-tag receipts](2026-10-01-controlarena-release-check.json) show no observed source tag descends from the confirmed fix. Latest published source release v19.0.0 is 13 commits behind and still has the original inversion; distribution package content/publication remains unknown. The independent reviewer spot-checked latest release metadata and ancestry only. Code and the six-record ledger remain at the reviewed 41-test implementation. Latest implementation CI: [run 36936638185](https://github.com/trimcrae/Alignment/actions/runs/36936638185) succeeded at `a09974d9fd9283473127b3b20f4a77c54afb0579`, Node v22.23.3, validation true, 41 cases passed.

## Original release-check plan (completed for GitHub source tags)

Verify ControlArena package-release inclusion for this one accepted fix. Read the releases/tags list, pin candidate release commits, prove whether `5792fe40f7ee7fbf4537b79588872e28fd5dbce3` is an ancestor of each candidate, and record the earliest verifiable containing tag with dated receipts. Distinguish a release tag containing the commit from verification of a built/distributed wheel. Add a narrowly scoped release-evidence contract and regression cases for non-containing tags, unknown ancestry, and prereleases; keep unknown outcomes explicit. Do not expand to another audit until these receipts and existing validation gaps are resolved.

## Next bounded implementation

The ranked wider project is a per-model dangerous-capability determination/release-artifact ledger (research/README.md section 5). Begin with a schema, one source-verifiable artifact, and offline provenance checks; no API-key-dependent evaluation runs or paid workloads are authorized by this handoff.

## Commands for the next session

```bash
node projects/eval-integrity/follow-up/ledger-tool.mjs validate
node projects/eval-integrity/follow-up/ledger-tool.mjs test
node projects/eval-integrity/follow-up/ledger-tool.mjs check
```

The last command prints live issue/PR observations and cannot overwrite the snapshot. Confirmation, ancestry, source and releases must be independently refreshed. Review pending local issue #2 and pending PR #1 in the owner's normal review flow. Do not merge, deploy, or send new upstream reports as part of this follow-on work.
