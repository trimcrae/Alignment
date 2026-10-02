// AI-authored OpenAI Codex/GPT-6. Bounded immutable seed; unknown is never absent.
export const SOURCE_PINS=Object.freeze({
  "original_receipt": "e47459cefe171ac1ee7af3217fd8100aba92333b63ccc882e838b5f91febb9ef",
  "landing_selected": "88c0a33125de4edd1e66070cecc79c6828c88b5fa661735560c6c3069b058efa",
  "card_receipt": "d0ce5a74bd26487261df721757f8060c2cea96d1394f0fa0488c6bca3eb35923",
  "landing_received": "7ff785937e09f35781e18f6a429b5603674e434abb48ad43e9ce0a4016bafe39",
  "robots_received": "f43be63c1571009a5f6a1364ef3bf60b48e50db989dbe9f47cc07818796b92f8"
});
const UNKNOWN_REASONS=Object.freeze({
 actual_card_model_identity:"card_not_acquired",evaluated_configuration:"card_not_acquired",
 native_framework_name:"card_not_acquired",native_framework_version:"card_not_acquired",
 provider_native_capability_determination:"card_not_acquired",deployment_safeguard_level:"card_not_acquired",
 actual_release_timing:"no_release_time_evidence",launch_edition_bytes:"no_launch_byte_identity_evidence"
});
function need(ok,why){if(!ok)throw new Error(why);}
function keys(obj,names,path){need(obj!==null&&typeof obj==="object"&&!Array.isArray(obj),path+" must be an object");need(Object.keys(obj).sort().join("|")===names.slice().sort().join("|"),path+" keys mismatch");}
function exact(obj,expected,path){keys(obj,Object.keys(expected),path);for(const [k,v]of Object.entries(expected))need(obj[k]===v,path+"."+k+" must equal source-bound value");}
function unknown(obj,reason,path){exact(obj,{status:"unknown",value:null,reason_code:reason},path);}
export function validate(result,bundle,digest) {
 need(typeof digest==="function","A real received-byte digest function is required");
 keys(bundle,Object.keys(SOURCE_PINS),"bundle");
 for(const [k,v]of Object.entries(SOURCE_PINS))need(digest(bundle[k])===v,"Immutable "+k+" digest mismatch; changed inputs require a separately reviewed seed");
 const prior=JSON.parse(String(bundle.original_receipt)),selected=JSON.parse(String(bundle.landing_selected)),card=JSON.parse(String(bundle.card_receipt));
 need(prior.execution.source_commit==="b4fa5e647ee78c96272553d8ae66b4b01032d14c"&&prior.execution.run_id==="36960889488","Original source revision/run mismatch");
 need(prior.sources.length===1&&prior.sources[0].response.status===200,"Original landing source mismatch");
 need(card.execution.source_commit==="074565c5ad6409e4ce9dad281bdc4d92ac26699d"&&card.execution.run_id==="36962354293","Amended source revision/run mismatch");
 need(card.method.source_requests===1&&card.source.state==="not_fetched"&&card.source.reason==="HTTPError: HTTP Error 302: Found","Card attempt must stay a single refused302 with no body");
 need(selected.title==="Gemini 3.1 Pro — Google DeepMind"&&selected.model_information_quote.text==="Model information Name 3.1 Pro Status Preview"&&selected.model_information_quote.start_char===8255&&selected.model_information_quote.end_char===8300,"Landing context binding mismatch");
 keys(result,["schema_version","kind","authorship","provider","observation","source_attempts","gap","evidence","interpretation_repair","determinations","native_domain_records","scope_limits","stop"],"result");
 need(result.schema_version===1&&result.kind==="provider-primary-input-gap"&&result.provider==="Google DeepMind","Wrong bounded provider seed");
 exact(result.authorship,{agent:"OpenAI Codex",model_family:"GPT-6",session:"usage-sprint-2026-10-01",human_review:"not_performed"},"authorship");
 exact(result.observation,{official_landing_url:prior.sources[0].requested_url,observed_at:prior.execution.collected_at,page_title:selected.title,displayed_name:"3.1 Pro",displayed_status:"Preview",scope:"received_landing_page_only",context_reference:"landing-selected.json:model_information_quote"},"observation");
 exact(result.source_attempts,{original_landing_gets:1,original_robots_gets:1,amended_card_get_attempts:1,pdf_gets:0,landing_refetches:0,child_gets:0,redirects_followed:0,card_body_acquired:false},"source_attempts");
 keys(result.gap,["status","reason_code","official_card_pointer","card_request_state","observed_failure","redirect_target","card_absence_claimed"],"gap");
 for(const [k,v]of Object.entries({status:"missing_primary_evidence",reason_code:"exact_card_html_302_not_followed",official_card_pointer:selected.official_html_card_pointer.href,card_request_state:card.source.state,observed_failure:card.source.reason,card_absence_claimed:false}))need(result.gap[k]===v,"gap."+k+" is not source-bound");
 unknown(result.gap.redirect_target,"location_header_not_retained","gap.redirect_target");
 exact(result.evidence,{original_source_commit:prior.execution.source_commit,original_run_id:prior.execution.run_id,original_job_id:"110694095517",amended_source_commit:card.execution.source_commit,amended_run_id:card.execution.run_id,amended_job_id:"110698571380",original_receipt_sha256:SOURCE_PINS.original_receipt,landing_selected_sha256:SOURCE_PINS.landing_selected,card_receipt_sha256:SOURCE_PINS.card_receipt,landing_received_sha256:SOURCE_PINS.landing_received,robots_received_sha256:SOURCE_PINS.robots_received,landing_decoded_sha256:selected.decoded.decoded_sha256},"evidence");
 exact(result.interpretation_repair,{original_defect:"gzip_bytes_decoded_directly_as_utf8",corrected_from:"retained_original_received_bytes",content_encoding_header:"not_recorded_by_original_collector",zero_original_anchors_used_as_source_absence:false},"interpretation_repair");
 keys(result.determinations,Object.keys(UNKNOWN_REASONS),"determinations");
 for(const [k,reason]of Object.entries(UNKNOWN_REASONS))unknown(result.determinations[k],reason,"determinations."+k);
 need(Array.isArray(result.native_domain_records)&&result.native_domain_records.length===0,"An unacquired card cannot seed native domains or outcomes");
 exact(result.scope_limits,{model_inference_performed:false,independent_safety_verdict:false,framework_scale_mapping:false,historical_policy_applicability_verified:false,launch_bytes_verified:false,unknown_means_absent:false},"scope_limits");
 exact(result.stop,{status:"met",reason_code:"one_exact_card_attempt_302_refused",further_source_acquisition:false},"stop");
 return {acquired_cards:0,native_domain_records:0,unknown_determination_fields:Object.keys(UNKNOWN_REASONS).length,source_stage_requests:2,redirects_followed:0,stop:"met"};
}
