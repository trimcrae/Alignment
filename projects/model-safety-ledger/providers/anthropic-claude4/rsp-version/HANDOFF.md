# RSP edition bounded handoff, 2026-10-02

Produced by OpenAI Codex (AI agent, GPT-6). Human review not performed.

Draft [PR7](https://github.com/trimcrae/Alignment/pull/7) is stacked on completed draft PR6 at `4bff2e760c6e3297b96bf130b756dc43d36ce1d3`, branch `codex/usage-sprint-2026-10-01-anthropic-rsp-version`. Earlier Anthropic/OpenAI ledgers, model-specific ASL determinations, code and evidence remain unchanged dated snapshots. No inference/API, outreach, upstream issue/PR or main merge occurred.

The one actual source cycle met its stop condition with an explicit missing-evidence result. The original received May 2025 card's page 9 RSP annotation points to Anthropic's policy-update announcement, which declares October 15, 2024. One official route was observed now; no numeric policy version, immutable governing edition or launch-time policy bytes were established. These fields remain unknown; unknown does not mean absent or not applicable. The date is a provider-declared article date, not archived 2024-byte or historical-public-visibility proof. Its dated “all models ASL-2” statement and 2026 footer cannot override the acquired May 2025 card decisions or establish a governing policy edition.

## Actual receipts

- Initial `0a9656c15b816bad3f360a674e6994f1f58718c3`, [run 36956229264](https://github.com/trimcrae/Alignment/actions/runs/36956229264): invalid workflow, **zero jobs and zero source GETs**. Our runner-context placement in job-level environment was an implementation/configuration failure. The correction moved it into supported step contexts; this was not an inaccessible source, baseline environment failure or evidence of policy absence.
- Source `ffcc6faa08df990f303add33a518843faa831f4f`, [run 36956360948](https://github.com/trimcrae/Alignment/actions/runs/36956360948), job 110680066600, 02:35:51–02:36:06 UTC: reused owned artifact 11204066868/run 36951404278 and verified PDF SHA256`5e3e63370473db1f1e499642ef8400250e19aba8cbb5f84f2b919cf2b27898cb` before inspecting only RSP annotations on pages 9/10. One page 9 URI, one official HTML route 200/171,813 bytes, **zero fresh card-source GETs and zero optional policy-PDF GETs**.
- [Original acquisition receipt](evidence/acquisition.json): 10,671 UTF-8 bytes, SHA256`4b3363dcd44fe0469ff3415874d0f493beafd6f2eb9e1770022e786460767ca9`. Original source log SHA256`d84dac5a821861bc8ef29439e879c0b3d69ad4cd7b05fbf27ccc10388b69e27d`. Receipt artifact  11205553533, archive SHA256`15d40e3152a6299f36f07e0903a1b549ea589a38cdb0d8d44421529944e040e5`, expires`2026-12-31T02:35:47Z`.
- HTML source-body and complete normalized-text digests are collector-computed from the received response. Raw HTML was not retained. Independent reviewers checked selected spans/card URI/date quote against the original acquisition receipt; they did not independently recompute the HTML-body or complete-text hash. No source was fetched again to improve this limitation.

## Implementation and executed checks

Independent review demonstrated an unused optional selector could accept a generic “Claude 4 usage policy version 2025” PDF. No candidate or optional request occurred in the actual cycle. The guarded selector now requires RSP/Responsible Scaling Policy identity, the scoped model, version/date evidence and an applicability relation; chronology-only links and Claude 4.5 are rejected. Automatic acquisition triggers were disabled in the same offline repair commit, preserving one actual source cycle. MIME/PDF-magic handling keeps the planned 8 MiB policy-PDF cap and 2 MiB HTML cap separate; the hard deadline uses an uncaught dedicated BaseException. Tests use synthetic PDFs and mocked responses, with no source requests.

Exact tested source `76b614e0a402ecef86a7fb7d1beea9b570e156bd` passed actual Node 22.23.3/Python 3.11.16 [CI 36957167508](https://github.com/trimcrae/Alignment/actions/runs/36957167508), job 110682594061, 02:46:26–02:46:33 UTC:

- **49 new Node checks (46 invalid) and 22 new Python tests** for native version/temporal inference, source-receipt integrity, selector identity, MIME/resource limits, annotation scope, reuse, robots/redirects and hard-stop behavior.
- **70 inherited Node checks (66 invalid) and 15 inherited Python tests** passed separately; these are inherited checks, not newly added cases.
- Syntax, immutable evidence/prior-ledger validation, exact gap summary and clean tracked status passed. No model-capability experiment was run.

Independent source/method/code review cleared the scoped result and repair. Independent V8 execution of the actual core/harness reproduced 49/46; actual Node/Python runs are the separate GitHub CI above. Root independently observed source/CI outcomes and original receipt/log hashes. Human review remains unperformed; model variant/reasoning effort, subscription usage and total session wall time were not exposed. No remaining scoped blocker or source/test job is pending.

[validation-receipt.json](validation-receipt.json) records exact commits, tested blob hashes, source/test receipts, review and limitations. Original harmless [acquisition log](acquisition-job-110680066600.log) and [offline CI log](offline-ci-job-110682594061.log) are preserved. The final documentation/receipt/log commit changes no tested code, collector, workflow, result or evidence bytes.

## Next distinct bounded task

A distinct provider-native ledger seed, preferably Google DeepMind, from one accessible official primary model/system card. Vet the exact source and native determination framework first; stop with explicit missing evidence if no supported determination exists. No cross-framework scale normalization, inference or outreach. Do not rerun the unchanged RSP route, card/PDF acquisition, gpt-oss timing cycle or ControlArena ancestry audit.
