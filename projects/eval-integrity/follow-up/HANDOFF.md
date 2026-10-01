# Usage sprint handoff

Produced by OpenAI Codex (AI agent), session `usage-sprint-2026-10-01`. Collection and validation happened October 1, 2026 UTC. Base: `c79d38e9e49d9c2fd133b6c4faf6412760089afe`; existing triage artifacts: `7e9d49081993d029d1730dca8b95fc79c0e1623e` in pending Alignment PR #1. Branch: `codex/usage-sprint-2026-10-01-followup-ledger`.

## Completed and verified

- Collected 14 dated GitHub receipts for six actual follow-ups; no upstream outreach.
- Independently read ControlArena collaborator review 5337096299: explicit bug-and-fix confirmation.
- Verified #880 merged into an intermediate branch and #883 merged to main; comparison from #883 merge `5792fe40f7ee7fbf4537b79588872e28fd5dbce3` to inspected main `173c872f04ee661c7e1cf37f4fc610e0791ef0da` is ahead with zero commits behind and merge-base equal to the merge SHA.
- Read the pinned scorer: only CORRECT/INCORRECT invert; unparseable judge verdict is preserved.
- Executed 36 pure-JavaScript regression cases in the available V8 functions.exec isolate. The committed module bodies ran with their ESM import/export declarations removed solely for that execution; no production logic was substituted. Cases cover contradictory states, main/release inflation, timestamps, URLs, missing evidence, stale approval after head changes, HTTP failures, token redaction, and snapshot immutability.
- Node CLI/file access, the GitHub Actions workflow, original Python reproductions, Quarto rendering, and package release inclusion were not executed/verified locally.

## Independent review

A separate AI reviewer independently checked the collaborator quote, the intermediate merge target, and the exact main source and existing regression test. The reviewer stressed keeping confirmation, approval, merge target, source observation, and release inclusion separate; the data and validator implement that separation. Detailed code review and CI status will be recorded here before handoff completion.

## First next bounded implementation

Verify ControlArena package-release inclusion for this one accepted fix. Read the releases/tags list, pin candidate release commits, prove whether `5792fe40f7ee7fbf4537b79588872e28fd5dbce3` is an ancestor of each candidate, and record the earliest verifiable containing tag with dated receipts. Distinguish a release tag containing the commit from verification of a built/distributed wheel. Add a narrowly scoped release-evidence contract and regression cases for non-containing tags, unknown ancestry, and prereleases; keep unknown outcomes explicit. Do not expand to another audit until these receipts and existing validation gaps are resolved.

After that, the ranked wider project is a per-model dangerous-capability determination/release-artifact ledger (research/README.md section 5). Begin with a schema, one source-verifiable artifact, and offline provenance checks; no API-key-dependent evaluation runs or paid workloads are authorized by this handoff.

## Commands for the next session

```bash
node projects/eval-integrity/follow-up/ledger-tool.mjs validate
node projects/eval-integrity/follow-up/ledger-tool.mjs test
node projects/eval-integrity/follow-up/ledger-tool.mjs check
```

The last command prints live issue/PR observations and cannot overwrite the snapshot. Confirmation, ancestry, source and releases must be independently refreshed. Review pending local issue #2 and pending PR #1 in the owner's normal review flow. Do not merge, deploy, or send new upstream reports as part of this follow-on work.
