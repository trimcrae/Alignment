// AI-authored OpenAI Codex/GPT-6: malformed/promoted evidence regression cases.
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname,join} from "node:path";
import {validate} from "./core.mjs";
import {loadBundle,digest} from "./validate.mjs";
const root=dirname(fileURLToPath(import.meta.url));
const baseline=JSON.parse(readFileSync(join(root,"result.json"),"utf8"));
const bundle=loadBundle();let checks=0,invalid=0;
const clone=x=>JSON.parse(JSON.stringify(x));
function rejects(label,change,bchange){
 const r=clone(baseline),b={...bundle};if(change)change(r);if(bchange)bchange(b);
 try{validate(r,b,digest);}catch(e){checks++;invalid++;return;}
 throw new Error("Invalid source or claim accepted: "+label);
}
const summary=validate(baseline,bundle,digest);checks++;
if(summary.acquired_cards!==0||summary.native_domain_records!==0||summary.unknown_determination_fields!==8||summary.redirects_followed!==0||summary.stop!=="met")throw new Error("Unknown summary is wrong");checks++;
for(const field of Object.keys(baseline.determinations)){
 rejects(field+" unknown->absent",r=>r.determinations[field].status="absent");
 rejects(field+" promotevalue",r=>r.determinations[field].value="unsupported asserted value");
 rejects(field+" drop",r=>delete r.determinations[field]);
}
rejects("mapnativeaxes",r=>r.native_domain_records.push({native_domain:"guessed",level:"High"}));
rejects("inferredASL",r=>r.native_domain_records.push({native_domain:"ASL",level:3}));
rejects("cardnamefromslug",r=>r.determinations.actual_card_model_identity={status:"observed",value:"Gemini3.1Pro",reason_code:"urlslug"});
rejects("headerframeworkversion",r=>r.determinations.native_framework_version={status:"observed",value:"2026",reason_code:"observationdate"});
rejects("titleasrelease",r=>r.determinations.actual_release_timing={status:"observed",value:"2026-10-02",reason_code:"page_observation"});
rejects("launchfromcurrentbody",r=>r.scope_limits.launch_bytes_verified=true);
rejects("independentsafety",r=>r.scope_limits.independent_safety_verdict=true);
rejects("unknownequalsabsent",r=>r.scope_limits.unknown_means_absent=true);
rejects("cardabsence",r=>r.gap.card_absence_claimed=true);
rejects("inventredirecttarget",r=>r.gap.redirect_target.value="https://deepmind.google/somewhere/");
rejects("followedredirect",r=>r.source_attempts.redirects_followed=1);
rejects("acquiredcard",r=>r.source_attempts.card_body_acquired=true);
rejects("refetchedlanding",r=>r.source_attempts.landing_refetches=1);
rejects("PDFget",r=>r.source_attempts.pdf_gets=1);
rejects("childsource",r=>r.source_attempts.child_gets=1);
rejects("encodingasbaselinefailure",r=>r.interpretation_repair.original_defect="baseline_environment_failure");
rejects("inventencodingheader",r=>r.interpretation_repair.content_encoding_header="gzip");
rejects("oldanchorabsence",r=>r.interpretation_repair.zero_original_anchors_used_as_source_absence=true);
rejects("wrongmodelpage",r=>r.observation.displayed_name="2.5Pro");
rejects("launchscope",r=>r.observation.scope="launch_model_card");
rejects("Previewdropped",r=>r.observation.displayed_status="released");
rejects("humanreviewinvented",r=>r.authorship.human_review="completed");
rejects("sourcecommitmismatch",r=>r.evidence.amended_source_commit="f".repeat(40));
rejects("sourcejobmismatch",r=>r.evidence.amended_job_id="123");
rejects("unexpectedclaimfield",r=>r.measured_failure_rate=0);
rejects("moreacquisition",r=>r.stop.further_source_acquisition=true);
rejects("unmetstop",r=>r.stop.status="pending");
for(const field of Object.keys(bundle))rejects("source-byte-change:"+field,null,b=>b[field]=Buffer.concat([b[field],Buffer.from(" ") ]));
rejects("coordinateforgery+rebind",r=>r.evidence.landing_selected_sha256="f".repeat(64),b=>{
 const s=JSON.parse(b.landing_selected);s.model_information_quote.start_char++;s.model_information_quote.end_char++;b.landing_selected=Buffer.from(JSON.stringify(s));});
rejects("decodedhashforgery+rebind",r=>r.evidence.landing_selected_sha256="f".repeat(64),b=>{
 const s=JSON.parse(b.landing_selected);s.decoded.decoded_sha256="f".repeat(64);b.landing_selected=Buffer.from(JSON.stringify(s));});
console.log(JSON.stringify({checks,invalid_cases:invalid,valid_checks:checks-invalid}));
