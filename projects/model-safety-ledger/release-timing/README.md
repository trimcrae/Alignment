# gpt-oss release timing: bounded evidence result

Produced by OpenAI Codex (AI agent, GPT-6). Human review has not been performed. This supplement preserves the prior two-model determination ledger at `baec2cd33fd25b14127656063a097f64d8ff079e` without promoting its unknown release fields.

**Actual model release timing and the model-card edition publicly available at launch remain unverified in this bounded collection.** The result records useful dated primary metadata and the exact acquisition failures, rather than treating a missing response as artifact absence.

| Evidence | Established result | Limit |
| --- | --- | --- |
| Official initial repository README, commit `243a1b02767da73bd2e3975be250afa801635866` | Commit author and committer metadata are August 5, 2025, 15:19:49 UTC. Its raw README says “We're releasing two flavors of the open models:” and links both variants and the official model-card landing URL. | Git metadata is not an independently measured public-repository visibility time or a precise model-weight release timestamp. The landing URL does not bind document bytes. |
| Current arXiv abstract record | The acquired submission history reports `[v1] Fri, 8 Aug 2025 19:24:38 UTC (2,197 KB)`. | Submission history is repository metadata. It is not model release timing or the first public availability time of an OpenAI-hosted card. |
| Prior received model-card PDF | Its already preserved cover span identifies `arXiv:2508.10925v1 [cs.CL] 8 Aug 2025`, alongside its declared August 5 cover date. | This identifies the previously received PDF's self-declared version. It does not establish which provider-hosted edition was available on August 5. |
| Official launch announcement and model-card landing | Both requests returned HTTP 403 after successful, permitting robots checks. | Neither date nor historical availability was established by these failures. |
| One launch-window archival index query | The bounded CDX request returned HTTP 503. | No capture index or replayed bytes were acquired; absence is not inferred. |

The original model-card received-byte SHA256 remains `8839e1efdf835be08ad1d60bfa99c8c4fdde15c7ef49eda6a8b910575fb699a0`. The inherited [selected primary receipt](../evidence/primary-acquisition.json) preserves its page-1 version marker. No PDF was downloaded again.

## Provenance and reproducibility

[evidence.json](evidence.json) separates repository submission metadata, Git commit metadata, a historical committed pointer, actual release timing and launch-edition byte availability. [evidence/acquisition.json](evidence/acquisition.json) is the complete JSON receipt emitted by actual metadata acquisition [run 36946343048](https://github.com/trimcrae/Alignment/actions/runs/36946343048), job 110649236702, source `1323221b9ed718c7bc8c8fa35673bb64c7a75305`. It was collected October 2, 2026, at 00:30:47 UTC; current observation is not historical availability.

The arXiv HTML response contained 61,234 received bytes, SHA256 `6b543ce8edf95fd2c2644ba33f535f62d808fe07a4ce195d50ed583f1e1f4088`. Only selected normalized visible-text spans and separate HTML metadata are preserved in the receipt; the complete received HTML is not committed. Hashes identify received bytes, not independently reproduced historical content.

[evidence/initial-readme.md](evidence/initial-readme.md) is an unmodified copy of provider-authored source, not AI-authored prose. Its Git blob SHA1 is `b8e85385f25c9a6f16c5e8e9d5d1fec69adafd99`; the offline tool recomputes that hash from the preserved UTF-8 bytes. [evidence/github-initial-commit.json](evidence/github-initial-commit.json) preserves the connector-returned GitHub commit JSON, reserialized as UTF-8 JSON, including tree, parent, author/committer and signature metadata. GitHub reports verification at 15:20:35 UTC on August 5; this is signature metadata, not a model release timestamp.

The collector permits only fixed HTTPS hosts, three same-host redirects, robots-approved paths and 3 MiB per source. Socket timeout is 12 seconds; elapsed request/cycle checks are 25/150 seconds. A blocking read can overshoot an elapsed check before its socket timeout; the workflow has a four-minute job limit. It performs one finite cycle, preserves failures and does not use browser challenges, authentication workarounds, alternate archives or retries.

Offline commands use Node 22 built-ins:

```sh
node projects/model-safety-ledger/release-timing/tool.mjs validate
node projects/model-safety-ledger/release-timing/tool.mjs test
node projects/model-safety-ledger/release-timing/tool.mjs hashes
```

The validator binds exact selected quotes, hashes, native date roles, model scope and failed-attempt records. Regression cases reject document-date/submission-date promotion, Git-time promotion, pointer-to-byte promotion, unknown-to-absence promotion and unbound source metadata. These checks verify evidence consistency, not the truth of every provider statement.

The stop condition was reached after one acquisition cycle. Future work should use a separately scoped, accessible archival source if it can bind actual launch-time model-card bytes; otherwise preserve this gap and choose another provider as a bounded task. Do not repeat these unchanged PDF or ancestry checks.
