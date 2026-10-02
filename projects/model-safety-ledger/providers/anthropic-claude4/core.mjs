// Produced by OpenAI Codex (AI agent, GPT-6). Human review not performed.
// This bounded seed preserves provider-native statements; it is not a universal ASL classifier.
const SOURCE = "https://www-cdn.anthropic.com/6d8a8055020700718b0c49369f60816ba2a7c285/Claude%204%20System%20Card.pdf";
const DOCUMENT = "5e3e63370473db1f1e499642ef8400250e19aba8cbb5f84f2b919cf2b27898cb";
const MODELS = ["anthropic-claude-opus-4","anthropic-claude-sonnet-4"];
const NAMES = ["Claude Opus 4","Claude Sonnet 4"];
const AXES = ["deployment_asl","capability_asl3","capability_asl4"];
const BINDINGS = [
  {
    "id": "opus-deployment",
    "model_id": "anthropic-claude-opus-4",
    "axis": "deployment_asl",
    "native_result": "ASL-3 Standard",
    "outcome": "ASL-3",
    "qualification": "provider_deployment_decision",
    "pdf_page": 10,
    "required_clause": "Based on these assessments, we have decided to release Claude Opus 4 under the ASL-3 Standard and Claude Sonnet 4 under the ASL-2 Standard."
  },
  {
    "id": "sonnet-deployment",
    "model_id": "anthropic-claude-sonnet-4",
    "axis": "deployment_asl",
    "native_result": "ASL-2 Standard",
    "outcome": "ASL-2",
    "qualification": "provider_deployment_decision",
    "pdf_page": 10,
    "required_clause": "Based on these assessments, we have decided to release Claude Opus 4 under the ASL-3 Standard and Claude Sonnet 4 under the ASL-2 Standard."
  },
  {
    "id": "opus-asl3",
    "model_id": "anthropic-claude-opus-4",
    "axis": "capability_asl3",
    "native_result": "cannot clearly rule out ASL-3 risks",
    "outcome": "not_ruled_out",
    "qualification": "precautionary_provisional_not_confirmed_passed",
    "pdf_page": 11,
    "required_clause": "To be clear, we have not yet determined whether Claude Opus 4 has deﬁnitively passed the capabilities threshold that requires ASL-3 protections. Rather, we cannot clearly rule out ASL-3 risks for Claude Opus 4 (although we have ruled out that it needs the ASL-4 Standard). Thus, we are deploying Claude Opus 4 with ASL-3 measures as a precautionary, provisional action, while maintaining Claude Sonnet 4 at the ASL-2 Standard."
  },
  {
    "id": "opus-asl4",
    "model_id": "anthropic-claude-opus-4",
    "axis": "capability_asl4",
    "native_result": "conﬁdently rule out ASL-4 capabilities",
    "outcome": "ruled_out",
    "qualification": "aggregate_native_assessment",
    "pdf_page": 88,
    "required_clause": "For Claude Opus 4, our evaluations showed that, whereas we could conﬁdently rule out ASL-4 capabilities, we could not conclusively rule out ASL-3 capabilities—which led to our precautionary decision to deploy it with ASL-3 protections."
  },
  {
    "id": "sonnet-asl3",
    "model_id": "anthropic-claude-sonnet-4",
    "axis": "capability_asl3",
    "native_result": "remained below the ASL-3 thresholds of concern",
    "outcome": "below_thresholds_of_concern",
    "qualification": "aggregate_native_assessment",
    "pdf_page": 11,
    "required_clause": "In contrast, Claude Sonnet 4 showed more modest improvements that—while noteworthy—remained below the ASL-3 thresholds of concern."
  }
];
const ensure = (ok,message) => { if (!ok) throw Error(message); };
const text = (v,label) => ensure(typeof v==="string" && v.trim().length>0,label+" must be nonempty text");
const sha = v => typeof v==="string" && /^[0-9a-f]{64}$/.test(v);
const obj = (v,label) => ensure(v!==null && typeof v==="object" && !Array.isArray(v),label+" must be object");
const array = (v,label) => ensure(Array.isArray(v),label+" must be array");
function keys(v,expected,label) {
  obj(v,label);
  ensure(Object.keys(v).sort().join("|")===expected.slice().sort().join("|"),label+" keys differ from bounded schema");
}
function utc(v,label) {
  ensure(typeof v==="string" && /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(v) && !Number.isNaN(Date.parse(v)),label+" must be UTC timestamp");
  ensure(new Date(v).toISOString().replace(".000Z","Z")===v,label+" must be real calendar timestamp");
  return Date.parse(v);
}
function host(v) {
  ensure(typeof v==="string","source URL must be text");
  const match=/^https:\/\/(www\.anthropic\.com|www-cdn\.anthropic\.com)(?::443)?\/[^\s#]*$/.exec(v);
  ensure(match,"source URL leaves provider HTTPS allowlist");
  return match[1];
}
function url(v) { host(v); }
function unknown(v,label,hasClaim=true) {
  keys(v,hasClaim?["status","claim_id","reason"]:["status","value","reason"],label);
  ensure(v.status==="unknown" && (hasClaim?v.claim_id:v.value)===null,label+" must remain explicitly unknown/null");
  text(v.reason,label+" reason");
}
export function summarize(l) {
  const ds=l.models.flatMap(m=>m.determinations);
  return {models:l.models.length,observed_system_cards:1,
    reported_deployment_decisions:ds.filter(d=>d.axis==="deployment_asl"&&d.status==="reported").length,
    reported_capability_assessments:ds.filter(d=>d.axis!=="deployment_asl"&&d.status==="reported").length,
    unknown_capability_assessments:ds.filter(d=>d.axis!=="deployment_asl"&&d.status==="unknown").length,
    unknown_release_dates:l.models.filter(m=>m.release_date.status==="unknown").length,
    unknown_launch_editions:l.models.filter(m=>m.artifact_at_release.status==="unknown").length,
    scope:"Provider-native statements only; no independent capability assessment, model inference or human review"};
}
export function validate(l,r,receiptDigest) {
  try {
    keys(l,["schema_version","authorship","snapshot_at","scope","evidence_receipt","artifact","framework","claims","models"],"ledger");
    ensure(l.schema_version===1,"unsupported schema");
    keys(l.authorship,["agent","model_family","session","human_review","base_commit"],"authorship");
    ensure(l.authorship.agent==="OpenAI Codex" && l.authorship.model_family==="GPT-6" && l.authorship.session==="usage-sprint-2026-10-01" && l.authorship.human_review==="not_performed","AI authorship/human review provenance mismatch");
    ensure(l.authorship.base_commit==="c79d38e9e49d9c2fd133b6c4faf6412760089afe","unpinned or changed base");
    const snapshot=utc(l.snapshot_at,"snapshot");
    keys(l.scope,["provider","model_ids","axes","coverage","comparison_policy"],"scope");
    ensure(l.scope.provider==="Anthropic" && JSON.stringify(l.scope.model_ids)===JSON.stringify(MODELS) && JSON.stringify(l.scope.axes)===JSON.stringify(AXES),"scope/model/native axes mismatch");
    text(l.scope.coverage,"coverage");text(l.scope.comparison_policy,"comparison policy");
    keys(l.evidence_receipt,["path","sha256","source_commit","run_id","job_id","run_url"],"receipt binding");
    ensure(l.evidence_receipt.path==="evidence/primary-acquisition.json" && sha(receiptDigest) && l.evidence_receipt.sha256===receiptDigest && receiptDigest==="434c2852efd69dcf1d3cfc562d9e46123745bbaa6307e50bcac1b6cb770ce953","selected receipt hash/path mismatch or immutable acquired subset changed");
    ensure(l.evidence_receipt.source_commit==="bda723fb2678787fc0ec6e52ad742d63b618ab5a" && l.evidence_receipt.run_id==="36951404278" && l.evidence_receipt.job_id==="110664941297" && l.evidence_receipt.run_url==="https://github.com/trimcrae/Alignment/actions/runs/36951404278","acquisition commit/run/job binding mismatch");
    ensure(r.schema_version===1 && r.authorship.agent===l.authorship.agent && r.authorship.human_review==="not_performed","receipt provenance mismatch");
    ensure(r.execution.source_commit===l.evidence_receipt.source_commit && r.execution.run_id===l.evidence_receipt.run_id && r.execution.job_name==="acquire","original receipt execution mismatch");
    ensure(utc(r.execution.collected_at,"collection")<=snapshot,"collection after snapshot");
    ensure(r.method.max_page_bytes===2*1024*1024 && r.method.max_pdf_bytes===20*1024*1024 && r.method.max_redirects===3,"bounded method mismatch");
    const subset=r.subset_provenance;
    ensure(subset.original_receipt_sha256==="d4ba9e969ac16bf45287f09bbd3287434cf8c97d584a163b4737c5d5af964189" && subset.original_receipt_utf8_bytes===49995 && subset.original_run_id===l.evidence_receipt.run_id && subset.original_job_id===l.evidence_receipt.job_id,"original subset provenance mismatch");
    text(subset.selection,"subset selection");
    ensure(r.selection.status==="observed" && JSON.stringify(r.selection.candidate_urls)===JSON.stringify([SOURCE]),"unique official document selection not observed");
    array(r.sources,"sources");ensure(r.sources.length===2 && r.sources[0].id==="claude-4-card-pointer" && r.sources[1].id==="claude-4-system-card","source cohort mismatch");
    for(const s of r.sources) {
      ensure(s.state==="observed" && s.sha256===DOCUMENT && s.bytes===4976826,"source state/hash/received-byte mismatch");
      ensure(utc(s.observed_at,"source observation")<=snapshot,"source observed after snapshot");
      url(s.requested_url);url(s.response.final_url);
      ensure(s.response.status===200 && s.response.final_url===SOURCE && s.response.content_type==="application/pdf","unsuccessful or wrong final PDF response");
      ensure(s.robots.allowed===true && [200,404,410].includes(s.robots.status),"source robots denial");
      array(s.response.redirect_chain,"redirect chain");ensure(s.response.redirect_chain.length>=1 && s.response.redirect_chain.length<=4,"unbounded redirect chain");
      for(let i=0;i<s.response.redirect_chain.length;i++) {
        const step=s.response.redirect_chain[i];url(step.url);
        ensure(step.robots.allowed===true && [200,404,410].includes(step.robots.status),"redirect robots denial");
        ensure(step.robots.url==="https://"+host(step.url)+"/robots.txt","robots host/path mismatch");
        if(step.robots.status===200) ensure(sha(step.robots.sha256),"robots body needs digest");
        if(i<s.response.redirect_chain.length-1) {
          ensure([301,302,303,307,308].includes(step.status) && step.location===s.response.redirect_chain[i+1].url,"redirect provenance discontinuity");url(step.location);
        } else ensure(step.url===SOURCE,"redirect chain does not terminate at observed PDF");
      }
    }
    const source=r.sources[1];
    ensure(r.sources[0].requested_url==="https://www.anthropic.com/claude-4-system-card" && source.requested_url===SOURCE && source.kind==="system_card" && source.pdf_pages===124,"official pointer/document identity mismatch");
    array(source.excerpts,"excerpts");const pages=new Map();
    for(const p of source.excerpts) {
      ensure(Number.isSafeInteger(p.pdf_page) && p.pdf_page>=1 && p.pdf_page<=124 && !pages.has(p.pdf_page),"invalid or duplicate selected PDF page");
      ensure(sha(p.normalized_page_text_sha256) && p.normalization==="Unicode whitespace collapsed to one ASCII space; stripped","page extraction metadata mismatch");
      array(p.spans,"spans");ensure(p.spans.length>0,"empty selected page");
      for(const span of p.spans) {text(span.text,"span text");ensure(Number.isSafeInteger(span.start_char)&&span.start_char>=0&&Number.isSafeInteger(span.end_char)&&span.end_char-span.start_char===Array.from(span.text).length,"invalid original span coordinates");}
      pages.set(p.pdf_page,p);
    }
    ensure(JSON.stringify([...pages.keys()])===JSON.stringify([1,3,9,10,11,88,117]),"selected governance page cohort changed");
    function citation(c,label) {
      keys(c,["artifact_id","document_sha256","pdf_page","quote"],label);
      ensure(c.artifact_id==="claude-4-system-card" && c.document_sha256===DOCUMENT,"citation artifact/hash mismatch");
      text(c.quote,label+" quote");
      ensure(pages.has(c.pdf_page) && pages.get(c.pdf_page).spans.some(s=>s.text.includes(c.quote)),label+" not verbatim on cited PDF page");
    }
    const a=l.artifact;
    keys(a,["id","publisher","kind","title","source_url","document_sha256","pdf_pages","observed_at","verification","identity","declared_month","edition"],"artifact");
    ensure(a.id==="claude-4-system-card"&&a.publisher==="Anthropic"&&a.kind==="system_card"&&a.title==="System Card: Claude Opus 4 & Claude Sonnet 4"&&a.source_url===SOURCE&&a.document_sha256===DOCUMENT&&a.pdf_pages===124&&a.observed_at===source.observed_at&&a.verification==="primary_document_observed","artifact metadata/source mismatch");
    citation(a.identity,"artifact identity");ensure(a.identity.pdf_page===1 && a.identity.quote.includes(a.title) && a.identity.quote.includes("anthropic.com"),"artifact publisher/title attribution");
    keys(a.declared_month,["status","value","citation"],"declared month");citation(a.declared_month.citation,"cover month");
    ensure(a.declared_month.status==="reported" && a.declared_month.value==="2025-05" && a.declared_month.citation.pdf_page===1 && a.declared_month.citation.quote.includes("May 2025"),"cover month is not source-backed");
    unknown(a.edition,"edition",false);
    const f=l.framework;
    keys(f,["id","provider","native_name","version","citation","cyber_formal_threshold"],"framework");
    ensure(f.id==="anthropic-rsp"&&f.provider==="Anthropic"&&f.native_name==="Responsible Scaling Policy (RSP)","native framework attribution");
    unknown(f.version,"framework version",false);citation(f.citation,"framework citation");
    ensure(f.citation.pdf_page===9 && f.citation.quote.includes(f.native_name),"native framework name not quoted");
    keys(f.cyber_formal_threshold,["status","native_statement","citation"],"cyber formal threshold");
    citation(f.cyber_formal_threshold.citation,"cyber formal threshold citation");
    const cyber="The RSP does not stipulate a formal threshold for cyber capabilities at any ASL level. Instead, we believe cyber requires ongoing assessment.";
    ensure(f.cyber_formal_threshold.status==="not_stipulated" && f.cyber_formal_threshold.native_statement===cyber && f.cyber_formal_threshold.citation.pdf_page===117 && f.cyber_formal_threshold.citation.quote===cyber,"formal cyber threshold cannot be invented or mapped to OpenAI scale");
    array(l.claims,"claims");ensure(l.claims.length===BINDINGS.length,"claim universe changed");
    const claims=new Map();
    for(const c of l.claims) {
      keys(c,["id","model_id","axis","native_result","outcome","qualification","citation","verification"],"claim");
      ensure(!claims.has(c.id),"duplicate claim");const b=BINDINGS.find(b=>b.id===c.id);ensure(b,"unknown claim");
      for(const k of ["model_id","axis","native_result","outcome","qualification"])ensure(c[k]===b[k],"model/native axis/outcome binding mismatch: "+k);
      ensure(c.verification==="provider_statement_transcribed","provider statement promoted to experimental validation");
      citation(c.citation,"claim citation");
      ensure(c.citation.pdf_page===b.pdf_page && c.citation.quote===b.required_clause,"claim must retain complete model-specific native qualification");
      claims.set(c.id,c);
    }
    array(l.models,"models");ensure(l.models.length===2,"model universe changed");
    const used=new Set();
    for(let i=0;i<l.models.length;i++) {
      const m=l.models[i];keys(m,["id","native_name","provider","identity","determinations","release_date","artifact_at_release"],"model");
      ensure(m.id===MODELS[i] && m.native_name===NAMES[i] && m.provider==="Anthropic","native model identity mismatch");
      citation(m.identity,"model identity");
      ensure(m.identity.pdf_page===3 && m.identity.quote.includes(m.native_name) && m.identity.quote.includes("Anthropic"),"model identity not explicitly in primary abstract");
      array(m.determinations,"determinations");ensure(m.determinations.length===AXES.length,"all native axes including unknowns required");
      for(let j=0;j<m.determinations.length;j++) {
        const d=m.determinations[j];keys(d,["axis","status","claim_id","reason"],"determination");
        ensure(d.axis===AXES[j],"native axis duplicate/missing/swapped");
        const c=[...claims.values()].find(c=>c.model_id===m.id&&c.axis===d.axis);
        if(c){ensure(d.status==="reported"&&d.claim_id===c.id&&d.reason===null,"reported native slot attribution mismatch");used.add(c.id);}
        else{ensure(d.status==="unknown"&&d.claim_id===null,"unknown not absent or unevaluated");text(d.reason,"unknown native slot reason");}
      }
      unknown(m.release_date,"release timing");unknown(m.artifact_at_release,"launch edition availability");
    }
    ensure(used.size===claims.size,"unreferenced claims outside coverage");
    return {valid:true,errors:[],counts:summarize(l)};
  }catch(e){return {valid:false,errors:[e instanceof Error?e.message:String(e)],counts:null};}
}
