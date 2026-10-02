# RSP version supplement, 2026-10-02

Produced by OpenAI Codex (AI agent, GPT-6). Human review not performed.

The single bounded cycle preserved a useful negative result: the reused May 2025 Claude 4 card has an RSP annotation on PDF page 9 pointing to Anthropic's October 15, 2024 policy-update announcement. That official page was observed now. It does not identify immutable policy-edition bytes or an explicit numeric version governing the May 2025 card. Historical applicability, numeric policy version and launch-edition identity therefore remain **unknown**. Unknown does not mean absent or not applicable.

This is a dated supplement to [the earlier Anthropic snapshot](../README.md); its ledger, source receipts, model-specific ASL decisions and unknown version fields remain unchanged. The announcement's date is provider-declared article metadata, not independently verified 2024 public visibility or archived 2024 bytes. Its historical “At present, all of our models operate under ASL-2 Standards” statement cannot override the acquired 2025 card or describe current 2026 model state. The page's 2026 footer also cannot select a policy edition.

The actual [source cycle 36956360948](https://github.com/trimcrae/Alignment/actions/runs/36956360948), job 110680066600 at source`ffcc6faa08df990f303add33a518843faa831f4f`, reused owned artifact 11204066868 and verified its original PDF hash before inspecting only pages 9/10 annotations. It made one official announcement-route request and no fresh external card request or optional policy-PDF request. The immutable [original receipt](evidence/acquisition.json) is 10,671 UTF-8 bytes, SHA256`4b3363dcd44fe0469ff3415874d0f493beafd6f2eb9e1770022e786460767ca9`. Source-body and complete normalized-text hashes are collector-computed from the received response; raw HTML was not retained, so reviewers independently matched selected spans to the original receipt and did not independently recompute a raw HTML digest. No source was fetched again to improve that limitation.

The initial workflow 36956229264 failed before any job because our YAML referenced the runner context at job-env level. The narrow correction moved it into supported step contexts. This was an implementation configuration defect, not an inaccessible source or policy gap. Separately, independent review demonstrated that an unused optional selector could accept a generic usage-policy PDF. The offline repair now requires explicit RSP/Responsible Scaling Policy identity, model/version evidence and an applicability relation; meaningful regressions reject the counterexample and chronology-only links. This was not exercised by the actual acquired route, which had zero policy-PDF candidates. Automatic acquisition triggers are disabled after the one-cycle stop; no second source cycle accompanied the selector repair.

Run offline checks:

```sh
node projects/model-safety-ledger/providers/anthropic-claude4/rsp-version/tool.mjs validate
node projects/model-safety-ledger/providers/anthropic-claude4/rsp-version/tool.mjs test
python3 -m pip install pypdf==6.0.0
python3 projects/model-safety-ledger/providers/anthropic-claude4/rsp-version/test_collect.py
node projects/model-safety-ledger/providers/anthropic-claude4/rsp-version/tool.mjs summary
```

Tests use synthetic PDFs and mocked responses; they make no source requests. The validator binds the immutable receipt and unchanged prior ledger and rejects article-date-to-version, pointer-to-launch, current-to-historical, source-hash verification and absence-state inflation. See HANDOFF.md and validation-receipt.json for actual executed checks and exact commits. No model inference/API, outreach, upstream PR/issue or main merge occurred. The one-cycle stop is complete; do not dispatch unchanged acquisition or retry these sources.
