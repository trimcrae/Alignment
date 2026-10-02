// AI-authored OpenAI Codex/GPT-6. Provider-native partial ledger, no model evaluation.
export const SOURCE_PINS=Object.freeze({
  "card": "a1739083c8a496ca0c121d90b98659a6aa7e36fcc0092581db35ef99736d104f",
  "tool": "8e0e931fa87de381c1064f05a23d3555286234ca249a20524245ce4032bc83ce",
  "citations": "6ccbf38f9912682a319bad72a4364e42476d9d7c36d982837a2e29ca279bb3ce",
  "acquisition": "e254f2015dc109ef90613ce8e6f41b986ed7f26ce21a829004d2c83fea4afecf",
  "plan": "3dad6ab535bf09016def9c142bdd2ce61703bccd721ce064d2909b55c5ce6d5e"
});
function need(ok,why){if(!ok)throw new Error(why);}
function keys(o,ks,p){need(o!==null&&typeof o==="object"&&!Array.isArray(o),p+" object required");need(Object.keys(o).sort().join("|")===ks.slice().sort().join("|"),p+" keys mismatch");}
function exact(o,e,p){keys(o,Object.keys(e),p);for(const[k,v]of Object.entries(e))need(o[k]===v,p+"."+k+" source-bound mismatch");}
function unknown(o,reason,p){exact(o,{status:"unknown",value:null,reason_code:reason},p);}
const MODEL_BINDINGS=[["scout-17bx16e","Llama 4 Scout (17Bx16E)","model_scout"],["maverick-17bx128e","Llama 4 Maverick (17Bx128E)","model_maverick"]];
const CATEGORY_BINDINGS=[
 ["critical-risk-1",1,"CBRNE (Chemical, Biological, Radiological, Nuclear, and Explosive materials) helpfulness","cbrne_label","provider_reported_evaluation_method","Llama 4","chemical_and_biological_weapon_proliferation","cbrne_method"],
 ["critical-risk-2",2,"Child Safety","child_label","provider_reported_evaluation_method","post trained model","child_safety_evaluation_and_fine_tuning","child_method"],
 ["critical-risk-3",3,"Cyber attack enablement","cyber_label","provider_reported_family_assessment","Llama 4 models","catastrophic_cyber_threat_scenario_capabilities","cyber_method_and_assessment"]
];
export function validate(r,b,d){
 keys(b,Object.keys(SOURCE_PINS),"source_bundle");
 for(const[k,v]of Object.entries(SOURCE_PINS))need(d.sha256(b[k])===v,"Immutable "+k+" source digest mismatch");
 need(d.byteLength(b.card)===23764&&d.gitBlobSha1(b.card)==="80e624a8f7415bd533070277cc6b9f3c5215625b","Original Git object identity mismatch");
 const tool=JSON.parse(String(b.tool)),c=JSON.parse(String(b.citations)),a=JSON.parse(String(b.acquisition)),p=JSON.parse(String(b.plan));
 need(tool.structuredContent.encoding==="base64"&&tool.structuredContent.sha==="80e624a8f7415bd533070277cc6b9f3c5215625b","Original exposed connector receipt mismatch");
 need(d.sha256(d.decodeBase64(tool.structuredContent.content))===SOURCE_PINS.card,"Original tool bytes differ from retained card");
 need(a.exposed_connector_artifact_reads===1&&a.stop.further_source_reads===false&&a.observed.http_request_count===null,"Connector scope must remain exposed-read-only");
 need(p.source.commit==="0e0b8c519242d5833d8c11bffc1232b77ad7f301"&&p.source.path==="models/llama4/MODEL_CARD.md","Pinned source route mismatch");
 need(c.source_sha256===SOURCE_PINS.card&&c.citations.length===14,"Citation set/source mismatch");
 const qs=new Map();for(const q of c.citations){
  keys(q,["id","source_id","start_byte","end_byte","quote"],"citation");
  need(!qs.has(q.id)&&q.source_id==="meta-llama4-git-card","Duplicate/unbound citation");
  need(Number.isSafeInteger(q.start_byte)&&Number.isSafeInteger(q.end_byte)&&q.start_byte>=0&&q.end_byte>q.start_byte&&q.end_byte<=23764,"Invalid UTF8 byte coordinates");
  need(d.byteSlice(b.card,q.start_byte,q.end_byte)===q.quote,"Literal source quote mismatch");qs.set(q.id,q.quote);
 }
 const cite=(id)=>{need(qs.has(id),"Missing citation "+id);return qs.get(id);};
 need(cite("developer")==="**Model developer**: Meta","Publisher statement mismatch");
 keys(r,["schema_version","authorship","provider","artifact_role","source","models","native_card_taxonomy","native_categories","deployment_guidance","release","limitations","stop"],"result");
 need(r.schema_version===1&&r.provider==="Meta"&&r.artifact_role==="official_model_card_with_provider_reported_safety_assessments","Wrong native artifact/provider");
 exact(r.authorship,{agent:"OpenAI Codex",model_family:"GPT-6",session:"usage-sprint-2026-10-01",human_review:"not_performed"},"authorship");
 exact(r.source,{id:"meta-llama4-git-card",repository:p.source.repository,commit:p.source.commit,path:p.source.path,git_blob_sha1:p.source.expected_git_blob_sha1,file_sha256:SOURCE_PINS.card,file_bytes:23764,observed_at:"2026-10-02T05:39:30Z",verification:"exact_original_connector_file_bytes",transport:"connector_internals_unobserved",artifact_reads:1,additional_source_reads:0},"source");
 need(Array.isArray(r.models)&&r.models.length===2,"Only two source-listed models");
 for(let i=0;i<2;i++){
  const m=r.models[i],[id,name,ref]=MODEL_BINDINGS[i];keys(m,["record_id","native_name","name_citation","formal_threshold_determination","native_deployment_level","critical_risk_evaluated_configuration"],"model");
  need(m.record_id===id&&m.native_name===name&&m.name_citation===ref&&cite(ref)===name,"Native model name/record/citation confusion");
  unknown(m.formal_threshold_determination,"no_model_specific_formal_threshold_binding_in_card","model.formal_threshold_determination");
  unknown(m.native_deployment_level,"no_model_specific_native_deployment_level_in_card","model.native_deployment_level");
  unknown(m.critical_risk_evaluated_configuration,"critical_risk_configuration_not_explicitly_bound_to_model","model.critical_risk_evaluated_configuration");
 }
 keys(r.native_card_taxonomy,["section_title","role","section_citation","named_threshold_framework","framework_version"],"native_card_taxonomy");
 need(r.native_card_taxonomy.section_title==="Critical Risks"&&r.native_card_taxonomy.role==="native_category_heading"&&r.native_card_taxonomy.section_citation==="native_section"&&cite("native_section")==="### Critical Risks ","Category heading must not become a framework or risk level");
 unknown(r.native_card_taxonomy.named_threshold_framework,"not_explicitly_bound_by_acquired_card","framework.name");
 unknown(r.native_card_taxonomy.framework_version,"not_explicitly_bound_by_acquired_card","framework.version");
 need(Array.isArray(r.native_categories)&&r.native_categories.length===3,"Only three source native categories");
 for(let i=0;i<3;i++){
  const x=r.native_categories[i],[id,ord,label,ref,kind,scope,method,mref]=CATEGORY_BINDINGS[i];
  keys(x,["record_id","native_ordinal","native_label","label_citation","record_kind","source_scope","reported_method_scope","method_citation","reported_outcome","formal_threshold_relation"],"native_category");
  for(const[k,v]of Object.entries({record_id:id,native_ordinal:ord,native_label:label,label_citation:ref,record_kind:kind,source_scope:scope,reported_method_scope:method,method_citation:mref}))need(x[k]===v,"Native category/method/scope confusion: "+k);
  need(cite(ref).includes(label)&&cite(mref).includes(cite(ref)),"Category label and method citation mismatch");
  unknown(x.formal_threshold_relation,"no_formal_threshold_binding_in_card","category.formal_threshold_relation");
  if(i<2)unknown(x.reported_outcome,"method_description_does_not_report_outcome","category.reported_outcome");
  else exact(x.reported_outcome,{status:"provider_reported",scope:"family_only",value:cite("cyber_family_conclusion"),citation:"cyber_family_conclusion"},"cyber.family_outcome");
 }
 exact(r.deployment_guidance,{kind:"provider_general_system_guidance",citation:"system_guidance",formal_deployment_determination:false},"deployment_guidance");cite("system_guidance");
 keys(r.release,["provider_declared_date","independently_verified_public_release","launch_artifact_availability","launch_edition_byte_identity"],"release");
 exact(r.release.provider_declared_date,{status:"provider_reported",value:"2025-04-05",literal_date:"April 5, 2025",scope:"shared_model_card_statement",citation:"declared_release"},"release.declared_date");
 need(cite("declared_release")==="**Model Release Date:** April 5, 2025","Provider-declared release statement mismatch");
 unknown(r.release.independently_verified_public_release,"no_independent_release_time_evidence","release.independent");
 unknown(r.release.launch_artifact_availability,"no_launch_availability_evidence","release.launch_availability");
 unknown(r.release.launch_edition_byte_identity,"no_launch_edition_byte_identity_evidence","release.launch_bytes");
 exact(r.limitations,{citation:"limits",independent_model_evaluation:false,measured_failure_rates_claimed:false,framework_scale_mapping:false,family_assessment_copied_to_model_determinations:false,named_framework_absence_claimed:false,unknown_means_absent:false,source_observation_is_launch_evidence:false},"limitations");cite("limits");
 exact(r.stop,{status:"met",formal_framework_gap:"explicit_unknown",further_source_acquisition:false,model_inference:false,external_outreach:false,merge:false},"stop");
 return {models:2,native_category_records:3,method_only_records:2,provider_reported_family_assessments:1,formal_model_threshold_determinations:0,formal_deployment_determinations:0,framework_binding:"unknown",provider_declared_release_date:"2025-04-05",independent_release_and_launch:"unknown",literal_citations:14,exposed_artifact_reads:1,stop:"met"};
}
