# Dated follow-up receipts

Produced by OpenAI Codex (an AI agent), session `usage-sprint-2026-10-01`, against Alignment main `c79d38e9e49d9c2fd133b6c4faf6412760089afe`. The collection time and source timestamps are in [ledger.json](ledger.json). This is a focused status snapshot of six existing findings, not a fresh audit or a census of all findings.

The maintainer-calibration gate has been met for one defect. A ControlArena collaborator explicitly [confirmed the bug and fix](https://github.com/UKGovernmentBEIS/control-arena/pull/880#pullrequestreview-5337096299). [PR #880](https://github.com/UKGovernmentBEIS/control-arena/pull/880) first merged into an intermediate branch on September 28; [PR #883](https://github.com/UKGovernmentBEIS/control-arena/pull/883) then brought the fix to main. The #883 merge commit is `5792fe40f7ee7fbf4537b79588872e28fd5dbce3`. Its ancestry and the scorer source were independently checked at main `173c872f04ee661c7e1cf37f4fc610e0791ef0da`.

That confirmation concerns this specific verdict-inversion defect. It does not endorse the original severity counts, establish novelty for other findings, estimate live judge-failure frequency, or verify a released package. The scorer's mean still counts NOANSWER as zero rather than excluding the sample.

| Existing work | GitHub receipt at collection | Next action |
| --- | --- | --- |
| AgentHarm paths, inspect_evals #2439 / #2455 | Issue and fix PR open | Owner review and upstream response |
| ControlArena #878 / #880 / #883 | Issue closed; collaborator confirmation; both PRs merged; fix on pinned main | Check release inclusion separately; preserve aggregation caveat |
| Petri rescoring #159 / #160 | Issue open; fix PR open and draft | Owner review, locked-dependency CI, Quarto render |
| MASK honesty prefix, inspect_evals #2104 | Existing PR open; original finding duplicates it | Track existing PR |
| Petri custom dimension #161 | Issue open | Await upstream response |
| Inspect Robots, local Alignment #2 | Local issue open; upstream filing awaits owner review | Review existing draft and patch |

The older root README and NEXT-STEPS describe September 14. Pending [Alignment PR #1](https://github.com/trimcrae/Alignment/pull/1) carries subsequent triage and prior reproduction results; this directory complements that PR and uses commit-pinned links to its artifacts. It does not merge it or repeat its upstream submissions.

## Run the tooling

Node 20 or newer is sufficient. There is no dependency installation.

```bash
node projects/eval-integrity/follow-up/ledger-tool.mjs validate
node projects/eval-integrity/follow-up/ledger-tool.mjs test
node projects/eval-integrity/follow-up/ledger-tool.mjs check
```

The optional second argument selects another local JSON snapshot. `validate` checks receipt identities, real dates, state/closure consistency, merge fields, exact refs, provenance, linked maintainer evidence, and default-branch inclusion evidence. `test` runs regression cases against the committed fixture. `check` performs GET requests to the ten recorded issue/PR endpoints and prints current fields and changes. It leaves the snapshot file untouched.

Public API reads can be anonymous. An optional `GITHUB_TOKEN` can improve rate limits; read access is sufficient. Redirects are rejected, each CLI request has a 15-second timeout, failed reads remain explicit, and the report redacts the token from fetch errors. The tool does not send issues, comments, reviews or PRs.

The live check refreshes only issue/PR state. Maintainer quotes, repository default branch, commit ancestry, source content, and releases need separate evidence collection and review. If a changed head or merge conflicts with existing evidence, the report includes the current observation and `evidence_conflicts`; it does not silently retain a stronger claim. HTTP failures and evidence conflicts set a nonzero exit status. Changed but consistent state is informational.

## What the evidence fields mean

A linked approval alone is insufficient for bug confirmation: the selected quote must explicitly confirm the bug and fix, and its interpretation still requires review. The lexical validator is a guard against empty/generic approvals, not a general natural-language verifier. The recorded contributor association supplies role evidence; it does not replace reading the quote.

A closed issue alone is insufficient for a fix. A merge names its target branch. A claim of default-branch inclusion additionally needs repository metadata, the PR targeting that exact branch, an ancestry result binding its merge commit to the inspected head, and an independently pinned source excerpt. Release inclusion stays `not-checked` in schema 1; implementing release verification needs a separate evidence contract.

No original Python reproduction was executed in this sprint. The core validator, status logic, injected-fetch refresh logic, and regression cases were executed in the available V8 tool isolate. The Node filesystem/CLI wrapper and GitHub Actions workflow require CI execution; the handoff records its observed result without assuming success.

Each new receipt should preserve its dated API URL and pinned source anchors, and each new assertion should state its limits. Private reports and exploit details remain outside this status ledger.
