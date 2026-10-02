// Produced by OpenAI Codex (AI agent), usage-sprint-2026-10-01. Human review not performed.
import { createHash } from "node:crypto";
import { validateLedger, summarizeLedger } from "./ledger-core.mjs";

const clone = value => JSON.parse(JSON.stringify(value));
const digest = value => createHash("sha256").update(value, "utf8").digest("hex");
function assert(condition, message) { if (!condition) throw Error(message); }

export function runLedgerTests(seed, receiptText) {
  const original = JSON.stringify(seed), originalReceipt = receiptText;
  const valid = validateLedger(seed, JSON.parse(receiptText), digest(receiptText));
  assert(valid.valid, "committed seed must validate: " + valid.errors.join("; "));
  assert(valid.counts.models === 2 && valid.counts.observed_artifacts === 2 &&
    valid.counts.provider_reported_determinations === 5 && valid.counts.unknown_determinations === 5 &&
    valid.counts.unknown_release_dates === 2 && valid.counts.unknown_release_artifact_states === 2,
    "actual seed coverage and unknowns must remain visible");
  const cases = [
    ["default native domain names swapped", l => {
      const domains = l.determination_claims[0].domains;
      [domains[0].native_name, domains[1].native_name] = [domains[1].native_name, domains[0].native_name];
    }],
    ["biological domain relabeled AI self-improvement", l => { l.determination_claims[0].domains[0].native_name = "AI Self-Improvement"; }],
    ["biological domain relabeled quoted Cyber substring", l => { l.determination_claims[0].domains[0].native_name = "Cyber"; }],
    ["adversarial native domain names swapped", l => {
      const domains = l.determination_claims[1].domains;
      [domains[0].native_name, domains[1].native_name] = [domains[1].native_name, domains[0].native_name];
    }],
    ["schema version", l => { l.schema_version = 2; }],
    ["unexpected ledger key", l => { l.release_ready = true; }],
    ["human review inflation", l => { l.authorship.human_review = "performed"; }],
    ["unpinned base", l => { l.authorship.base_commit = "main"; }],
    ["wrong receipt path", l => { l.evidence_receipt.path = "../private.json"; }],
    ["wrong receipt digest", l => { l.evidence_receipt.sha256 = "0".repeat(64); }],
    ["unpinned collector", l => { l.evidence_receipt.source_commit = "main"; }],
    ["run mismatch", l => { l.evidence_receipt.run_id = "1"; l.evidence_receipt.run_url = "https://github.com/trimcrae/Alignment/actions/runs/1"; }],
    ["job nonnumeric", l => { l.evidence_receipt.job_id = "acquire"; }],
    ["run URL mismatch", l => { l.evidence_receipt.run_url += "?other=1"; }],
    ["non-UTC observation", l => { l.snapshot_at = "2026-10-01"; }],
    ["impossible observation", l => { l.snapshot_at = "2026-02-31T00:00:00Z"; }],
    ["future source observation", (l,r) => { r.sources[0].observed_at = "2027-01-01T00:00:00Z"; }, true],
    ["execution provenance mismatch", (l,r) => { r.execution.source_commit = "f".repeat(40); }, true],
    ["collector human review inflation", (l,r) => { r.authorship.human_review = "performed"; }, true],
    ["duplicate source", (l,r) => { r.sources.push(clone(r.sources[0])); }, true],
    ["failed fetch is not observed artifact", (l,r) => { r.sources[0].state = "not_fetched"; r.sources[0].reason = "HTTP 403"; }, true],
    ["HTTP error is not primary observation", (l,r) => { r.sources[0].response.status = 404; }, true],
    ["robots denial", (l,r) => { r.sources[0].robots.allowed = false; }, true],
    ["off-host redirect", (l,r) => { r.sources[0].response.final_url = "https://example.com/card.pdf"; }, true],
    ["source digest malformed", (l,r) => { r.sources[0].sha256 = "UPPER"; }, true],
    ["zero PDF size", (l,r) => { r.sources[0].bytes = 0; }, true],
    ["unbounded PDF size", (l,r) => { r.sources[0].bytes = 17 * 1024 * 1024; }, true],
    ["zero PDF pages", (l,r) => { r.sources[0].pdf_pages = 0; }, true],
    ["duplicate excerpt page", (l,r) => { r.sources[0].excerpts.push(clone(r.sources[0].excerpts[0])); }, true],
    ["invalid span coordinates", (l,r) => { r.sources[0].excerpts[0].spans[0].end_char++; }, true],
    ["receipt phrase tamper", (l,r) => { const span=r.sources[0].excerpts[1].spans[0]; span.text=span.text.replaceAll("High","Low "); }, true],
    ["duplicate artifact", l => { l.artifacts.push(clone(l.artifacts[0])); }],
    ["artifact hash substitution", l => { l.artifacts[0].document_sha256 = "f".repeat(64); }],
    ["artifact URL substitution", l => { l.artifacts[0].source_url = "https://example.com/card.pdf"; }],
    ["independent verification inflation", l => { l.artifacts[0].verification = "independently_evaluated"; }],
    ["publisher attribution inflation", l => { l.artifacts[0].publisher = "AnotherLab"; }],
    ["wrong declared document date", l => { l.artifacts[0].document_date.value = "2025-08-06"; }],
    ["unknown document date populated", l => { l.artifacts[1].document_date.value = "2025-08-05"; }],
    ["framework version inferred from date", l => { l.frameworks[0].version = "v2"; l.frameworks[0].version_status = "reported"; }],
    ["framework native name rewritten", l => { l.frameworks[0].native_name = "Universal Risk Framework"; }],
    ["duplicate model", l => { l.models.push(clone(l.models[0])); }],
    ["scoped model omitted", l => { l.models.pop(); }],
    ["20b relabeled 120b", l => { l.models[1].native_name = "gpt-oss-120b"; }],
    ["model canonical id/name mismatch", l => { l.models[1].id = "openai-gpt-oss-21b"; l.scope.model_ids[1] = l.models[1].id; }],
    ["identity page changed", l => { l.models[1].identity.pdf_page = 4; }],
    ["identity name missing", l => { l.models[1].identity.quote = "OpenAI August 5, 2025"; }],
    ["duplicate claim", l => { l.determination_claims.push(clone(l.determination_claims[0])); }],
    ["claim scope promoted to 20b", l => { l.determination_claims[0].model_ids.push(l.models[1].id); }],
    ["empty claim scope", l => { l.determination_claims[0].model_ids = []; }],
    ["claim configuration rewritten", l => { l.determination_claims[0].configuration = "adversarially_fine_tuned"; }],
    ["native domain normalized away", l => { l.determination_claims[0].domains[0].native_name = "CBRN safe"; }],
    ["native threshold case changed", l => { l.determination_claims[0].native_threshold = "high"; }],
    ["negation dropped", l => { l.determination_claims[0].native_result = "reach our indicative thresholds for High capability"; }],
    ["outcome inverted", l => { l.determination_claims[0].native_outcome = "reached"; }],
    ["provider statement promoted to experiment", l => { l.determination_claims[0].verification = "independent_experimental_validation"; }],
    ["quote paraphrased", l => { l.determination_claims[0].citation.quote += " Therefore the model is safe."; }],
    ["quote hash wrong", l => { l.determination_claims[0].citation.document_sha256 = "f".repeat(64); }],
    ["zero citation page", l => { l.determination_claims[0].citation.pdf_page = 0; }],
    ["out of range citation page", l => { l.determination_claims[0].citation.pdf_page = 36; }],
    ["wrong quote page", l => { l.determination_claims[0].citation.pdf_page = 1; }],
    ["unknown entry with claimed result", l => { l.models[1].determinations[0].claim_id = l.determination_claims[0].id; }],
    ["120b result copied into 20b row", l => { Object.assign(l.models[1].determinations[0], {status:"reported",claim_id:l.determination_claims[0].id,reason:null}); }],
    ["unknown treated as absent", l => { l.models[1].determinations[0].status = "absent"; }],
    ["unknown treated as not evaluated", l => { l.models[1].determinations[0].status = "not_evaluated"; }],
    ["unknown reason removed", l => { l.models[1].determinations[0].reason = ""; }],
    ["reported missing claim", l => { l.models[0].determinations[0].claim_id = null; }],
    ["reported wrong configuration claim", l => { l.models[0].determinations[0].claim_id = l.determination_claims[1].id; }],
    ["determination omitted", l => { l.models[1].determinations.pop(); }],
    ["determination duplicated", l => { l.models[1].determinations.push(clone(l.models[1].determinations[0])); }],
    ["expected unknown slot omitted", l => { l.scope.expected_determination_slots.pop(); }],
    ["unreferenced claim", l => { const extra=clone(l.determination_claims[0]);extra.id="unused";l.determination_claims.push(extra); }],
    ["unknown release date carries claim", l => { l.models[0].release_date.claim_id = "inferred"; }],
    ["card date promoted to release timing", l => {
      const identity=l.models[0].identity;
      l.release_claims=[{id:"card-date-release",model_ids:[l.models[0].id],date:"2025-08-05",date_phrase:"August 5, 2025",verification:"provider_statement_transcribed",citation:clone(identity)}];
      l.models[0].release_date={status:"reported",claim_id:"card-date-release",reason:null};
    }],
    ["current artifact promoted to launch-present", l => { Object.assign(l.models[0].release_artifacts[0].at_release,{status:"present",reason:null}); }],
    ["current artifact promoted to launch-absent", l => { Object.assign(l.models[0].release_artifacts[0].at_release,{status:"absent",reason:null}); }],
    ["unreadable source promoted to launch-absence", (l,r) => {
      r.sources[0].state="not_fetched";r.sources[0].reason="robots denied";
      l.models[0].release_artifacts[0].at_release={status:"absent",claim_id:null,reason:null};
    }, true],
    ["unknown availability reason removed", l => { l.models[0].release_artifacts[0].at_release.reason = ""; }],
    ["current status disagrees with observation", l => { l.models[0].release_artifacts[0].current_status = "absent"; }],
    ["duplicate tracked artifact", l => { l.models[0].release_artifacts.push(clone(l.models[0].release_artifacts[0])); }],
    ["boolean replaces unknown record", l => { l.models[0].release_date = false; }],
  ];
  for (const [name, mutate, rebindReceipt] of cases) {
    const ledger = clone(seed), receipt = JSON.parse(receiptText);
    mutate(ledger, receipt);
    const raw = JSON.stringify(receipt, null, 2) + "\n", hash = digest(raw);
    if (rebindReceipt) ledger.evidence_receipt.sha256 = hash;
    const result = validateLedger(ledger, receipt, hash);
    assert(!result.valid, name + " unexpectedly passed");
  }
  // A source's HTTP ETag is opaque metadata, not the computed received-byte digest.
  const ledger = clone(seed), receipt = JSON.parse(receiptText);
  receipt.sources[0].response.etag = '"sha256:' + "f".repeat(64) + '"';
  const raw = JSON.stringify(receipt, null, 2) + "\n";
  ledger.evidence_receipt.sha256 = digest(raw);
  assert(validateLedger(ledger, receipt, digest(raw)).valid, "an opaque unequal ETag must not replace the computed PDF SHA256");
  assert(JSON.stringify(seed) === original && receiptText === originalReceipt, "validation/tests must not mutate the input snapshot");
  assert(summarizeLedger(seed).unknown_determinations === 5, "unknown coverage cannot disappear from summary");
  return {passed: cases.length + 4, invalid_cases: cases.length, evidence: "Offline consistency checks only; no model inference or human review"};
}
