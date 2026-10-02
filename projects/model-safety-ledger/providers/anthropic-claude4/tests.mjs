// Produced by OpenAI Codex (AI agent, GPT-6). Human review not performed.
import {validate,summarize} from "./core.mjs";
const clone=v=>JSON.parse(JSON.stringify(v));
const assert=(ok,msg)=>{if(!ok)throw Error(msg);};
export function runTests(seed,receiptText,digest) {
  const original=JSON.stringify(seed), receipt=JSON.parse(receiptText);
  let checks=0;const good=validate(seed,receipt,digest(receiptText));
  assert(good.valid,"committed seed: "+good.errors.join("; "));checks++;
  assert(JSON.stringify(good.counts)===JSON.stringify({models:2,observed_system_cards:1,reported_deployment_decisions:2,reported_capability_assessments:3,unknown_capability_assessments:1,unknown_release_dates:2,unknown_launch_editions:2,scope:"Provider-native statements only; no independent capability assessment, model inference or human review"}),"coverage and explicit unknown counts");checks++;
  const cases=[
    ["deployment ASL values swapped despite both being in source",l=>{[l.claims[0].native_result,l.claims[1].native_result]=[l.claims[1].native_result,l.claims[0].native_result];}],
    ["deployment model attribution swapped",l=>{[l.claims[0].model_id,l.claims[1].model_id]=[l.claims[1].model_id,l.claims[0].model_id];}],
    ["Opus ASL3 precaution promoted to passed",l=>{l.claims[2].outcome="passed";}],
    ["Opus ASL3 treated as ruled out",l=>{l.claims[2].outcome="ruled_out";}],
    ["Opus ASL3 provisional qualification removed",l=>{l.claims[2].qualification="confirmed_passed";}],
    ["Sonnet ASL4 goal promoted to conclusion",l=>{Object.assign(l.models[1].determinations[2],{status:"reported",claim_id:"opus-asl4",reason:null});}],
    ["Opus ASL4 claim copied to Sonnet",l=>{l.claims[3].model_id=l.models[1].id;}],
    ["Sonnet3 assessment copied to Opus",l=>{l.claims[4].model_id=l.models[0].id;}],
    ["capability conflated with deployment",l=>{l.claims[2].axis="deployment_asl";}],
    ["native ASL renamed OpenAI High",l=>{l.claims[0].native_result="High";}],
    ["framework normalized across providers",l=>{l.framework.native_name="Preparedness Framework";}],
    ["framework version inferred from month",l=>{l.framework.version={status:"reported",value:"May2025",reason:null};}],
    ["edition inferred from Last-Modified",l=>{l.artifact.edition={status:"reported",value:"2025-09-02",reason:null};}],
    ["cover date promoted to model release",l=>{l.models[0].release_date={status:"reported",claim_id:"cover-month",reason:null};}],
    ["current bytes promoted to launch bytes",l=>{l.models[0].artifact_at_release.status="present";}],
    ["failed fetch promoted to absent card",l=>{l.models[0].artifact_at_release.status="absent";}],
    ["unknown determination treated as absent",l=>{l.models[1].determinations[2].status="absent";}],
    ["unknown determination treated as not evaluated",l=>{l.models[1].determinations[2].status="not_evaluated";}],
    ["unknown determination has claim",l=>{l.models[1].determinations[2].claim_id="opus-asl4";}],
    ["unknown reason removed",l=>{l.models[1].determinations[2].reason="";}],
    ["native cyber threshold invented",l=>{l.framework.cyber_formal_threshold.status="ASL-3";}],
    ["cyber statement reverses negation",l=>{l.framework.cyber_formal_threshold.native_statement=l.framework.cyber_formal_threshold.native_statement.replace("does not","does");}],
    ["capability qualification paraphrased",l=>{l.claims[2].citation.quote=l.claims[2].citation.quote.replace("not yet determined","determined");}],
    ["qualification quote shortened to ambiguous clause",l=>{l.claims[2].citation.quote="cannot clearly rule out ASL-3 risks";}],
    ["quote wrong page",l=>{l.claims[0].citation.pdf_page=3;}],
    ["quote hash replaced",l=>{l.claims[0].citation.document_sha256="f".repeat(64);}],
    ["quote experimental verification inflated",l=>{l.claims[0].verification="independent_experiment";}],
    ["artifact publisher substituted",l=>{l.artifact.publisher="OpenAI";}],
    ["artifact URL substituted",l=>{l.artifact.source_url="https://example.org/card.pdf";}],
    ["artifact byte hash substituted",l=>{l.artifact.document_sha256="f".repeat(64);}],
    ["artifact cover month unsupported",l=>{l.artifact.declared_month.value="2025-06";}],
    ["model renamed newer family",l=>{l.models[0].native_name="Claude Opus 4.1";}],
    ["model identity scope mismatch",l=>{l.models[0].identity.quote="Claude Sonnet 4";}],
    ["scope universe broadened",l=>{l.scope.model_ids.push("claude-5");}],
    ["native axis omitted",l=>{l.models[1].determinations.pop();}],
    ["native axis duplicated",l=>{l.models[0].determinations[2].axis="capability_asl3";}],
    ["claim duplicated",l=>{l.claims.push(clone(l.claims[0]));}],
    ["reported claim missing",l=>{l.models[0].determinations[0].claim_id=null;}],
    ["schema unknown extra claim",l=>{l.independent_safety_verdict="safe";}],
    ["human review inflated",l=>{l.authorship.human_review="performed";}],
    ["base unpinned",l=>{l.authorship.base_commit="main";}],
    ["receipt digest wrong",l=>{l.evidence_receipt.sha256="0".repeat(64);}],
    ["acquisition commit unpinned",l=>{l.evidence_receipt.source_commit="main";}],
    ["acquisition run substituted",l=>{l.evidence_receipt.run_id="1";}],
    ["acquisition job substituted",l=>{l.evidence_receipt.job_id="1";}],
    ["receipt cohort says failed",(_l,r)=>{r.sources[1].state="not_fetched";},true],
    ["receipt hash changed",(_l,r)=>{r.sources[1].sha256="f".repeat(64);},true],
    ["receipt size wrong",(_l,r)=>{r.sources[1].bytes++;},true],
    ["receipt PDF pages wrong",(_l,r)=>{r.sources[1].pdf_pages=0;},true],
    ["receipt HTTP error",(_l,r)=>{r.sources[1].response.status=403;},true],
    ["receipt robots denied",(_l,r)=>{r.sources[1].robots.allowed=false;},true],
    ["redirect robots denied",(_l,r)=>{r.sources[1].response.redirect_chain[1].robots.allowed=false;},true],
    ["redirect off provider",(_l,r)=>{r.sources[1].response.redirect_chain[1].location="https://example.org/card.pdf";},true],
    ["redirect robots wrong host",(_l,r)=>{r.sources[1].response.redirect_chain[1].robots.url="https://example.org/robots.txt";},true],
    ["multiple selected URLs",(_l,r)=>{r.selection.candidate_urls.push("https://example.org/card.pdf");},true],
    ["source observation after snapshot",(_l,r)=>{r.sources[1].observed_at="2027-01-01T00:00:00Z";},true],
    ["impossible snapshot day",l=>{l.snapshot_at="2026-02-31T00:00:00Z";}],
    ["original subset hash wrong",(_l,r)=>{r.subset_provenance.original_receipt_sha256="f".repeat(64);},true],
    ["original subset byte count wrong",(_l,r)=>{r.subset_provenance.original_receipt_utf8_bytes=49709;},true],
    ["selected page duplicated",(_l,r)=>{r.sources[1].excerpts.push(clone(r.sources[1].excerpts[0]));},true],
    ["rebinding cannot replace acquired normalized page digest",(_l,r)=>{r.sources[1].excerpts[0].normalized_page_text_sha256="f".repeat(64);},true],
    ["rebinding cannot shift original acquired span coordinates",(_l,r)=>{r.sources[1].excerpts[0].spans[0].start_char++;r.sources[1].excerpts[0].spans[0].end_char++;},true],
    ["original span coordinates wrong",(_l,r)=>{r.sources[1].excerpts[0].spans[0].end_char++;},true],
    ["original exact quote tampered",(_l,r)=>{r.sources[1].excerpts[4].spans[0].text=r.sources[1].excerpts[4].spans[0].text.replace("not yet","yes yet");},true],
    ["evidence page extracted without digest",(_l,r)=>{r.sources[1].excerpts[0].normalized_page_text_sha256="";},true],
    ["receipt provenance human review inflated",(_l,r)=>{r.authorship.human_review="performed";},true]
  ];
  for(const [name,mutate,rebind] of cases) {
    const l=clone(seed),r=clone(receipt);mutate(l,r);
    const sha=rebind?digest(JSON.stringify(r)):digest(receiptText);
    if(rebind)l.evidence_receipt.sha256=sha;
    const got=validate(l,r,sha);
    assert(!got.valid,"invalid case accepted: "+name);checks++;
  }
  const reordered=clone(seed);reordered.claims.reverse();
  assert(validate(reordered,receipt,digest(receiptText)).valid,"claim order must not change attribution");checks++;
  assert(JSON.stringify(seed)===original && JSON.stringify(receipt)===JSON.stringify(JSON.parse(receiptText)),"validator/tests mutate inputs");checks++;
  return {checks,invalid_cases:cases.length,actual_seed_summary:summarize(seed)};
}
