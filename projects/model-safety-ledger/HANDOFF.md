# 2026-10-01 bounded handoff

Produced by OpenAI Codex (AI agent, GPT-6). Human review not performed.

- Scope: research priorities 2 and 3; two gpt-oss variants, one model card and one related safety report.
- Evidence: acquisition commit `5c4b06403ca34b565f10e4e8fd7737e84c9d4ff3`, successful actual run [36941633243](https://github.com/trimcrae/Alignment/actions/runs/36941633243), job 110634241560.
- Model-card received-byte SHA256: `8839e1efdf835be08ad1d60bfa99c8c4fdde15c7ef49eda6a8b910575fb699a0` (35 PDF pages).
- Safety-report received-byte SHA256: `dbd97a15deaa6c37976ef809c10879213b39115c51b98f1cf645fd33129e66d7` (16 PDF pages).
- Selected receipt SHA256: `6440a6d9b10341da558071ea87052df600a26568fc8d319c0b77604e4eb94657`. Only selected original cover/page-4 spans are committed, with subset provenance.
- Current result: five provider-reported 120b slots; five corresponding 20b slots unknown. Default/adversarial configurations remain separate. Safety report is not a final determination.
- Unknowns: framework version, both model-release dates, and both model-card launch-availability entries. Cover date, current fetch and historical links do not establish release-time bytes.
- Completed validation: exact source `e91dc74a798b8e5236166fa900077f2794a88e8d` passed actual Node 22.23.3 [run 36945362067](https://github.com/trimcrae/Alignment/actions/runs/36945362067), job 110646137019: syntax, evidence validation, **84 checks (80 invalid cases)**, unknown summary and clean tracked status. Independent execution of the actual core/regression harness in V8 reproduced all 84 checks. No model inference or experimental capability replication was run.
- Independent evidence review cleared every one of the eight seeded citations against the original acquisition receipt: exact quotes, PDF pages, hashes, provider, model and configuration scope. The selected receipt and ledger SHA256s were independently recomputed. PDF hashes were corroborated against the successful received-byte acquisition receipt, without downloading the documents again.
- Independent code review found one demonstrated gap: swapping quoted native domain labels could misclassify a domain while still validating. The focused repair binds domain IDs to source-backed names by framework and configuration; four new regressions reject the demonstrated aliases/swaps. The repaired source and tests were independently reviewed with no remaining scoped blocker.
- Human review remains unperformed. Model variant, reasoning effort, subscription usage and task wall time were not exposed. The final CPU CI job lasted seven seconds (00:19:00–00:19:07 UTC on 2026-10-02).
- Next useful question: dated primary/archival release timing and artifact-edition availability. Do not re-acquire unchanged documents or repeat completed ControlArena ancestry checks.

## Final receipts and limits

Draft [PR4](https://github.com/trimcrae/Alignment/pull/4) remains reviewable; no main merge or external outreach was performed. Initial implementation `4d41c5c4fd287df7d7a356a9c298815ee6a3b29d` passed 80 actual Node checks in [run 36943629686](https://github.com/trimcrae/Alignment/actions/runs/36943629686). The later repair changes only core and regression tests; all seeded evidence, source hashes, CLI and workflow remain unchanged. This final receipt-only commit changes documentation and logs, preserving the tested source.

Machine-readable [validation receipt](validation-receipt.json) records exact source/code/data hashes, review coverage and limitations. Original Node logs are preserved at [initial log](node-ci-job-110640616737.log) and [settled log](node-ci-job-110646137019.log). Validation proves consistency with selected primary evidence, not the truth of provider capability assessments. No release timing, launch-edition availability, framework version, 20b determination or independent experimental finding was inferred.

The bounded task is complete. Reuse unchanged source receipts; the next task is dated primary/archival evidence for model-release timing and which model-card edition was available at launch, with an explicit missing-evidence stop condition.
