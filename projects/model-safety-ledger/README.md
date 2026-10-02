# Model determination and release-artifact ledger

Produced by OpenAI Codex (AI agent, GPT-6) for the 2026-10-01 usage sprint. Human review has not been performed.

This bounded ledger implements research priorities 2 and 3 in [research/README.md](../../research/README.md): preserve provider-native dangerous-capability determinations with exact quotes and track what is known about release artifacts. It covers OpenAI's gpt-oss-120b and gpt-oss-20b, one shared model card and one related safety report. It is not a frontier-wide census.

The model card's PDF page 4 reports three default-model determinations and two adversarially fine-tuned determinations for **gpt-oss-120b**. The five corresponding gpt-oss-20b entries remain **unknown**: the shared title does not extend those statements to the smaller model. Unknown does not mean absent or unevaluated. The default and adversarial configurations remain separate, and the native High threshold is preserved without cross-framework scale normalization.

The related safety report explicitly says on PDF page 4 that it does not aim to make a final risk-level determination. It is an observed primary artifact, not another final determination. The model card names the Preparedness Framework; its version remains unknown in this snapshot.

## Evidence and dates

[ledger.json](ledger.json) binds every reported determination to its exact source hash, PDF page number and normalized verbatim quote. Page numbers are 1-based **PDF pages**, not inferred printed-page numbers. [evidence/primary-acquisition.json](evidence/primary-acquisition.json) contains selected cover and determination-page spans from the actual acquisition receipt; it openly records that it is an AI-selected subset, not the full log.

| Primary artifact | Received-byte SHA256 | PDF pages |
| --- | --- | --- |
| [Model card](https://arxiv.org/pdf/2508.10925) | `8839e1efdf835be08ad1d60bfa99c8c4fdde15c7ef49eda6a8b910575fb699a0` | 35 |
| [Safety report](https://cdn.openai.com/pdf/231bf018-659a-494d-976c-2efdfc72b652/oai_gpt-oss_Model_Safety.pdf) | `dbd97a15deaa6c37976ef809c10879213b39115c51b98f1cf645fd33129e66d7` | 16 |

The model card's August 5, 2025 cover date is a **declared document date**. It does not establish model-release timing or that these bytes were available at launch. Both models' release dates and model-card availability at release remain unknown. A historical official README link is a lead, not launch-byte evidence; a failed fetch cannot establish absence. Response headers and ETags are opaque metadata, and the receipt uses a digest computed over received PDF bytes.

The arXiv model-card record was confirmed in the official [openai/gpt-oss README](https://github.com/openai/gpt-oss/blob/7b583341fe16729127f6d5b94a7b09ccae97e1a1/README.md). The model-card PDF was acquired directly from arXiv. A mirror provided only a discovery lead for the safety-report URL; the accepted evidence was retrieved directly from the OpenAI CDN.

Actual acquisition: [run 36941633243](https://github.com/trimcrae/Alignment/actions/runs/36941633243), job 110634241560, acquisition source commit `5c4b06403ca34b565f10e4e8fd7737e84c9d4ff3`. Both PDFs were retrieved successfully after robots checks. The collector fixes source URLs, permits only same-host HTTPS redirects, caps bytes/pages, and has a 25-second request/socket timeout within a six-minute workflow-job limit. The socket timeout is not a total-document time budget.

## Read-only checks

Node 22 built-ins suffice; no package installation, network requests, credentials, model inference or data writes are needed:

```sh
node projects/model-safety-ledger/ledger-tool.mjs validate
node projects/model-safety-ledger/ledger-tool.mjs test
node projects/model-safety-ledger/ledger-tool.mjs summary
```

The dependency-free core checks strict status fields, complete declared model/configuration slots, evidence hashes and exact quote/page bindings, provider/model/domain/configuration scope, and explicit evidence for any reported release or availability claim. Regression cases reject accidental 120b-to-20b promotion, dropped negation, document-date-to-release promotion, unknown-to-absence promotion and unbound provenance.

Validation establishes internal consistency with the selected evidence; it does not independently replicate capability evaluations or establish that a provider's assessment is true. Lexical guards on claim quotations are structural checks, not a general semantic verifier. Labels distinguish primary-document observation from transcription of a provider statement. Human review remains `not_performed`.

## Continuation

Do not repeat acquisition of unchanged PDFs or the completed ControlArena ancestry audit. Use the committed hashes and acquisition receipt. A useful next bounded question is whether dated primary or archival evidence can establish genuine release timing and which model-card edition was publicly available then; keep present observation and launch availability separate. Expand providers only in a separately scoped task.
