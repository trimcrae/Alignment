#!/usr/bin/env python3
"""AI-authored OpenAI Codex/GPT-6: verify owned retained bytes without provider GETs."""
import argparse, base64, hashlib, importlib.util, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RECEIPT_SHA="e47459cefe171ac1ee7af3217fd8100aba92333b63ccc882e838b5f91febb9ef"
def digest(raw):return hashlib.sha256(raw).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument("artifact",type=Path);args=p.parse_args()
    receipt_raw=(args.artifact/"acquisition.json").read_bytes()
    assert digest(receipt_raw)==RECEIPT_SHA,"Original receipt byte binding changed"
    r=json.loads(receipt_raw)
    assert r["execution"]["source_commit"]=="b4fa5e647ee78c96272553d8ae66b4b01032d14c"
    assert r["execution"]["run_id"]=="36960889488"
    spec=importlib.util.spec_from_file_location("google_collect",ROOT/"collect.py")
    collector=importlib.util.module_from_spec(spec);spec.loader.exec_module(collector)
    def forbidden(*a,**k):raise AssertionError("Offline inspection attempted a source GET")
    collector.get_raw=forbidden;collector.acquire=forbidden
    s=r["sources"][0];raw=(args.artifact/"landing.html").read_bytes()
    assert len(raw)==s["bytes"] and digest(raw)==s["sha256"]
    robots=(args.artifact/"robots-deepmind.google.txt").read_bytes()
    assert len(robots)==s["robots"]["bytes"] and digest(robots)==s["robots"]["sha256"]
    parser=collector.Landing();parser.feed(raw.decode("utf-8",errors="replace"))
    t=collector.normalize(" ".join(parser.text))
    old_candidates=collector.card_candidates(parser,s["response"]["final_url"])
    assert digest(t.encode())==s["normalized_text_sha256"]
    assert collector.page_spans(t)==s["spans"]
    assert old_candidates==r["selection"]["candidates"]
    assert sorted({a["url"] for a in old_candidates})==r["selection"]["unique_candidate_urls"]
    assert not (args.artifact/"model-card.pdf").exists()
    entity,interpretation=collector.decode_entity(raw,s["response"])
    corrected_parser=collector.Landing();corrected_parser.feed(entity.decode("utf-8",errors="strict"))
    corrected_text=collector.normalize(" ".join(corrected_parser.text))
    candidates=collector.card_candidates(corrected_parser,s["response"]["final_url"])
    title=re.search(rb"<title[^>]*>(.*?)</title>",entity,re.I|re.S)
    result={"schema_version":1,"method":"Offline reuse of owned Actions artifact; no provider GET",
      "original_receipt_sha256":RECEIPT_SHA,"landing_sha256":digest(raw),"landing_bytes":len(raw),
      "robots_sha256":digest(robots),"normalized_text_sha256":digest(t.encode()),
      "original_normalized_text_length":len(t),"corrected_normalized_text_length":len(corrected_text),"interpretation":interpretation,"eligible_card_pointers":len(candidates),
      "all_anchor_count":len(corrected_parser.links),"title":collector.normalize(title.group(1).decode(errors="replace")) if title else None,
      "normalized_text_prefix":corrected_text[:1800],"anchors":[a for a in corrected_parser.links if re.search(r"model.?card|\\.pdf|frontier|responsib",a["href"]+" "+a["text"]+" "+a["aria_label"],re.I)],"eligible_candidates":candidates,"identity_spans":collector.page_spans(corrected_text),
      "raw_bytes_and_original_extraction":"verified against original receipt","repair":"Original collector decoded compressed bytes directly as text; corrected interpretation reuses retained bytes only",
      "scope_limit":"HTTP200 and zero eligible anchors are observations, not evidence that a model card or determination is absent"}
    print("RETAINED_INSPECTION_BEGIN");print(json.dumps(result,ensure_ascii=False,indent=2));print("RETAINED_INSPECTION_END")
    print("RETAINED_HTML_BASE64_BEGIN");print(base64.b64encode(raw).decode("ascii"));print("RETAINED_HTML_BASE64_END")
    print("RETAINED_ROBOTS_BASE64_BEGIN");print(base64.b64encode(robots).decode("ascii"));print("RETAINED_ROBOTS_BASE64_END")
if __name__=="__main__":main()
