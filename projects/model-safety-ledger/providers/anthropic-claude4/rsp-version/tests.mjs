// Produced by OpenAI Codex (AI agent, GPT-6). Human review not performed.
import {validate,summarize} from "./core.mjs";
const clone=v=>JSON.parse(JSON.stringify(v));
const assert=(ok,m)=>{if(!ok)throw Error(m);};
export function runTests(seed,receiptText,digest,priorDigest){
 const initial=JSON.stringify(seed),r=JSON.parse(receiptText);let checks=0;
 assert(validate(seed,r,digest(receiptText),priorDigest).valid,"committed supplement");checks++;
 const count=summarize(seed);
 assert(count.historical_policy_applicability==="unknown"&&count.launch_policy_edition==="unknown"&&count.numeric_policy_version==="unknown"&&count.stop_condition==="met"&&count.new_card_source_requests===0&&count.official_route_requests===1&&count.optional_policy_pdf_requests===0,"actual finite-cycle gap summary");checks++;
 const cases=[
  ["date chronology promoted to governing version",s=>{s.historical_applicability={status:"reported",version:"v2",policy_document_sha256:null,claim_id:"announcement",reason:null};}],
  ["card pointer promoted to launch edition",s=>{s.launch_edition.status="present";}],
  ["unknown edition treated as absent",s=>{s.launch_edition.status="absent";}],
  ["unknown governing policy treated as not applicable",s=>{s.historical_applicability.status="not_applicable";}],
  ["numeric version inferred from update date",s=>{s.official_route_observation.numeric_policy_version={status:"reported",value:"2.0",reason:null};}],
  ["2026 footer promoted to governing edition",s=>{s.historical_applicability.version="2026";}],
  ["policy bytes inferred from HTML digest",s=>{s.historical_applicability.policy_document_sha256=s.official_route_observation.content_sha256;}],
  ["dated article promoted to policy document",s=>{s.official_route_observation.kind="versioned_policy";}],
  ["current page observation promoted to archived bytes",s=>{s.official_route_observation.verification="archived_2024_bytes_verified";}],
  ["collector HTML hash promoted to independent hash",s=>{s.official_route_observation.hash_verification="independently_recomputed";}],
  ["receipt extraction promoted to independent HTML transcript",s=>{s.official_route_observation.extraction_verification="independent_full_html_verified";}],
  ["announcement date promoted to actual effective date",s=>{s.official_route_observation.declared_update_date.status="effective";}],
  ["wrong reported article date",s=>{s.official_route_observation.declared_update_date.value="2025-05-22";}],
  ["native date phrase replaced",s=>{s.official_route_observation.declared_update_date.date_phrase="May 2025";}],
  ["quote paraphrased",s=>{s.official_route_observation.declared_update_date.citation.quote+=" It applies to Claude4."; }],
  ["wrong source-body quote hash",s=>{s.official_route_observation.declared_update_date.citation.content_sha256="f".repeat(64);}],
  ["wrong source observation URL",s=>{s.official_route_observation.source_url="https://example.org/policy";}],
  ["received-card relation promoted to historical binding",s=>{s.received_card_reference.relation="governing_policy_version";}],
  ["card annotation page changed",s=>{s.received_card_reference.pdf_page=10;}],
  ["card rectangle shifted",s=>{s.received_card_reference.annotation_rectangle[0]++;}],
  ["card URI rewritten to current policy",s=>{s.received_card_reference.uri="https://www.anthropic.com/responsible-scaling-policy";}],
  ["reused card hash replaced",s=>{s.received_card_reference.document_sha256="f".repeat(64);}],
  ["new card GET fabricated",s=>{s.completion.new_card_source_requests=1;}],
  ["optional policy PDF GET fabricated",s=>{s.completion.optional_policy_pdf_requests=1;}],
  ["extra source route fabricated",s=>{s.completion.official_route_requests=2;}],
  ["stop condition reopened",s=>{s.completion.stop_condition="pending";}],
  ["gap falsely called resolved",s=>{s.completion.status="verified_policy_edition";}],
  ["unknown reason removed",s=>{s.historical_applicability.reason="";}],
  ["unknown version carries claim",s=>{s.historical_applicability.claim_id="date-inferred";}],
  ["prior dated snapshot promoted",s=>{s.prior_snapshot.framework_version_status="reported";}],
  ["prior hash changed",s=>{s.prior_snapshot.sha256="f".repeat(64);}],
  ["receipt path offscope",s=>{s.evidence_receipt.path="../private.json";}],
  ["source revision unpinned",s=>{s.evidence_receipt.source_commit="main";}],
  ["actual source run replaced",s=>{s.evidence_receipt.run_id="1";}],
  ["actual source job replaced",s=>{s.evidence_receipt.job_id="1";}],
  ["AI/human review inflated",s=>{s.authorship.human_review="performed";}],
  ["base unpinned",s=>{s.authorship.base_commit="main";}],
  ["unsupported extra scientific verdict",s=>{s.current_model_safety_verdict="all ASL2";}],
  ["impossible date",s=>{s.snapshot_at="2026-02-31T00:00:00Z";}],
  ["rebinding forged original card coordinates",(_s,r)=>{r.reused_card.pointers[0].annotation_rectangle[0]++;},true],
  ["rebinding forged source body digest",(_s,r)=>{r.sources[0].sha256="f".repeat(64);},true],
  ["rebinding source quote text",(_s,r)=>{r.sources[0].spans[0].text+=" governing v2.0";r.sources[0].spans[0].end_char+=15;},true],
  ["rebinding extra source cohort",(_s,r)=>{r.sources.push(clone(r.sources[0]));},true],
  ["rebinding denied robots",(_s,r)=>{r.sources[0].robots.allowed=false;},true],
  ["rebinding source time as publication time",(_s,r)=>{r.sources[0].observed_at="2024-10-15T00:00:00Z";},true],
  ["rebinding collector human review",(_s,r)=>{r.authorship.human_review="performed";},true]
 ];
 for(const[name,mutate,rebind]of cases){
  const s=clone(seed),r=JSON.parse(receiptText);mutate(s,r);const hash=rebind?digest(JSON.stringify(r)):digest(receiptText);
  if(rebind)s.evidence_receipt.sha256=hash;
  assert(!validate(s,r,hash,priorDigest).valid,"invalid case accepted: "+name);checks++;
 }
 assert(JSON.stringify(seed)===initial,"validation/tests mutate input");checks++;
 return {checks,invalid_cases:cases.length,actual_summary:count};
}
