#!/usr/bin/env python3
"""AI-authored OpenAI Codex/GPT-6: independent stdlib source/UTF8 coordinate verifier."""
import base64,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PINS={
  "card": "a1739083c8a496ca0c121d90b98659a6aa7e36fcc0092581db35ef99736d104f",
  "tool": "8e0e931fa87de381c1064f05a23d3555286234ca249a20524245ce4032bc83ce",
  "citations": "6ccbf38f9912682a319bad72a4364e42476d9d7c36d982837a2e29ca279bb3ce",
  "acquisition": "e254f2015dc109ef90613ce8e6f41b986ed7f26ce21a829004d2c83fea4afecf",
  "plan": "3dad6ab535bf09016def9c142bdd2ce61703bccd721ce064d2909b55c5ce6d5e"
}
PATHS={"card":"evidence/MODEL_CARD.md","tool":"evidence/original-tool-receipt.json","citations":"evidence/citations.json","acquisition":"evidence/acquisition.json","plan":"acquisition-plan.json"}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def check_quote(raw,q):
    a,b=q["start_byte"],q["end_byte"]
    if type(a) is not int or type(b) is not int or not 0<=a<b<=len(raw):raise ValueError("Invalid UTF8 file-byte coordinates")
    if raw[a:b]!=q["quote"].encode("utf-8"):raise ValueError("Source quote does not match UTF8 bytes")
def verify(root=ROOT):
    bundle={k:(root/p).read_bytes() for k,p in PATHS.items()}
    for k,raw in bundle.items():
        if sha(raw)!=PINS[k]:raise ValueError("Immutable "+k+" changed")
    raw=bundle["card"];tool=json.loads(bundle["tool"]);citations=json.loads(bundle["citations"])
    gitsha=hashlib.sha1(("blob "+str(len(raw))).encode()+bytes((0,))+raw).hexdigest()
    if len(raw)!=23764 or gitsha!="80e624a8f7415bd533070277cc6b9f3c5215625b":raise ValueError("Git object byte identity mismatch")
    decoded=base64.b64decode("".join(tool["structuredContent"]["content"].split()),validate=True)
    if decoded!=raw:raise ValueError("Original base64 tool bytes mismatch")
    if len(citations["citations"])!=14:raise ValueError("Expected fourteen source quotes")
    seen=set()
    for q in citations["citations"]:
        if q["id"] in seen:raise ValueError("Duplicate quote identity")
        seen.add(q["id"]);check_quote(raw,q)
    result=json.loads((root/"result.json").read_text())
    if result["native_categories"][2]["reported_outcome"]["scope"]!="family_only":raise ValueError("Family assessment scope changed")
    if any(m["formal_threshold_determination"]["status"]!="unknown" for m in result["models"]):raise ValueError("Unsupported model threshold claim")
    return {"file_bytes":len(raw),"sha256":sha(raw),"git_blob_sha1":gitsha,"literal_UTF8_byte_quotes":len(seen),"original_tool_base64_matches":True,"provider_reported_family_assessments":1,"formal_model_threshold_determinations":0,"provider_GETs":0}
if __name__=="__main__":print(json.dumps(verify(),sort_keys=True))
