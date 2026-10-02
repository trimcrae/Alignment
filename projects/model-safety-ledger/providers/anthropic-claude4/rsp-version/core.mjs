// Produced by OpenAI Codex (AI agent, GPT-6). Human review not performed.
// Bounded immutable source supplement: a dated announcement is not a governing policy edition.
const RECEIPT="4b3363dcd44fe0469ff3415874d0f493beafd6f2eb9e1770022e786460767ca9";
const PRIOR="8ac146cdd706421dc84d5ca5fafef70439030be48278665ac3cb454c108a3151";
const CARD="5e3e63370473db1f1e499642ef8400250e19aba8cbb5f84f2b919cf2b27898cb";
const URI="https://www.anthropic.com/news/announcing-our-updated-responsible-scaling-policy";
const BODY="8c454b6a7c24806d4ee8795eb76ea63bfaad67cfafe8350aaf2f922c8fb802ac";
const TEXT="40a4c7295d624fa9ca2be16f4ddb17bd09ee748521bc5189b784fb80625be192";
const RECT=[352.1366,623.1524,486.19763,637.23242];
const DATE_QUOTE="Announcing our updated Responsible Scaling Policy Oct 15, 2024 Read the Responsible Scaling Policy Today we are publishing a significant update to our Responsible Scaling Policy (RSP), the risk governance framework we use to mitigate potential catastrophic risks from frontier AI systems.";
const need=(ok,msg)=>{if(!ok)throw Error(msg);};
function keys(v,k,label){need(v!==null&&typeof v==="object"&&!Array.isArray(v),label+" must be object");need(Object.keys(v).sort().join("|")===k.slice().sort().join("|"),label+" keys differ from bounded schema");}
function text(v,label){need(typeof v==="string"&&v.trim().length>0,label+" requires text");}
function unknown(v,k,label){keys(v,["status",...k,"reason"],label);need(v.status==="unknown"&&k.every(k=>v[k]===null),label+" must remain unknown/null; no date or pointer inference");text(v.reason,label+" reason");}
function utc(v,label){need(typeof v==="string"&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(v)&&!Number.isNaN(Date.parse(v))&&new Date(v).toISOString().replace(".000Z","Z")===v,label+" needs real UTC time");return Date.parse(v);}
export function summarize(v){return {received_card_pointer:"observed",official_route:"dated_2024_update_announcement_observed_2026",numeric_policy_version:"unknown",historical_policy_applicability:"unknown",launch_policy_edition:"unknown",stop_condition:v.completion.stop_condition,new_card_source_requests:0,official_route_requests:1,optional_policy_pdf_requests:0,scope:"Provider page/date as observed; no archived2024-byte proof, independent HTML digest verification or historical policy edition inferred"};}
export function validate(v,r,receiptDigest,priorDigest){
 try{
  keys(v,["schema_version","authorship","snapshot_at","prior_snapshot","evidence_receipt","received_card_reference","official_route_observation","historical_applicability","launch_edition","completion"],"supplement");
  need(v.schema_version===1,"schema version");
  keys(v.authorship,["agent","model_family","session","human_review","base_commit"],"authorship");
  need(v.authorship.agent==="OpenAI Codex"&&v.authorship.model_family==="GPT-6"&&v.authorship.session==="usage-sprint-2026-10-01"&&v.authorship.human_review==="not_performed"&&v.authorship.base_commit==="4bff2e760c6e3297b96bf130b756dc43d36ce1d3","AI/base/review provenance");
  const time=utc(v.snapshot_at,"snapshot");
  keys(v.prior_snapshot,["path","sha256","framework_version_status"],"prior snapshot");
  need(v.prior_snapshot.path==="../ledger.json"&&v.prior_snapshot.sha256===PRIOR&&priorDigest===PRIOR&&v.prior_snapshot.framework_version_status==="unknown","prior snapshot changed or version promoted");
  keys(v.evidence_receipt,["path","sha256","source_commit","run_id","job_id","run_url"],"receipt");
  need(v.evidence_receipt.path==="evidence/acquisition.json"&&v.evidence_receipt.sha256===RECEIPT&&receiptDigest===RECEIPT,"immutable original acquisition receipt changed");
  need(v.evidence_receipt.source_commit==="ffcc6faa08df990f303add33a518843faa831f4f"&&v.evidence_receipt.run_id==="36956360948"&&v.evidence_receipt.job_id==="110680066600"&&v.evidence_receipt.run_url==="https://github.com/trimcrae/Alignment/actions/runs/36956360948","actual acquisition source/run/job binding");
  need(r.schema_version===1&&r.authorship.agent==="OpenAI Codex"&&r.authorship.model_family==="GPT-6"&&r.authorship.human_review==="not_performed","receipt authorship");
  need(r.execution.source_commit===v.evidence_receipt.source_commit&&r.execution.run_id===v.evidence_receipt.run_id&&r.execution.job_name==="acquire"&&utc(r.execution.collected_at,"collection")<=time,"receipt execution/time binding");
  need(r.method.max_html_bytes===2097152&&r.method.max_policy_pdf_bytes===8388608&&r.method.max_redirects===3&&r.method.cycle_seconds===180,"bounded method");
  const reused=r.reused_card;
  need(reused.state==="verified"&&reused.expected_sha256===CARD&&reused.sha256===CARD&&reused.bytes===4976826&&reused.pdf_pages===124&&reused.source_commit==="bda723fb2678787fc0ec6e52ad742d63b618ab5a"&&reused.run_id==="36951404278"&&reused.artifact_id==="11204066868","verified reused card provenance");
  need(JSON.stringify(reused.annotation_pages)==="[9,10]"&&reused.pointers.length===1,"bounded annotation scope");
  const p=reused.pointers[0];need(p.pdf_page===9&&p.uri===URI&&JSON.stringify(p.annotation_rectangle)===JSON.stringify(RECT),"original received-card URI/rectangle");
  need(r.sources.length===1&&r.sources[0].id==="official-rsp-route","one actual source route");
  const s=r.sources[0];
  need(s.state==="observed"&&s.kind==="html"&&s.requested_url===URI&&s.sha256===BODY&&s.bytes===171813&&s.normalized_text_sha256===TEXT,"observed announcement metadata");
  need(s.response.status===200&&s.response.final_url===URI&&s.response.content_type==="text/html; charset=utf-8"&&s.response.applied_byte_limit===2097152,"HTTP/MIME/size provenance");
  need(s.robots.allowed===true&&s.robots.status===200&&s.robots.url==="https://www.anthropic.com/robots.txt","permitted source");
  need(s.response.redirect_chain.length===1&&s.response.redirect_chain[0].url===URI&&s.response.redirect_chain[0].robots.allowed===true,"original direct source route");
  need(utc(s.observed_at,"observation")<=time&&s.policy_links.length===0,"actual source time/PDF candidate count");
  const a=v.received_card_reference;
  keys(a,["status","document_sha256","source_run_id","artifact_id","pdf_page","uri","annotation_rectangle","relation","limitation"],"received card pointer");
  need(a.status==="observed"&&a.document_sha256===CARD&&a.source_run_id===reused.run_id&&a.artifact_id===reused.artifact_id&&a.pdf_page===p.pdf_page&&a.uri===p.uri&&JSON.stringify(a.annotation_rectangle)===JSON.stringify(RECT)&&a.relation==="received_card_uri_only","card pointer is not historical or launch-edition proof");
  text(a.limitation,"pointer limitation");
  const o=v.official_route_observation;
  keys(o,["status","source_id","kind","source_url","content_sha256","bytes","observed_at","verification","declared_update_date","numeric_policy_version","hash_verification","extraction_verification"],"official route observation");
  need(o.status==="observed"&&o.source_id===s.id&&o.kind==="dated_policy_update_announcement"&&o.source_url===URI&&o.content_sha256===BODY&&o.bytes===s.bytes&&o.observed_at===s.observed_at&&o.verification==="primary_page_observed","dated source observation cannot be promoted to policy edition");
  need(o.hash_verification==="collector_computed_received_bytes_not_independently_recomputed"&&o.extraction_verification==="verbatim_spans_matched_to_original_collector_receipt","source-body hash/extraction verification inflation");
  keys(o.declared_update_date,["status","value","date_phrase","citation"],"declared date");const d=o.declared_update_date;
  need(d.status==="reported"&&d.value==="2024-10-15"&&d.date_phrase==="Oct 15, 2024","publisher-declared date");
  keys(d.citation,["source_id","content_sha256","normalized_text_sha256","quote"],"date citation");
  need(d.citation.source_id===s.id&&d.citation.content_sha256===BODY&&d.citation.normalized_text_sha256===TEXT&&d.citation.quote===DATE_QUOTE&&s.spans.some(x=>x.text.includes(d.citation.quote)),"exact publisher date/update quote is not in original acquired receipt");
  unknown(o.numeric_policy_version,["value"],"numeric policy version");
  unknown(v.historical_applicability,["version","policy_document_sha256","claim_id"],"historical applicability");
  unknown(v.launch_edition,["policy_document_sha256","claim_id"],"launch-edition identity");
  keys(v.completion,["status","stop_condition","official_route_requests","optional_policy_pdf_requests","policy_pdf_candidates","new_card_source_requests","reason"],"completion");
  need(v.completion.status==="version_gap"&&v.completion.stop_condition==="met"&&v.completion.official_route_requests===1&&v.completion.optional_policy_pdf_requests===0&&v.completion.policy_pdf_candidates===0&&v.completion.new_card_source_requests===0,"finite cycle/counts must match actual receipt");
  text(v.completion.reason,"explicit missing-version reason");
  need(r.selection.status==="unknown"&&r.selection.policy_pdf_candidates.length===0&&r.selection.explicitly_bound_candidates.length===0,"source selection cannot be inflated");
  return {valid:true,errors:[],counts:summarize(v)};
 }catch(e){return {valid:false,errors:[e instanceof Error?e.message:String(e)],counts:null};}
}
