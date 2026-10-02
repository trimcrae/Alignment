#!/usr/bin/env python3
"""Produced by OpenAI Codex (AI agent, GPT-6); one bounded public source cycle."""
from __future__ import annotations
import hashlib, html, io, json, os, re, signal, sys, time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
import urllib.error, urllib.parse, urllib.request, urllib.robotparser
import pypdf

ROOT = Path(__file__).resolve().parent
UA = "AlignmentArtifactLedger/0.2 (+https://github.com/trimcrae/Alignment)"
HOSTS = {"www.anthropic.com", "www-cdn.anthropic.com"}
PAGE_LIMIT = 2 * 1024 * 1024
PDF_LIMIT = 20 * 1024 * 1024
ROBOTS_LIMIT = 256 * 1024
robots_cache = {}
def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
def sha(raw): return hashlib.sha256(raw).hexdigest()
def allowed_url(url):
    p = urllib.parse.urlsplit(url)
    if p.scheme != "https" or p.hostname not in HOSTS or p.username or p.password or p.port not in (None,443):
        raise ValueError("URL leaves the explicit provider HTTPS host allowlist")
    return p
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl): return None
OPENER = urllib.request.build_opener(NoRedirect())
def raw_get(url, limit):
    allowed_url(url)
    req = urllib.request.Request(url, headers={"User-Agent":UA, "Accept":"*/*"})
    start = time.monotonic()
    with OPENER.open(req, timeout=12) as response:
        chunks = []; total = 0
        while True:
            if time.monotonic() - start > 25: raise TimeoutError("25 second response read bound")
            chunk = response.read(min(65536, limit + 1 - total))
            if not chunk: break
            chunks.append(chunk); total += len(chunk)
            if total > limit: raise ValueError("Response exceeds byte bound")
        return b"".join(chunks), {"status":response.status, "final_url":response.url,
            "content_type":response.headers.get("Content-Type"),
            "last_modified":response.headers.get("Last-Modified"), "etag":response.headers.get("ETag")}
def robots(url):
    p=allowed_url(url); host=p.hostname
    if host not in robots_cache:
        robots_url="https://"+host+"/robots.txt"
        rec={"url":robots_url,"user_agent":UA}
        try:
            raw,meta=raw_get(robots_url,ROBOTS_LIMIT)
            parser=urllib.robotparser.RobotFileParser(robots_url)
            parser.parse(raw.decode("utf-8",errors="replace").splitlines())
            rec.update(status=meta["status"],sha256=sha(raw),body=raw.decode("utf-8",errors="replace"))
            robots_cache[host]=(rec,parser)
        except urllib.error.HTTPError as e:
            rec.update(status=e.code,error=type(e).__name__)
            robots_cache[host]=(rec,None)
        except Exception as e:
            rec.update(status=None,error=type(e).__name__+": "+str(e));robots_cache[host]=(rec,None)
    rec,parser=robots_cache[host]
    return {**rec,"allowed":parser.can_fetch(UA,url) if parser else rec["status"] in (404,410)}
def acquire(url,limit):
    chain=[]; current=url
    for _ in range(4):
        rr=robots(current); chain.append({"url":current,"robots":rr})
        if not rr["allowed"]: raise PermissionError("robots unavailable or disallows explicit path")
        try:
            raw,meta=raw_get(current,limit)
            return raw,{**meta,"redirect_chain":chain},rr
        except urllib.error.HTTPError as e:
            if e.code not in (301,302,303,307,308): raise
            target=urllib.parse.urljoin(current,e.headers.get("Location",""))
            allowed_url(target)
            chain[-1].update(status=e.code,location=target)
            current=target
    raise ValueError("More than three redirects")
class Page(HTMLParser):
    def __init__(self): super().__init__();self.links=[];self.text=[];self.current=None;self.skip=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ("script","style"): self.skip+=1
        if tag=="a": self.current={"href":a.get("href",""),"text":""}
    def handle_endtag(self,tag):
        if tag in ("script","style"): self.skip=max(0,self.skip-1)
        if tag=="a" and self.current is not None: self.links.append(self.current);self.current=None
    def handle_data(self,data):
        if self.skip:return
        self.text.append(data)
        if self.current is not None:self.current["text"]+=data
def normalized(text): return re.sub(r"\s+"," ",text).strip()
def excerpt(text,pattern,margin=450):
    matches=list(re.finditer(pattern,text,re.I))
    intervals=[]
    for m in matches:
        a,b=max(0,m.start()-margin),min(len(text),m.end()+margin)
        if intervals and a<=intervals[-1][1]:intervals[-1]=(intervals[-1][0],max(b,intervals[-1][1]))
        else:intervals.append((a,b))
    return [{"start_char":a,"end_char":b,"text":text[a:b]} for a,b in intervals]
def pdf_excerpts(raw):
    reader=pypdf.PdfReader(io.BytesIO(raw),strict=True)
    if reader.is_encrypted or not 1<=len(reader.pages)<=200:raise ValueError("Unsupported encrypted/page-count PDF")
    result=[]
    # Safety-level and governance passages only; no benchmark tasks or exploit content.
    pattern=r"ASL[-\u2010-\u2015 ]?[23]|Responsible Scaling Policy|AI Safety Level|activated.{0,100}ASL|deploy.{0,100}ASL"
    for i,page in enumerate(reader.pages,1):
        text=normalized(page.extract_text() or "")
        spans=excerpt(text,pattern,650)
        if i==1:spans=[{"start_char":0,"end_char":min(1800,len(text)),"text":text[:1800]}]+spans
        if spans: result.append({"pdf_page":i,"normalized_page_text_sha256":sha(text.encode()),
                               "normalization":"Unicode whitespace collapsed to one ASCII space; stripped","spans":spans})
    return len(reader.pages),result
