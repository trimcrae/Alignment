# Anthropic Claude 4 native evidence seed

Produced by OpenAI Codex (AI agent, GPT-6), usage-sprint-2026-10-01. Human review not performed.

This bounded seed transcribes provider-native deployment decisions and aggregate capability assessments from the May 2025 Claude 4 system card observed on 2026-10-02. It is a separate provider directory; the prior OpenAI ledger and release-timing supplements remain unchanged dated snapshots.

The card reports Opus 4 deployment under ASL-3 and Sonnet 4 under ASL-2. Its Opus ASL-3 deployment is explicitly precautionary and provisional: the provider has not yet determined a definitive threshold pass and cannot clearly rule out ASL-3 risks. Opus ASL-4 capabilities are reported ruled out. Sonnet ASL-3 assessment is reported below thresholds of concern; the selected evidence leaves the model-specific Sonnet ASL-4 outcome unknown. Deployment protections and capability assessments are separate axes. They are not mapped onto OpenAI High or treated as independently measured safety findings.

The card also states that its RSP does not stipulate a formal cyber threshold at any ASL level. This is the policy state described by this source, not a claim about the latest 2026 framework, no cyber evaluation or no cyber risk. Framework version, artifact edition, exact model release dates and launch-edition byte identity remain unknown. Unknown does not mean absent or unevaluated. A cover month and HTTP Last-Modified are metadata, not historical availability proof.

## Evidence and reproducibility

The original official pointer redirects to a provider CDN PDF. The received document is 4,976,826 bytes/124 pages, SHA256`5e3e63370473db1f1e499642ef8400250e19aba8cbb5f84f2b919cf2b27898cb`. [Corrected acquisition 36951404278](https://github.com/trimcrae/Alignment/actions/runs/36951404278), job 110664941297, ran source`bda723fb2678787fc0ec6e52ad742d63b618ab5a` once. The selected receipt reproduces only governance passages (pages 1, 3, 9, 10, 11, 88 and one cyber-policy sentence on 117) and retains source metadata, hashes and original span coordinates. Other evaluation/benchmark content is not reproduced. Original received PDF/full receipt are preserved by the workflow artifact for 90 days; original logs remain the acquisition recovery channel.

The first [acquisition 36951198584](https://github.com/trimcrae/Alignment/actions/runs/36951198584), job 110664323460, observed the official announcement but hit our collector's 2 MiB page limit on a direct PDF pointer. This was an implementation defect, not evidence of a missing card. A narrow correction used the originally planned 20 MiB PDF bound and fetched only that pointer; the announcement was not fetched again. No guessed CDN URL, mirror, model inference or outreach occurred. The first planned 180 s soft alarm could have been swallowed by broad exception handling; its actual job completed in 16 s. The correction uses a dedicated BaseException deadline and a five-minute workflow hard stop. Both original receipt hashes and exact run provenance are preserved.

The validator is deliberately bounded to this source, these models and native bindings. Adding providers or editions requires separate evidence/schema review. It rejects model/ASL swaps even when both names and levels occur in one quote, dropped provisional language, deployment/threshold conflation, inflated experimental or human verification, unsupported release/launch states, and altered source provenance. It validates consistency with received evidence, not the truth of provider assessments.

Run supported offline checks:

```sh
node projects/model-safety-ledger/providers/anthropic-claude4/tool.mjs validate
node projects/model-safety-ledger/providers/anthropic-claude4/tool.mjs test
python3 -m pip install pypdf==6.0.0
python3 projects/model-safety-ledger/providers/anthropic-claude4/test_collect.py
node projects/model-safety-ledger/providers/anthropic-claude4/tool.mjs summary
```

The Python tests use mocked public-source responses, including a PDF over 2 MiB and the real production limit-selection path; they make no source requests. See HANDOFF.md and validation-receipt.json for executed tests, exact tested revision, independent review, limitations and the next bounded task. No workflow dispatch or acquisition retry is needed to validate these committed records.
