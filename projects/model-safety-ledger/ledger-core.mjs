// Produced by OpenAI Codex (AI agent), usage-sprint-2026-10-01. Human review not performed.
// This validates evidence consistency, not the truth of a provider's capability assessment.
// This bounded OpenAI seed preserves the configuration-specific names in the model card.
// A new framework needs its own source-backed native-domain mapping.
const nativeDomainNames = {
  "openai-preparedness": {
    default: {
      biological_chemical: "Biological and Chemical capability",
      cyber: "Cyber capability",
      ai_self_improvement: "AI Self-Improvement",
    },
    adversarially_fine_tuned: {
      biological_chemical: "Biological and Chemical Risk",
      cyber: "Cyber risk",
    },
  },
};
const object = value => value !== null && typeof value === "object" && !Array.isArray(value);
const sha64 = value => typeof value === "string" && /^[a-f0-9]{64}$/.test(value);
const git40 = value => typeof value === "string" && /^[a-f0-9]{40}$/.test(value);
function need(condition, message) { if (!condition) throw Error(message); }
function text(value, label) { need(typeof value === "string" && value.trim().length > 0, label + " must be nonempty text"); }
function record(value, label) { need(object(value), label + " must be a record"); }
function array(value, label) { need(Array.isArray(value), label + " must be an array"); }
function keys(value, required, optional, label) {
  record(value, label);
  for (const key of required) need(Object.hasOwn(value, key), label + " missing " + key);
  for (const key of Object.keys(value)) need(required.includes(key) || optional.includes(key), label + " unexpected " + key);
}
function timestamp(value, label) {
  need(typeof value === "string" && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(value), label + " must be UTC seconds");
  const n = Date.parse(value);
  need(Number.isFinite(n) && new Date(n).toISOString().replace(".000Z", "Z") === value, label + " is not a real timestamp");
  return n;
}
function day(value, label) {
  need(typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value), label + " must be an ISO date");
  need(new Date(value + "T00:00:00Z").toISOString().slice(0, 10) === value, label + " is not a real date");
  return value;
}
function phraseDate(value) {
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return day(value, "date phrase");
  const match = /^(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}), (\d{4})$/.exec(value);
  need(match, "date phrase must explicitly state a full supported calendar date");
  const month = ["January","February","March","April","May","June","July","August","September","October","November","December"].indexOf(match[1]) + 1;
  return day(match[3] + "-" + String(month).padStart(2, "0") + "-" + match[2].padStart(2, "0"), "date phrase");
}
function index(records, label) {
  array(records, label); const map = new Map();
  for (const item of records) {
    record(item, label + " item"); text(item.id, label + " id");
    need(/^[a-z0-9][a-z0-9-]*$/.test(item.id), label + " id must be a canonical slug");
    need(!map.has(item.id), label + " duplicate id " + item.id); map.set(item.id, item);
  }
  return map;
}
function unique(values, label) {
  array(values, label); need(values.length > 0, label + " cannot be empty");
  need(new Set(values).size === values.length, label + " contains duplicates");
}
function hasModel(quote, name) { return quote.split(/[^A-Za-z0-9-]+/).includes(name); }
function slotKey(slot) { return slot.configuration + "/" + slot.domain; }