def main():
    plan=json.loads((ROOT/"acquisition-plan.json").read_text())
    receipt={"schema_version":1,"authorship":plan["authorship"],
      "execution":{"source_commit":os.getenv("GITHUB_SHA"),"run_id":os.getenv("GITHUB_RUN_ID"),"job_name":os.getenv("GITHUB_JOB"),"collected_at":None},
      "method":{"python":sys.version.split()[0],"pypdf":pypdf.__version__,"socket_timeout_seconds":12,
                "response_read_seconds":25,"cycle_seconds":180,"max_page_bytes":PAGE_LIMIT,"max_pdf_bytes":PDF_LIMIT,
                "max_redirects":3,"scope":"Official page pointers and selected governance PDF spans only; no inference or launch-edition inference"},
      "sources":[],"selection":{"status":"unknown","candidate_urls":[],"reason":None}}
    candidates=set()
    try:
        for source in plan["sources"]:
            r={"id":source["id"],"requested_url":source["url"],"observed_at":now()}
            try:
                raw,meta,rr=acquire(source["url"],PDF_LIMIT if source["id"]=="claude-4-card-pointer" else PAGE_LIMIT);r.update(state="observed",response=meta,robots=rr,bytes=len(raw),sha256=sha(raw))
                if raw.startswith(b"%PDF-"):
                    candidates.add(meta["final_url"]);r.update(kind="pdf_pointer_response")
                    # Never fetch the identical PDF again: preserve already received bytes.
                    r["_raw_pdf"]=raw
                else:
                    parser=Page();parser.feed(raw.decode("utf-8",errors="replace"))
                    text=normalized(" ".join(parser.text))
                    r.update(kind="html",normalized_text_sha256=sha(text.encode()),spans=excerpt(text,r"Claude (?:Opus|Sonnet) 4|ASL[- ]?3|system card|May 22, 2025",800),links=[])
                    for link in parser.links:
                        u=urllib.parse.urljoin(meta["final_url"],html.unescape(link["href"]))
                        try:p=allowed_url(u)
                        except ValueError:continue
                        if p.hostname=="www-cdn.anthropic.com" and p.path.lower().endswith(".pdf") and re.search(r"(Claude.?4.*system.?card|system.?card.*Claude.?4|system.?card)",link["text"],re.I):
                            candidates.add(u);r["links"].append({"url":u,"anchor":normalized(link["text"])})
            except Exception as e:
                r.update(state="not_fetched",reason=type(e).__name__+": "+str(e),robots=robots(source["url"]))
            receipt["sources"].append(r)
        receipt["selection"]["candidate_urls"]=sorted(candidates)
        if len(candidates)!=1:
            receipt["selection"].update(reason="No unique explicitly linked official provider PDF; no guessed URL or mirror used")
        else:
            url=next(iter(candidates));r={"id":"claude-4-system-card","requested_url":url,"observed_at":now(),"kind":"system_card"}
            try:
                prior=next((s for s in receipt["sources"] if s.get("_raw_pdf") is not None and s.get("response",{}).get("final_url")==url),None)
                if prior:raw,meta,rr=prior["_raw_pdf"],prior["response"],prior["robots"]
                else:raw,meta,rr=acquire(url,PDF_LIMIT)
                if not raw.startswith(b"%PDF-"):raise ValueError("Official linked response is not PDF")
                count,spans=pdf_excerpts(raw)
                r.update(state="observed",response=meta,robots=rr,bytes=len(raw),sha256=sha(raw),pdf_pages=count,excerpts=spans)
                receipt["selection"].update(status="observed",reason="Exactly one explicit official provider PDF pointer")
                target=Path(os.environ["RUNNER_TEMP"])/"anthropic-card.pdf";target.write_bytes(raw)
            except Exception as e:r.update(state="not_fetched",reason=type(e).__name__+": "+str(e),robots=robots(url));receipt["selection"].update(reason="Explicit pointer exists but PDF was not acquired; current and launch edition remain unknown")
            receipt["sources"].append(r)
    except Exception as e:
        receipt["selection"]["reason"]="Cycle stopped: "+type(e).__name__+": "+str(e)
    finally:
        for s in receipt["sources"]:s.pop("_raw_pdf",None)
        receipt["execution"]["collected_at"]=now()
        payload=json.dumps(receipt,ensure_ascii=False,indent=2)+"\n"
        (Path(os.environ["RUNNER_TEMP"])/"anthropic-acquisition.json").write_text(payload,encoding="utf-8")
        print("ANTHROPIC_PRIMARY_RECEIPT_BEGIN");print(payload,end="");print("ANTHROPIC_PRIMARY_RECEIPT_END")
if __name__=="__main__":
    class CycleDeadline(BaseException): pass
    def deadline(signum,frame): raise CycleDeadline("180 second cycle bound")
    signal.signal(signal.SIGALRM,deadline);signal.alarm(180);main()
