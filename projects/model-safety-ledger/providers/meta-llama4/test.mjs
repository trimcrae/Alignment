// AI-authored OpenAI Codex/GPT-6: source/native-scope promotion regressions, no inference.
import {readFileSync} from "node:fs";
import {dirname,join} from "node:path";
import {fileURLToPath} from "node:url";
import {validate} from "./core.mjs";
import {loadBundle,deps} from "./validate.mjs";
const root=dirname(fileURLToPath(import.meta.url)),base=JSON.parse(readFileSync(join(root,"result.json"),"utf8")),bundle=loadBundle();
const clone=x=>JSON.parse(JSON.stringify(x));let checks=0,invalid=0;
function bad(label,f,bf){const r=clone(base),b={...bundle};if(f)f(r);if(bf)bf(b);try{validate(r,b,deps);}catch(e){checks++;invalid++;return;}throw new Error("Unsupported evidence/claim accepted: "+label);}
const summary=validate(base,bundle,deps);checks++;
if(summary.models!==2||summary.native_category_records!==3||summary.method_only_records!==2||summary.provider_reported_family_assessments!==1||summary.formal_model_threshold_determinations!==0||summary.formal_deployment_determinations!==0||summary.framework_binding!=="unknown"||summary.literal_citations!==14||summary.stop!=="met")throw Error("Truthful partial summary mismatch");checks++;
for(let i=0;i<2;i++)for(const field of["formal_threshold_determination","native_deployment_level","critical_risk_evaluated_configuration"]){
 bad("model unknown->absent",r=>r.models[i][field].status="absent");
 bad("model unknown->asserted",r=>r.models[i][field].value="High");
}
for(const field of["named_threshold_framework","framework_version"]){
 bad("frameworkunknown->absent",r=>r.native_card_taxonomy[field].status="absent");
 bad("frameworkunknown->asserted",r=>r.native_card_taxonomy[field].value="Critical Risks");
}
for(let i=0;i<3;i++){
 bad("thresholdunknown->absent",r=>r.native_categories[i].formal_threshold_relation.status="absent");
 bad("thresholdunknown->below",r=>r.native_categories[i].formal_threshold_relation.value="below");
}
for(let i=0;i<2;i++){
 bad("method promoted outcome",r=>r.native_categories[i].reported_outcome.status="provider_reported");
 bad("method promoted outcome value",r=>r.native_categories[i].reported_outcome.value="safe");
}
for(const f of["independently_verified_public_release","launch_artifact_availability","launch_edition_byte_identity"]){
 bad("releaseunknown->absent",r=>r.release[f].status="absent");
 bad("releaseunknown->date/hash",r=>r.release[f].value="2025-04-05");
}
bad("swappednative_names",r=>{[r.models[0].native_name,r.models[1].native_name]=[r.models[1].native_name,r.models[0].native_name];});
bad("swappedinternalIDs",r=>{[r.models[0].record_id,r.models[1].record_id]=[r.models[1].record_id,r.models[0].record_id];});
bad("swappedmodelcitations",r=>{[r.models[0].name_citation,r.models[1].name_citation]=[r.models[1].name_citation,r.models[0].name_citation];});
bad("thirdunacquiredmodel",r=>r.models.push(clone(r.models[0])));
bad("familyassessment->Scoutthreshold",r=>r.models[0].formal_threshold_determination={status:"provider_reported",value:r.native_categories[2].reported_outcome.value,reason_code:"family_copy"});
bad("familyassessment->Maverickthreshold",r=>r.models[1].formal_threshold_determination={status:"provider_reported",value:r.native_categories[2].reported_outcome.value,reason_code:"family_copy"});
bad("BF16benchmark->criticalconfig",r=>r.models[0].critical_risk_evaluated_configuration.value="BF16");
bad("riskheading->framework",r=>r.native_card_taxonomy.named_threshold_framework.value="Critical Risks");
bad("riskheading->level",r=>r.native_card_taxonomy.role="risk_level");
bad("CCLmapping",r=>r.limitations.framework_scale_mapping=true);
bad("CBRNEheading->nuclearcoverage",r=>r.native_categories[0].reported_method_scope="all_CBRNE_domains_evaluated");
bad("ChildSafety->chemicalmethod",r=>r.native_categories[1].method_citation="cbrne_method");
bad("cyberfamily->modelscope",r=>r.native_categories[2].reported_outcome.scope="each_model");
bad("cyberstatement->independentlyverified",r=>r.native_categories[2].reported_outcome.status="independently_verified");
bad("cyberstatement->safetyverdict",r=>r.native_categories[2].reported_outcome.value="Both models are safe");
bad("cyberstatementwrongcitation",r=>r.native_categories[2].reported_outcome.citation="system_guidance");
bad("duplicatednativecategory",r=>r.native_categories.push(clone(r.native_categories[2])));
bad("CBRNEtoChildlabel",r=>r.native_categories[0].native_label="Child Safety");
bad("unknownordinal",r=>r.native_categories[0].native_ordinal=4);
bad("guidance->deployeddecision",r=>r.deployment_guidance.formal_deployment_determination=true);
bad("declaredrelease->actual",r=>r.release.provider_declared_date.status="independently_verified");
bad("sharedcarddate->oneModel",r=>r.release.provider_declared_date.scope="scout_only");
bad("wrongdeclaredDate",r=>r.release.provider_declared_date.value="2025-04-06");
bad("datewrongcitation",r=>r.release.provider_declared_date.citation="model_scout");
for(const field of Object.keys(base.limitations).filter(k=>k!=="citation"))bad("limitpromotion:"+field,r=>r.limitations[field]=true);
bad("humanreviewfabricated",r=>r.authorship.human_review="completed");
bad("unexposedtransportverified",r=>r.source.transport="raw_HTTP_headers_verified");
bad("moreartifactreads",r=>r.source.artifact_reads=2);
bad("moreSources",r=>r.source.additional_source_reads=1);
bad("wrongGitcommit",r=>r.source.commit="f".repeat(40));
bad("measuredrateadded",r=>r.measured_failure_rate=0);
bad("inference",r=>r.stop.model_inference=true);
bad("sourcecontinuation",r=>r.stop.further_source_acquisition=true);
bad("missingstop",r=>r.stop.status="pending");
for(const field of Object.keys(bundle))bad("originalbytecorruption:"+field,null,b=>b[field]=Buffer.concat([b[field],Buffer.from(" ")]));
bad("sourcecoordinateforgery+hashrebind",null,b=>{const c=JSON.parse(b.citations);c.citations[3].start_byte++;c.citations[3].end_byte++;c.source_sha256="f".repeat(64);b.citations=Buffer.from(JSON.stringify(c));});
bad("originaltoolbase64swap",null,b=>{const t=JSON.parse(b.tool);t.structuredContent.content=Buffer.from("different artifact").toString("base64");b.tool=Buffer.from(JSON.stringify(t));});
console.log(JSON.stringify({checks,invalid_cases:invalid,valid_checks:checks-invalid}));