export function validateLedger(ledger, receipt, receiptSha256) {
  try {
    keys(ledger, ["schema_version","authorship","snapshot_at","evidence_receipt","scope","artifacts","frameworks","determination_claims","release_claims","availability_claims","models"], [], "ledger");
    need(ledger.schema_version === 1, "unsupported ledger schema");
    keys(ledger.authorship, ["agent","model_family","session","human_review","base_commit"], [], "authorship");
    text(ledger.authorship.agent, "AI agent"); text(ledger.authorship.model_family, "model family"); text(ledger.authorship.session, "session");
    need(ledger.authorship.human_review === "not_performed", "this AI-authored snapshot cannot claim human review");
    need(git40(ledger.authorship.base_commit), "base commit must be pinned");
    const snapshotTime = timestamp(ledger.snapshot_at, "snapshot_at");
    keys(ledger.evidence_receipt, ["path","sha256","source_commit","run_id","job_id","run_url"], [], "evidence receipt");
    need(ledger.evidence_receipt.path === "evidence/primary-acquisition.json", "receipt path must be the bounded local evidence file");
    need(sha64(receiptSha256) && receiptSha256 === ledger.evidence_receipt.sha256, "receipt bytes do not match committed SHA256");
    need(git40(ledger.evidence_receipt.source_commit), "acquisition source commit must be pinned");
    need(/^[1-9]\d*$/.test(ledger.evidence_receipt.run_id) && /^[1-9]\d*$/.test(ledger.evidence_receipt.job_id), "receipt needs numeric actual run/job IDs");
    need(ledger.evidence_receipt.run_url === "https://github.com/trimcrae/Alignment/actions/runs/" + ledger.evidence_receipt.run_id, "run URL/id mismatch");
    record(receipt, "receipt"); need(receipt.schema_version === 1, "unsupported acquisition receipt schema");
    record(receipt.execution, "execution");
    need(receipt.execution.source_commit === ledger.evidence_receipt.source_commit && receipt.execution.run_id === ledger.evidence_receipt.run_id, "receipt execution/ledger provenance mismatch");
    need(timestamp(receipt.execution.collected_at, "collection time") <= snapshotTime, "collection time is after snapshot");
    record(receipt.authorship, "receipt authorship");
    need(receipt.authorship.agent === ledger.authorship.agent && receipt.authorship.session === ledger.authorship.session && receipt.authorship.human_review === "not_performed", "receipt authorship mismatch");
    const sourceMap = index(receipt.sources, "receipt sources");
    const artifacts = index(ledger.artifacts, "artifacts");
    const frameworks = index(ledger.frameworks, "frameworks");
    const models = index(ledger.models, "models");
    const claims = index(ledger.determination_claims, "determination claims");
    const releases = index(ledger.release_claims, "release claims");
    const availability = index(ledger.availability_claims, "availability claims");
    keys(ledger.scope, ["model_ids","expected_determination_slots","coverage","comparison_policy"], [], "scope");
    unique(ledger.scope.model_ids, "scope model_ids"); text(ledger.scope.coverage, "coverage"); text(ledger.scope.comparison_policy, "comparison policy");
    need(ledger.scope.model_ids.length === models.size && ledger.scope.model_ids.every(id => models.has(id)), "model universe does not match scope");
    const expectedSlots = new Set();
    array(ledger.scope.expected_determination_slots, "expected slots");
    need(ledger.scope.expected_determination_slots.length > 0, "expected slots cannot be empty");
    for (const slot of ledger.scope.expected_determination_slots) {
      keys(slot, ["domain","configuration"], [], "expected slot");
      text(slot.domain, "domain"); need(["default","adversarially_fine_tuned"].includes(slot.configuration), "unsupported evaluated configuration");
      need(!expectedSlots.has(slotKey(slot)), "duplicate expected determination slot"); expectedSlots.add(slotKey(slot));
    }
    for (const source of sourceMap.values()) {
      text(source.requested_url, "source URL"); timestamp(source.observed_at, "source observation time");
      need(timestamp(source.observed_at, "source observation time") <= snapshotTime, "source observation is after snapshot");
      need(["observed","not_fetched"].includes(source.state), "unsupported source observation state");
      if (source.state !== "observed") { text(source.reason, "unfetched source reason"); continue; }
      need(/^https:\/\/(?:arxiv\.org|cdn\.openai\.com)\//.test(source.requested_url), "primary source host is outside this bounded snapshot");
      record(source.response, "source response"); record(source.robots, "robots observation");
      need(source.response.status === 200 && source.robots.allowed === true, "an observed primary source needs successful permitted acquisition");
      const host = source.requested_url.split("/")[2];
      need(typeof source.response.final_url === "string" && source.response.final_url.startsWith("https://" + host + "/"), "source final URL leaves allowed host");
      need(sha64(source.sha256), "computed document digest must be lowercase SHA256");
      need(Number.isSafeInteger(source.bytes) && source.bytes > 0 && source.bytes <= 16 * 1024 * 1024, "invalid document byte count");
      need(Number.isSafeInteger(source.pdf_pages) && source.pdf_pages >= 1 && source.pdf_pages <= 200, "invalid PDF page count");
      array(source.excerpts, "selected page excerpts"); const pages = new Set();
      for (const page of source.excerpts) {
        need(Number.isSafeInteger(page.pdf_page) && page.pdf_page >= 1 && page.pdf_page <= source.pdf_pages && !pages.has(page.pdf_page), "invalid or duplicate excerpt PDF page");
        pages.add(page.pdf_page); need(sha64(page.normalized_page_text_sha256), "page extraction needs its recorded digest");
        array(page.spans, "page spans");
        for (const span of page.spans) {
          text(span.text, "span text");
          need(Number.isSafeInteger(span.start_char) && span.start_char >= 0 && Number.isSafeInteger(span.end_char) && span.end_char - span.start_char === Array.from(span.text).length, "invalid mechanically extracted span coordinates");
        }
      }
    }
    function citation(value, label) {
      keys(value, ["artifact_id","document_sha256","pdf_page","quote"], [], label);
      const artifact = artifacts.get(value.artifact_id); need(artifact, label + " references missing artifact");
      const source = sourceMap.get(value.artifact_id);
      need(source && source.state === "observed", label + " cannot rely on an unobserved document");
      need(value.document_sha256 === artifact.document_sha256 && value.document_sha256 === source.sha256, label + " document hash mismatch");
      need(Number.isSafeInteger(value.pdf_page) && value.pdf_page >= 1 && value.pdf_page <= source.pdf_pages, label + " PDF page out of range");
      text(value.quote, label + " quote");
      const page = source.excerpts.find(p => p.pdf_page === value.pdf_page);
      need(page && page.spans.some(span => span.text.includes(value.quote)), label + " quote is not an exact substring of that PDF page excerpt");
      return artifact;
    }
    for (const artifact of artifacts.values()) {
      keys(artifact, ["id","publisher","kind","title","source_url","document_sha256","pdf_pages","observed_at","verification","document_date","publisher_citation"], [], "artifact");
      text(artifact.publisher, "artifact publisher"); text(artifact.title, "artifact title");
      citation(artifact.publisher_citation, "publisher citation");
      need(artifact.publisher_citation.artifact_id === artifact.id && hasModel(artifact.publisher_citation.quote, artifact.publisher), "publisher identity must be quoted from its own artifact");
      need(["model_card","safety_report"].includes(artifact.kind), "unsupported artifact kind");
      need(artifact.verification === "primary_document_observed", "artifact observation cannot claim experimental verification");
      const source = sourceMap.get(artifact.id); need(source && source.state === "observed", "observed artifact lacks observed source receipt");
      need(artifact.kind === source.kind && artifact.source_url === source.requested_url && artifact.document_sha256 === source.sha256 && artifact.pdf_pages === source.pdf_pages && artifact.observed_at === source.observed_at, "artifact differs from acquired source metadata");
      keys(artifact.document_date, ["status","value","date_phrase","citation"], ["reason"], "document date");
      if (artifact.document_date.status === "reported") {
        need(phraseDate(artifact.document_date.date_phrase) === day(artifact.document_date.value, "document date"), "document date/phrase mismatch");
        citation(artifact.document_date.citation, "document date citation");
        need(artifact.document_date.citation.artifact_id === artifact.id && artifact.document_date.citation.quote.includes(artifact.document_date.date_phrase), "document date must be quoted from its own artifact");
      } else {
        need(artifact.document_date.status === "unknown" && artifact.document_date.value === null && artifact.document_date.date_phrase === null && artifact.document_date.citation === null, "unknown document date must remain null");
        text(artifact.document_date.reason, "unknown document date reason");
      }
    }
    for (const framework of frameworks.values()) {
      keys(framework, ["id","provider","native_name","version","version_status","version_reason","citation"], [], "framework");
      text(framework.provider, "framework provider"); text(framework.native_name, "framework native name");
      need(framework.version_status === "unknown" && framework.version === null, "framework version has not been established in this bounded schema");
      text(framework.version_reason, "framework version reason");
      const source = citation(framework.citation, "framework citation");
      need(source.publisher === framework.provider && framework.citation.quote.includes(framework.native_name), "framework must retain exact native source name");
    }
    function scope(modelIds, cite, label) {
      unique(modelIds, label + " model scope");
      for (const id of modelIds) { const model = models.get(id); need(model && hasModel(cite.quote, model.native_name), label + " does not explicitly name scoped model " + id); }
    }
    for (const claim of claims.values()) {
      keys(claim, ["id","model_ids","framework_id","configuration","domains","native_threshold","native_result","verification","citation","native_outcome"], [], "determination claim");
      need(claim.verification === "provider_statement_transcribed", "determination must remain a provider statement, not independent capability verification");
      const artifact = citation(claim.citation, "determination citation"); scope(claim.model_ids, claim.citation, "determination");
      need(artifact.kind === "model_card", "this seed uses explicit model-card determinations, not supporting report comparisons");
      const framework = frameworks.get(claim.framework_id); need(framework && framework.provider === artifact.publisher, "determination framework/provider mismatch");
      need(claim.model_ids.every(id => models.get(id).provider === framework.provider), "cross-provider determination attribution");
      need(["default","adversarially_fine_tuned"].includes(claim.configuration), "unknown determination configuration");
      need(claim.configuration === "default" ? claim.citation.quote.includes("default model") : claim.citation.quote.includes("adversarially fine-tuned"), "evaluated configuration is not explicit in quoted statement");
      text(claim.native_threshold, "native threshold"); text(claim.native_result, "native result");
      need(claim.native_outcome === "not_reached" && claim.native_threshold === "High" && /\b(?:does|do|did) not reach\b/.test(claim.native_result), "this seed preserves an explicit not-reached High outcome including negation");
      need(claim.citation.quote.includes(claim.native_threshold) && claim.citation.quote.includes(claim.native_result), "native threshold/result must remain exact quoted text");
      array(claim.domains, "native domains"); need(claim.domains.length > 0, "determination has no native domains");
      const domains = new Set();
      for (const domain of claim.domains) {
        keys(domain, ["id","native_name"], [], "native domain"); text(domain.id, "native domain id"); text(domain.native_name, "native domain name");
        need(!domains.has(domain.id), "duplicate claim domain"); domains.add(domain.id);
        need(claim.citation.quote.includes(domain.native_name), "native domain name is not quoted");
        const nativeName = nativeDomainNames[claim.framework_id]?.[claim.configuration]?.[domain.id];
        need(nativeName !== undefined && domain.native_name === nativeName, "native domain ID/name mismatch for framework and configuration");
        need(expectedSlots.has(claim.configuration + "/" + domain.id), "claim includes an out-of-scope determination slot");
      }
    }
    for (const claim of releases.values()) {
      keys(claim, ["id","model_ids","date","date_phrase","verification","citation"], [], "release claim");
      need(claim.verification === "provider_statement_transcribed", "release claim verification label unsupported");
      citation(claim.citation, "release citation"); scope(claim.model_ids, claim.citation, "release");
      need(phraseDate(claim.date_phrase) === day(claim.date, "release date") && claim.citation.quote.includes(claim.date_phrase) && /\breleas(?:e|ed|ing)\b/i.test(claim.citation.quote), "a document date alone cannot establish model release timing");
      need(claim.date <= ledger.snapshot_at.slice(0, 10), "release date is after snapshot");
    }
    for (const claim of availability.values()) {
      keys(claim, ["id","model_ids","artifact_id","release_claim_id","status","native_statement","basis","verification","citation"], [], "availability claim");
      need(["present","absent"].includes(claim.status) && claim.basis === "explicit_publisher_statement" && claim.verification === "provider_statement_transcribed", "availability needs explicit dated publisher evidence; fetch outcomes and metadata are insufficient");
      const artifact = artifacts.get(claim.artifact_id), release = releases.get(claim.release_claim_id);
      need(artifact && release, "availability needs an artifact and established release claim");
      const statementArtifact = citation(claim.citation, "availability citation"); scope(claim.model_ids, claim.citation, "availability");
      need(statementArtifact.publisher === artifact.publisher && claim.model_ids.every(id => release.model_ids.includes(id)), "availability provider/model scope mismatch");
      text(claim.native_statement, "availability native statement");
      need(claim.citation.quote.includes(claim.native_statement) && claim.citation.quote.includes(release.date_phrase), "availability must state its release date and exact native assertion");
      need(/\b(card|report)\b/i.test(claim.native_statement), "availability assertion must name the artifact type");
      need(claim.status === "absent" ? /\b(no|without|absent|unavailable)\b/i.test(claim.native_statement) : /\b(available|published|released)\b/i.test(claim.native_statement) && !/\b(no|not|without|absent|unavailable)\b/i.test(claim.native_statement), "availability status lacks matching explicit native assertion");
    }
    const usedClaims = new Set(), usedReleases = new Set(), usedAvailability = new Set(), identities = new Set();
    for (const model of models.values()) {
      keys(model, ["id","provider","native_name","identity","release_date","release_artifacts","determinations"], [], "model");
      text(model.provider, "model provider"); text(model.native_name, "native model name");
      const identityKey = model.provider + "/" + model.native_name;
      need(!identities.has(identityKey), "duplicate provider/model identity"); identities.add(identityKey);
      const canonicalId = (model.provider + "-" + model.native_name).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
      need(model.id === canonicalId, "canonical model id does not match native provider/name");
      const identityArtifact = citation(model.identity, "model identity");
      need(identityArtifact.publisher === model.provider && hasModel(model.identity.quote, model.native_name), "identity must explicitly name the provider/model");
      keys(model.release_date, ["status","claim_id","reason"], [], "model release date");
      if (model.release_date.status === "unknown") {
        need(model.release_date.claim_id === null, "unknown release date cannot carry a determination"); text(model.release_date.reason, "unknown release date reason");
      } else {
        const release = releases.get(model.release_date.claim_id);
        need(model.release_date.status === "reported" && release && release.model_ids.includes(model.id) && model.release_date.reason === null, "model release date is not supported by matching release claim"); usedReleases.add(release.id);
      }
      array(model.release_artifacts, "model release artifacts"); need(model.release_artifacts.length > 0, "model needs at least one tracked release artifact");
      const artifactIds = new Set();
      for (const item of model.release_artifacts) {
        keys(item, ["artifact_id","current_status","at_release"], [], "model artifact");
        need(artifacts.has(item.artifact_id) && !artifactIds.has(item.artifact_id), "missing or duplicate model artifact"); artifactIds.add(item.artifact_id);
        need(item.current_status === "observed", "current model artifact state must match actual observed source");
        keys(item.at_release, ["status","claim_id","reason"], [], "release-time availability");
        if (item.at_release.status === "unknown") {
          need(item.at_release.claim_id === null, "unknown availability cannot carry a claim"); text(item.at_release.reason, "unknown availability reason");
        } else {
          const claim = availability.get(item.at_release.claim_id);
          need(claim && item.at_release.status === claim.status && item.at_release.reason === null && claim.model_ids.includes(model.id) && claim.artifact_id === item.artifact_id && model.release_date.status === "reported" && claim.release_claim_id === model.release_date.claim_id, "release-time present/absent status lacks matching historical publisher claim"); usedAvailability.add(claim.id);
        }
      }
      array(model.determinations, "model determinations"); const slots = new Set();
      for (const determination of model.determinations) {
        keys(determination, ["domain","configuration","status","claim_id","reason"], [], "model determination");
        const key = slotKey(determination);
        need(expectedSlots.has(key) && !slots.has(key), "missing-scope or duplicate model determination"); slots.add(key);
        if (determination.status === "unknown") {
          need(determination.claim_id === null, "unknown determination cannot carry a claim"); text(determination.reason, "unknown determination reason");
        } else {
          const claim = claims.get(determination.claim_id);
          need(determination.status === "reported" && claim && claim.model_ids.includes(model.id) && claim.configuration === determination.configuration && claim.domains.some(domain => domain.id === determination.domain) && determination.reason === null, "reported determination does not match model/configuration/domain claim"); usedClaims.add(claim.id);
        }
      }
      need(slots.size === expectedSlots.size, "every scoped determination slot must be represented, including unknowns");
    }
    need(usedClaims.size === claims.size && usedReleases.size === releases.size && usedAvailability.size === availability.size, "unreferenced claim hides outside model coverage");
    return {valid: true, errors: [], counts: summarizeLedger(ledger)};
  } catch (error) {
    return {valid: false, errors: [error instanceof Error ? error.message : String(error)], counts: null};
  }
}

export function summarizeLedger(ledger) {
  const determinations = ledger.models.flatMap(model => model.determinations);
  return {
    models: ledger.models.length,
    observed_artifacts: ledger.artifacts.length,
    provider_reported_determinations: determinations.filter(item => item.status === "reported").length,
    unknown_determinations: determinations.filter(item => item.status === "unknown").length,
    unknown_release_dates: ledger.models.filter(model => model.release_date.status === "unknown").length,
    unknown_release_artifact_states: ledger.models.flatMap(model => model.release_artifacts).filter(item => item.at_release.status === "unknown").length,
    evidence_scope: "Provider statements transcribed; no independent capability assessment or human review",
  };
}
