#!/usr/bin/env python3
"""Produced by OpenAI Codex (AI agent, GPT-6): reuse one card, inspect one official RSP route."""
from __future__ import annotations
import hashlib, html, io, json, os, re, signal, sys, time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
import urllib.error, urllib.parse, urllib.request, urllib.robotparser
import pypdf

ROOT=Path(__file__).resolve().parent
UA="AlignmentRSPVersion/0.1 (+https://github.com/trimcrae/Alignment)"
HOSTS={"www.anthropic.com","www-cdn.anthropic.com"}
HTML_LIMIT=2*1024*1024;PDF_LIMIT=8*1024*1024;ROBOTS_LIMIT=256*1024
CARD_SHA="5e3e63370473db1f1e499642ef8400250e19aba8cbb5f84f2b919cf2b27898cb"
ROBOTS={}
class CycleDeadline(BaseException): pass
def now():return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")
def digest(raw):return hashlib.sha256(raw).hexdigest()
def normal(t):return re.sub(r"\s+"," ",t).strip()
def safe_url(u):
    p=urllib.parse.urlsplit(u)
    if p.scheme!="https" or p.hostname not in HOSTS or p.username or p.password or p.port not in(None,443):
        raise ValueError("URL leaves fixed official provider HTTPS hosts")
    return p
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None
OPENER=urllib.request.build_opener(NoRedirect())
def response_limit(content_type,robots=False):
    if robots:return ROBOTS_LIMIT
    return PDF_LIMIT if (content_type or "").split(";")[0].strip().lower()=="application/pdf" else HTML_LIMIT
def get_raw(u,robots=False):
    safe_url(u);started=time.monotonic()
    req=urllib.request.Request(u,headers={"User-Agent":UA,"Accept":"*/*"})
    with OPENER.open(req,timeout=12) as response:
        content_type=response.headers.get("Content-Type")
        limit=response_limit(content_type,robots)
        parts=[];count=0
        while True:
            if time.monotonic()-started>25:raise TimeoutError("25 second response-read bound")
            piece=response.read(min(65536,limit+1-count))
            if not piece:break
            if count==0 and not robots:
                if piece.startswith(b"%PDF-"):limit=PDF_LIMIT
                elif limit==PDF_LIMIT:raise ValueError("PDF MIME response lacks PDF magic header")
            count+=len(piece)
            if count>limit:raise ValueError("Response exceeds MIME-selected byte bound")
            parts.append(piece)
        return b"".join(parts),{"status":response.status,"final_url":response.url,"content_type":content_type,
            "last_modified":response.headers.get("Last-Modified"),"etag":response.headers.get("ETag"),
            "applied_byte_limit":limit}
def robots(u):
    p=safe_url(u);host=p.hostname
    if host not in ROBOTS:
        ru="https://"+host+"/robots.txt";r={"url":ru,"user_agent":UA}
        try:
            raw,meta=get_raw(ru,True);parser=urllib.robotparser.RobotFileParser(ru)
            parser.parse(raw.decode("utf-8",errors="replace").splitlines())
            r.update(status=meta["status"],sha256=digest(raw));ROBOTS[host]=(r,parser)
        except urllib.error.HTTPError as e:r.update(status=e.code,error=type(e).__name__);ROBOTS[host]=(r,None)
        except Exception as e:r.update(status=None,error=type(e).__name__+": "+str(e));ROBOTS[host]=(r,None)
    r,parser=ROBOTS[host]
    return {**r,"allowed":parser.can_fetch(UA,u) if parser else r["status"] in(404,410)}
def acquire(u):
    chain=[];current=u
    for _ in range(4):
        rr=robots(current);chain.append({"url":current,"robots":rr})
        if not rr["allowed"]:raise PermissionError("robots unavailable or disallows explicit path")
        try:
            raw,meta=get_raw(current);return raw,{**meta,"redirect_chain":chain},rr
        except urllib.error.HTTPError as e:
            if e.code not in(301,302,303,307,308):raise
            target=urllib.parse.urljoin(current,e.headers.get("Location",""));safe_url(target)
            chain[-1].update(status=e.code,location=target);current=target
    raise ValueError("More than three official redirects")
