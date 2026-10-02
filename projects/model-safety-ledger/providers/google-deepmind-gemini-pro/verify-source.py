#!/usr/bin/env python3
"""AI-authored OpenAI Codex/GPT-6: offline exact retained-byte/source-coordinate check."""
import hashlib,importlib.util,json,re,urllib.robotparser
from pathlib import Path
ROOT=Path(__file__).resolve().parent;E=ROOT/"evidence"
PINS={"original_receipt":"e47459cefe171ac1ee7af3217fd8100aba92333b63ccc882e838b5f91febb9ef","landing_selected":"88c0a33125de4edd1e66070cecc79c6828c88b5fa661735560c6c3069b058efa","card_receipt":"d0ce5a74bd26487261df721757f8060c2cea96d1394f0fa0488c6bca3eb35923","landing_received":"7ff785937e09f35781e18f6a429b5603674e434abb48ad43e9ce0a4016bafe39","robots_received":"f43be63c1571009a5f6a1364ef3bf60b48e50db989dbe9f47cc07818796b92f8"}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    paths={"original_receipt":"acquisition.json","landing_selected":"landing-selected.json","card_receipt":"card-acquisition.json","landing_received":"landing.html","robots_received":"robots-deepmind.google.txt"}
    raw={k:(E/p).read_bytes() for k,p in paths.items()}
    for k,v in raw.items():assert sha(v)==PINS[k],k+" immutable bytes mismatch"
    prior=json.loads(raw["original_receipt"]);s=json.loads(raw["landing_selected"]);card=json.loads(raw["card_receipt"])
    spec=importlib.util.spec_from_file_location("collector",ROOT/"collect.py");c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
    def forbidden(*a,**k):raise AssertionError("Offline source verifier attempted network access")
    c.get_raw=forbidden;c.acquire=forbidden
    entity,interpretation=c.decode_entity(raw["landing_received"],prior["sources"][0]["response"],limit_override=2097152)
    assert interpretation==s["decoded"]
    parser=c.Landing();parser.feed(entity.decode("utf-8",errors="strict"))
    t=c.normalize(" ".join(parser.text));q=s["model_information_quote"]
    assert t[q["start_char"]:q["end_char"]]==q["text"]
    assert len(parser.links)==s["all_anchor_count"]==141
    assert s["official_html_card_pointer"] in parser.links
    assert s["official_html_card_pointer"]["href"]==card["source"]["requested_url"]
    assert not c.card_candidates(parser,prior["sources"][0]["response"]["final_url"])
    title=re.search(rb"<title[^>]*>(.*?)</title>",entity,re.I|re.S)
    assert c.normalize(title.group(1).decode())==s["title"]=="Gemini 3.1 Pro — Google DeepMind"
    robots=urllib.robotparser.RobotFileParser(prior["sources"][0]["robots"]["url"])
    robots.parse(raw["robots_received"].decode().splitlines())
    assert robots.can_fetch(c.UA,card["source"]["requested_url"])
    assert card["method"]["source_requests"]==1 and card["source"]["state"]=="not_fetched"
    assert card["source"]["reason"]=="HTTPError: HTTP Error 302: Found"
    assert not (E/"card-response.bin").exists()
    print(json.dumps({"retained_received_bytes":len(raw["landing_received"]),"decoded_bytes":len(entity),"all_anchors":len(parser.links),"eligible_vendor_pdf_pointers":0,"exact_html_card_pointer_verified":True,"bound_preview_quote":[q["start_char"],q["end_char"]],"card_response_body_acquired":False,"network_requests":0},sort_keys=True))
if __name__=="__main__":main()
