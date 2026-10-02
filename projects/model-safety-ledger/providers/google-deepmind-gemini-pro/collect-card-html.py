#!/usr/bin/env python3
"""AI-authored OpenAI Codex/GPT-6: one exact unused HTML-card stage, no children."""
import base64,hashlib,importlib.util,json,os,re,signal,sys,urllib.robotparser
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("google_collect",ROOT/"collect.py")
c=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(c)
def main():
    plan=json.loads((ROOT/"card-amendment-plan.json").read_text())
    prior_raw=(ROOT/"evidence/acquisition.json").read_bytes()
    selected_raw=(ROOT/"evidence/landing-selected.json").read_bytes()
    assert c.sha(prior_raw)==plan["original_receipt_sha256"]
    assert c.sha(selected_raw)==plan["selected_landing_receipt_sha256"]
    prior=json.loads(prior_raw);selected=json.loads(selected_raw);u=plan["card_url"]
    assert u==selected["official_html_card_pointer"]["href"]=="https://deepmind.google/models/model-cards/gemini-3-1-pro"
    raw_landing=(ROOT/"evidence/landing.html").read_bytes()
    assert c.sha(raw_landing)==selected["received"]["sha256"]
    landing_entity,interp=c.decode_entity(raw_landing,prior["sources"][0]["response"],limit_override=c.HTML_LIMIT)
    assert interp==selected["decoded"]
    p=c.Landing();p.feed(landing_entity.decode("utf-8",errors="strict"))
    assert selected["official_html_card_pointer"] in p.links
    normalized=c.normalize(" ".join(p.text));q=selected["model_information_quote"]
    assert normalized[q["start_char"]:q["end_char"]]==q["text"]
    robots=(ROOT/"evidence/robots-deepmind.google.txt").read_bytes()
    rr=prior["sources"][0]["robots"];assert c.sha(robots)==rr["sha256"]
    robotparser=urllib.robotparser.RobotFileParser(rr["url"]);robotparser.parse(robots.decode().splitlines())
    assert robotparser.can_fetch(c.UA,u),"Reused same-origin robots disallow exact card"
    out=Path(os.environ["RUNNER_TEMP"])/"google-html-card";out.mkdir(exist_ok=True)
    receipt={"schema_version":1,"authorship":plan["authorship"],
      "execution":{"source_commit":os.getenv("GITHUB_SHA"),"run_id":os.getenv("GITHUB_RUN_ID"),"job_name":os.getenv("GITHUB_JOB"),"observed_at":c.now()},
      "method":{"stage":"One amended unused HTML-card GET; original landing reused, no redirects, children or PDF",
        "source_requests":0,"max_received_bytes":c.HTML_LIMIT,"max_decoded_bytes":c.HTML_LIMIT,
        "python":sys.version.split()[0],"cycle_seconds":180,"socket_seconds":12,"read_seconds":25},
      "discovery":{"selected_landing_receipt_sha256":c.sha(selected_raw),"original_receipt_sha256":c.sha(prior_raw),
        "exact_anchor":selected["official_html_card_pointer"],"reused_robots":rr,"reused_robots_observed_at":prior["execution"]["collected_at"]},
      "source":{"id":"official-html-model-card","requested_url":u,"state":"not_fetched"}}
    try:
        receipt["method"]["source_requests"]=1
        raw,meta=c.get_raw(u,limit_override=c.HTML_LIMIT)
        (out/"card-response.bin").write_bytes(raw)
        s=receipt["source"];s.update(state="received_uninterpreted",response=meta,bytes=len(raw),sha256=c.sha(raw))
        entity,interpretation=c.decode_entity(raw,meta,limit_override=c.HTML_LIMIT);s["interpretation"]=interpretation
        mime=(meta.get("content_type") or "").split(";")[0].strip().lower()
        if mime not in("text/html","application/xhtml+xml") or entity.startswith(b"%PDF-"):raise ValueError("Exact amended stage requires an HTML card response")
        parser=c.Landing();parser.feed(entity.decode("utf-8",errors="strict"))
        t=c.normalize(" ".join(parser.text));ranges=[]
        marker=r"Gemini.{0,40}Pro|Preview|Frontier Safety Framework|Critical Capability Level|\\bCCLs?\\b|capability threshold|dangerous capability|(?:does|did|has|have) not.{0,60}(?:reach|meet)|framework"
        for m in re.finditer(marker,t,re.I):
            a,b=max(0,m.start()-300),min(len(t),m.end()+900)
            if ranges and a<=ranges[-1][1]:ranges[-1]=(ranges[-1][0],max(b,ranges[-1][1]))
            else:ranges.append((a,b))
        title=re.search(rb"<title[^>]*>(.*?)</title>",entity,re.I|re.S)
        s.update(state="observed_html_card",title=c.normalize(title.group(1).decode()) if title else None,
          normalized_text_sha256=c.sha(t.encode()),normalized_text_length=len(t),
          spans=[{"start_char":a,"end_char":b,"text":t[a:b]} for a,b in ranges],
          normalization="Unicode whitespace collapsed to one ASCII space; stripped")
    except Exception as e:
        receipt["source"]["reason"]=type(e).__name__+": "+str(e)
    finally:
        receipt["execution"]["completed_at"]=c.now();payload=json.dumps(receipt,ensure_ascii=False,indent=2)+"\n"
        (out/"card-acquisition.json").write_text(payload,encoding="utf-8")
        print("GOOGLE_HTML_CARD_RECEIPT_BEGIN");print(payload,end="");print("GOOGLE_HTML_CARD_RECEIPT_END")
        if (out/"card-response.bin").exists():
            print("GOOGLE_HTML_CARD_BODY_BASE64_BEGIN");print(base64.b64encode((out/"card-response.bin").read_bytes()).decode());print("GOOGLE_HTML_CARD_BODY_BASE64_END")
if __name__=="__main__":
    def stop(_s,_f):raise c.CycleDeadline("180 second hard amended-card deadline")
    signal.signal(signal.SIGALRM,stop);signal.alarm(180);main()