class PolicyPage(HTMLParser):
    def __init__(self):super().__init__();self.text=[];self.links=[];self.current=None;self.skip=0
    def handle_starttag(self,t,attrs):
        if t in("script","style"):self.skip+=1
        if t=="a":self.current={"href":dict(attrs).get("href",""),"text":""}
    def handle_endtag(self,t):
        if t in("script","style"):self.skip=max(0,self.skip-1)
        if t=="a" and self.current is not None:self.links.append(self.current);self.current=None
    def handle_data(self,t):
        if self.skip:return
        self.text.append(t)
        if self.current is not None:self.current["text"]+=t
def spans(text,pattern,margin=320):
    intervals=[]
    for m in re.finditer(pattern,text,re.I):
        a,b=max(0,m.start()-margin),min(len(text),m.end()+margin)
        if intervals and a<=intervals[-1][1]:intervals[-1]=(intervals[-1][0],max(b,intervals[-1][1]))
        else:intervals.append((a,b))
    return [{"start_char":a,"end_char":b,"text":text[a:b]} for a,b in intervals]
def card_pointers(raw):
    if digest(raw)!=CARD_SHA:raise ValueError("Reused card bytes do not match the previously acquired immutable PDF")
    reader=pypdf.PdfReader(io.BytesIO(raw),strict=True)
    if reader.is_encrypted or len(reader.pages)!=124:raise ValueError("Reused card page count/encryption mismatch")
    records=[]
    for n in(9,10):
        for annotation in reader.pages[n-1].get("/Annots",[]):
            a=annotation.get_object();action=a.get("/A")
            if action is None:continue
            action=action.get_object();u=action.get("/URI")
            if not isinstance(u,str):continue
            try:p=safe_url(u)
            except ValueError:continue
            if not re.search(r"responsible[-_ ]?scaling[-_ ]?policy|(?:^|[/_-])rsp(?:[/_.-]|$)",urllib.parse.unquote(p.path),re.I):continue
            records.append({"pdf_page":n,"uri":u,"annotation_rectangle":[float(x) for x in a.get("/Rect",[])],
                            "relation":"URI annotation in the received card, not launch-edition availability proof"})
    return records
def policy_pdf(raw):
    if not raw.startswith(b"%PDF-"):raise ValueError("Response MIME identifies PDF but bytes are not PDF")
    reader=pypdf.PdfReader(io.BytesIO(raw),strict=True)
    if reader.is_encrypted or not 1<=len(reader.pages)<=80:raise ValueError("Policy PDF page/encryption bound")
    out=[]
    for n,p in enumerate(reader.pages,1):
        t=normal(p.extract_text() or "")
        # Only policy identity/revision/effective-date passages; no model/eval exploit content.
        ss=spans(t,r"\b(?:version|effective|updated|adopted|supersed|Claude (?:Opus |Sonnet )?4)\b",380)
        if n==1:ss=[{"start_char":0,"end_char":min(1600,len(t)),"text":t[:1600]}]+ss
        if ss:out.append({"pdf_page":n,"normalized_page_text_sha256":digest(t.encode()),"spans":ss})
    return len(reader.pages),out
def select_policy_links(parser,base):
    explicit=[];candidates=[]
    for a in parser.links:
        u=urllib.parse.urljoin(base,html.unescape(a["href"]));label=normal(a["text"])
        try:p=safe_url(u)
        except ValueError:continue
        if p.path.lower().endswith(".pdf") and re.search(r"\bRSP\b|Responsible Scaling Policy",label,re.I):
            entry={"url":u,"anchor":label};candidates.append(entry)
            # Only explicit card/model applicability in the anchor can authorize a dated PDF.
            # A date/version near May2025 alone is not a historical applicability relation.
            if (re.search(r"\bClaude (?:Opus |Sonnet )?4(?![\w.])",label,re.I)
                and re.search(r"\b(?:version\s+\d|v\d|\d{4})\b",label,re.I)
                and re.search(r"\b(?:applicable|governing|applies to|in effect for)\b",label,re.I)):
                explicit.append(entry)
    return candidates,explicit
def main():
    plan=json.loads((ROOT/"acquisition-plan.json").read_text())
    receipt={"schema_version":1,"authorship":plan["authorship"],
       "execution":{"source_commit":os.getenv("GITHUB_SHA"),"run_id":os.getenv("GITHUB_RUN_ID"),"job_name":os.getenv("GITHUB_JOB"),"collected_at":None},
       "method":{"python":sys.version.split()[0],"pypdf":pypdf.__version__,"cycle_seconds":180,"socket_seconds":12,
           "response_read_seconds":25,"max_html_bytes":HTML_LIMIT,"max_policy_pdf_bytes":PDF_LIMIT,"max_redirects":3,
           "scope":"Reused card RSP annotations on pages9/10; one official policy route and at most one explicitly bound dated policy PDF; no current-to-historical inference"},
       "reused_card":{"source_commit":"bda723fb2678787fc0ec6e52ad742d63b618ab5a","run_id":"36951404278","artifact_id":"11204066868",
           "expected_sha256":CARD_SHA,"state":"unknown","annotation_pages":[9,10],"pointers":[]},
       "sources":[],"selection":{"status":"unknown","policy_pdf_candidates":[],"explicitly_bound_candidates":[],"reason":None}}
    try:
        raw=(Path(os.environ["REUSED_CARD_DIR"])/"anthropic-card.pdf").read_bytes()
        records=card_pointers(raw)
        receipt["reused_card"].update(state="verified",sha256=digest(raw),bytes=len(raw),pdf_pages=124,pointers=records)
        uris=sorted({p["uri"] for p in records})
        if len(uris)>1:
            receipt["selection"]["reason"]="Ambiguous RSP annotations; no policy route was guessed";return
        target=uris[0] if uris else plan["official_policy_route"]
        result={"id":"official-rsp-route","requested_url":target,"observed_at":now()}
        try:
            received,meta,rr=acquire(target)
            result.update(state="observed",response=meta,robots=rr,bytes=len(received),sha256=digest(received))
            if received.startswith(b"%PDF-"):
                count,excerpts=policy_pdf(received)
                result.update(kind="policy_pdf",pdf_pages=count,excerpts=excerpts)
                receipt["selection"].update(status="policy_document_observed",reason="Explicit received-card route produced a policy PDF; historical applicability still requires a reviewed native statement")
            else:
                parser=PolicyPage();parser.feed(received.decode("utf-8",errors="replace"))
                t=normal(" ".join(parser.text));candidates,explicit=select_policy_links(parser,meta["final_url"])
                result.update(kind="html",normalized_text_sha256=digest(t.encode()),
                    spans=spans(t,r"\b(?:version|effective|updated|previous|histor|2025|2026|Claude (?:Opus |Sonnet )?4)\b",380),
                    policy_links=candidates)
                receipt["selection"].update(policy_pdf_candidates=candidates,explicitly_bound_candidates=explicit,
                    reason="Current official policy pointer is mutable; version dates alone do not bind the May2025 card")
                if len(explicit)==1:
                    u=explicit[0]["url"];pdf={"id":"explicit-dated-rsp","requested_url":u,"observed_at":now(),"kind":"policy_pdf"}
                    try:
                        pbytes,pmeta,prr=acquire(u);count,excerpts=policy_pdf(pbytes)
                        pdf.update(state="observed",response=pmeta,robots=prr,bytes=len(pbytes),sha256=digest(pbytes),pdf_pages=count,excerpts=excerpts)
                        receipt["selection"].update(status="policy_document_observed",reason="One explicit model/card-linked dated policy candidate observed; relation requires independent evidence review")
                    except Exception as e:pdf.update(state="not_fetched",reason=type(e).__name__+": "+str(e),robots=robots(u))
                    receipt["sources"].append(pdf)
            receipt["sources"].insert(0,result)
        except Exception as e:
            result.update(state="not_fetched",reason=type(e).__name__+": "+str(e),robots=robots(target));receipt["sources"].append(result)
            receipt["selection"]["reason"]="Official policy route not acquired; no fallback mirror or guessed archived edition"
    except Exception as e:
        receipt["reused_card"].update(state="not_verified",reason=type(e).__name__+": "+str(e))
        receipt["selection"]["reason"]="Reused input unavailable or invalid; no fresh card acquisition attempted"
    finally:
        receipt["execution"]["collected_at"]=now()
        payload=json.dumps(receipt,ensure_ascii=False,indent=2)+"\n"
        (Path(os.environ["RUNNER_TEMP"])/"rsp-version-acquisition.json").write_text(payload,encoding="utf-8")
        print("RSP_VERSION_RECEIPT_BEGIN");print(payload,end="");print("RSP_VERSION_RECEIPT_END")
if __name__=="__main__":
    def stop(_signal,_frame):raise CycleDeadline("180 second hard acquisition cycle deadline")
    signal.signal(signal.SIGALRM,stop);signal.alarm(180);main()
