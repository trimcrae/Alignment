#!/usr/bin/env python3
"""Produced by OpenAI Codex (AI agent, GPT-6): one official page and at most one model card."""
from __future__ import annotations
import gzip, hashlib, io, json, os, re, signal, sys, time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
import urllib.error, urllib.parse, urllib.request, urllib.robotparser
import pypdf

ROOT=Path(__file__).resolve().parent
UA="AlignmentGoogleCard/0.1 (+https://github.com/trimcrae/Alignment)"
HTML_LIMIT=2*1024*1024;PDF_LIMIT=12*1024*1024;ROBOTS_LIMIT=256*1024
ROBOTS={};OUTPUT=None
class CycleDeadline(BaseException):pass
def now():return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")
def sha(raw):return hashlib.sha256(raw).hexdigest()
def normalize(t):return re.sub(r"\s+"," ",t).strip()
def safe_url(u,robots=False):
    p=urllib.parse.urlsplit(u)
    if p.scheme!="https" or p.username or p.password or p.port not in(None,443):
        raise ValueError("Source URL must be explicit uncredentialed HTTPS")
    decoded=urllib.parse.unquote(p.path)
    if "\\" in decoded or any(x in(".","..") for x in decoded.split("/")):
        raise ValueError("Path escapes the explicit vendor route")
    if p.hostname=="deepmind.google":return p
    if p.hostname=="storage.googleapis.com":
        if robots and p.path=="/robots.txt":return p
        if not decoded.startswith("/deepmind-media/"):raise ValueError("Storage source is outside the exact vendor bucket")
        return p
    raise ValueError("Source host leaves DeepMind/vendor allowlist")
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None
OPENER=urllib.request.build_opener(NoRedirect())
def get_raw(u,robots=False,limit_override=None):
    safe_url(u,robots);start=time.monotonic()
    req=urllib.request.Request(u,headers={"User-Agent":UA,"Accept":"*/*"})
    with OPENER.open(req,timeout=12) as response:
        mime=response.headers.get("Content-Type")
        limit=limit_override if limit_override is not None else(ROBOTS_LIMIT if robots else(PDF_LIMIT if (mime or "").split(";")[0].strip().lower()=="application/pdf" else HTML_LIMIT))
        chunks=[];count=0
        while True:
            if time.monotonic()-start>25:raise TimeoutError("25 second response-read bound")
            part=response.read(min(65536,limit+1-count))
            if not part:break
            if count==0 and not robots and limit_override is None:
                if part.startswith(b"%PDF-"):limit=PDF_LIMIT
                elif limit==PDF_LIMIT and not part.startswith(bytes((31,139))):raise ValueError("PDF MIME response lacks PDF or supported gzip received magic")
            count+=len(part)
            if count>limit:raise ValueError("Response exceeds MIME/magic-selected byte bound")
            chunks.append(part)
        return b"".join(chunks),{"status":response.status,"final_url":response.url,"content_type":mime,
             "applied_byte_limit":limit,"content_encoding":response.headers.get("Content-Encoding"),"last_modified":response.headers.get("Last-Modified"),"etag":response.headers.get("ETag")}
def decode_entity(raw,meta,limit_override=None):
    """Interpret received bytes with a separate bounded decoded-entity receipt; no GET."""
    encoding=(meta.get("content_encoding") or "").strip().lower()
    is_gzip=raw.startswith(bytes((31,139)))
    if encoding not in("","identity","gzip"):raise ValueError("Unsupported Content-Encoding")
    if encoding=="gzip" and not is_gzip:raise ValueError("Gzip header lacks gzip magic")
    stream=gzip.GzipFile(fileobj=io.BytesIO(raw)) if is_gzip else io.BytesIO(raw)
    chunks=[];count=0;limit=limit_override if limit_override is not None else(PDF_LIMIT if (meta.get("content_type") or "").split(";")[0].strip().lower()=="application/pdf" else HTML_LIMIT)
    while True:
        part=stream.read(min(65536,limit+1-count))
        if not part:break
        if count==0 and limit_override is None:
            if part.startswith(b"%PDF-"):limit=PDF_LIMIT
            elif limit==PDF_LIMIT:raise ValueError("Decoded PDF MIME lacks PDF magic")
        count+=len(part)
        if count>limit:raise ValueError("Decoded entity exceeds MIME/magic-selected byte bound")
        chunks.append(part)
    entity=b"".join(chunks)
    return entity,{"encoding_basis":"gzip_magic" if is_gzip else"identity",
      "content_encoding_header":meta.get("content_encoding"),"decoded_bytes":len(entity),
      "decoded_sha256":sha(entity),"applied_decoded_byte_limit":limit}
def robots_for(u):
    host=safe_url(u).hostname
    if host not in ROBOTS:
        url="https://"+host+"/robots.txt";r={"url":url,"user_agent":UA}
        try:
            raw,meta=get_raw(url,True);parser=urllib.robotparser.RobotFileParser(url)
            entity,decoded=decode_entity(raw,meta,ROBOTS_LIMIT)
            parser.parse(entity.decode("utf-8",errors="replace").splitlines())
            r.update(status=meta["status"],sha256=sha(raw),bytes=len(raw))
            if OUTPUT is not None:(OUTPUT/("robots-"+host+".txt")).write_bytes(raw)
            ROBOTS[host]=(r,parser)
        except urllib.error.HTTPError as e:r.update(status=e.code,error=type(e).__name__);ROBOTS[host]=(r,None)
        except Exception as e:r.update(status=None,error=type(e).__name__+": "+str(e));ROBOTS[host]=(r,None)
    r,parser=ROBOTS[host]
    return {**r,"allowed":parser.can_fetch(UA,u) if parser else r["status"] in(404,410)}
def acquire(u):
    route=[];current=u
    for _ in range(4):
        rr=robots_for(current);route.append({"url":current,"robots":rr})
        if not rr["allowed"]:raise PermissionError("Robots unavailable or disallows explicit source path")
        try:
            raw,meta=get_raw(current);return raw,{**meta,"redirect_chain":route},rr
        except urllib.error.HTTPError as e:
            if e.code not in(301,302,303,307,308):raise
            target=urllib.parse.urljoin(current,e.headers.get("Location",""));safe_url(target)
            route[-1].update(status=e.code,location=target);current=target
    raise ValueError("More than three approved redirects")
class Landing(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.text=[];self.a=None;self.skip=0
    def handle_starttag(self,t,attrs):
        data=dict(attrs)
        if t in("script","style"):self.skip+=1
        if t=="a":self.a={"href":data.get("href",""),"text":"","aria_label":data.get("aria-label",""),"raw_start_tag":self.get_starttag_text()}
    def handle_endtag(self,t):
        if t in("script","style"):self.skip=max(0,self.skip-1)
        if t=="a" and self.a is not None:self.links.append(self.a);self.a=None
    def handle_data(self,t):
        if self.skip:return
        self.text.append(t)
        if self.a is not None:self.a["text"]+=t
def card_candidates(parser,base):
    out=[]
    for a in parser.links:
        u=urllib.parse.urldefrag(urllib.parse.urljoin(base,a["href"]))[0]
        try:p=safe_url(u)
        except ValueError:continue
        label=normalize(a["text"]+" "+a["aria_label"])
        if (p.hostname=="storage.googleapis.com" and p.path.lower().endswith(".pdf")
             and re.search(r"\bmodel\s*[- ]?\s*card\b",label,re.I)):
            out.append({"url":u,"anchor":label,"raw_start_tag":a["raw_start_tag"]})
    return out
def excerpts(raw):
    reader=pypdf.PdfReader(io.BytesIO(raw),strict=True)
    if reader.is_encrypted or not 1<=len(reader.pages)<=100:raise ValueError("Unsupported card page count/encryption")
    result=[]
    marker=r"Frontier Safety Framework|Critical Capability Level|\bCCLs?\b|capability threshold|(?:does|did|has|have) not.{0,60}(?:reach|meet)|framework"
    for n,p in enumerate(reader.pages,1):
        t=normalize(p.extract_text() or "");ranges=[]
        if n==1:ranges.append((0,min(1500,len(t))))
        for m in re.finditer(marker,t,re.I):
            a,b=max(0,m.start()-400),min(len(t),m.end()+750)
            if ranges and a<=ranges[-1][1]:ranges[-1]=(ranges[-1][0],max(b,ranges[-1][1]))
            else:ranges.append((a,b))
        if ranges:result.append({"pdf_page":n,"normalized_page_text_sha256":sha(t.encode()),
            "normalization":"Unicode whitespace collapsed to one ASCII space; stripped",
            "spans":[{"start_char":a,"end_char":b,"text":t[a:b]} for a,b in ranges]})
    return len(reader.pages),result
def page_spans(t):
    ranges=[]
    for m in re.finditer(r"Gemini.{0,35}Pro|\bPreview\b|model\s*[- ]?\s*card",t,re.I):
        a,b=max(0,m.start()-150),min(len(t),m.end()+350)
        if ranges and a<=ranges[-1][1]:ranges[-1]=(ranges[-1][0],max(b,ranges[-1][1]))
        else:ranges.append((a,b))
    return [{"start_char":a,"end_char":b,"text":t[a:b]} for a,b in ranges]
def main():
    global OUTPUT
    plan=json.loads((ROOT/"acquisition-plan.json").read_text())
    OUTPUT=Path(os.environ["RUNNER_TEMP"])/"google-primary-source";OUTPUT.mkdir(exist_ok=True)
    receipt={"schema_version":1,"authorship":plan["authorship"],
      "execution":{"source_commit":os.getenv("GITHUB_SHA"),"run_id":os.getenv("GITHUB_RUN_ID"),"job_name":os.getenv("GITHUB_JOB"),"collected_at":None},
      "method":{"python":sys.version.split()[0],"pypdf":pypdf.__version__,"cycle_seconds":180,"socket_seconds":12,"response_read_seconds":25,
          "max_html_bytes":HTML_LIMIT,"max_pdf_bytes":PDF_LIMIT,"max_redirects":3,"max_pdf_pages":100,
          "scope":"One official Gemini Pro page, one unique explicitly labeled model-card pointer; governance/identity spans only, no inference or historical edition assertion"},
      "sources":[],"selection":{"status":"unknown","candidates":[],"unique_candidate_urls":[],"reason":None},
      "raw_files":[]}
    landing={"id":"official-pro-landing","requested_url":plan["landing_url"],"observed_at":now()}
    try:
        raw,meta,rr=acquire(plan["landing_url"])
        landing.update(state="observed",response=meta,robots=rr,bytes=len(raw),sha256=sha(raw))
        name="landing.pdf" if raw.startswith(b"%PDF-") else"landing.html";(OUTPUT/name).write_bytes(raw)
        receipt["raw_files"].append({"path":name,"bytes":len(raw),"sha256":sha(raw)})
        entity,interpretation=decode_entity(raw,meta);landing["interpretation"]=interpretation
        if entity.startswith(b"%PDF-"):
            count,selected=excerpts(entity);landing.update(kind="direct_model_card_response")
            card={"id":"gemini-pro-model-card","requested_url":meta["final_url"],"observed_at":landing["observed_at"],"kind":"model_card",
                 "state":"observed","response":meta,"robots":rr,"bytes":len(raw),"sha256":sha(raw),"pdf_pages":count,"excerpts":selected,
                 "received_via":"reused_direct_official_landing_response"}
            (OUTPUT/"model-card.pdf").write_bytes(raw);receipt["raw_files"].append({"path":"model-card.pdf","bytes":len(raw),"sha256":sha(raw)})
            receipt["sources"]=[landing,card];receipt["selection"].update(status="observed",reason="Official landing route directly returned a card PDF; no duplicate card fetch")
        else:
            parser=Landing();parser.feed(entity.decode("utf-8",errors="replace"))
            t=normalize(" ".join(parser.text));candidates=card_candidates(parser,meta["final_url"]);urls=sorted({a["url"] for a in candidates})
            landing.update(kind="html",normalized_text_sha256=sha(t.encode()),spans=page_spans(t))
            receipt["sources"].append(landing);receipt["selection"].update(candidates=candidates,unique_candidate_urls=urls)
            if len(urls)!=1:
                receipt["selection"]["reason"]="No unique explicit official model-card PDF pointer; no guessed URL, alternative provider or report fallback"
            else:
                u=urls[0];card={"id":"gemini-pro-model-card","requested_url":u,"observed_at":now(),"kind":"model_card"}
                try:
                    pdf,pmeta,prr=acquire(u)
                    card.update(state="received_uninterpreted",response=pmeta,robots=prr,bytes=len(pdf),sha256=sha(pdf),received_via="unique_official_model_card_pointer")
                    (OUTPUT/"model-card.pdf").write_bytes(pdf);receipt["raw_files"].append({"path":"model-card.pdf","bytes":len(pdf),"sha256":sha(pdf)})
                    pdf_entity,pdf_interpretation=decode_entity(pdf,pmeta);card["interpretation"]=pdf_interpretation
                    if not pdf_entity.startswith(b"%PDF-"):raise ValueError("Official linked card did not return PDF bytes")
                    count,selected=excerpts(pdf_entity);card.update(state="observed",pdf_pages=count,excerpts=selected)
                    receipt["selection"].update(status="observed",reason="Exactly one official vendor-bucket model-card pointer acquired")
                except Exception as e:card.update(state="received_uninterpreted" if "bytes" in card else"not_fetched",reason=type(e).__name__+": "+str(e),robots=robots_for(u));receipt["selection"]["reason"]="Explicit primary card could not be interpreted or acquired; preserve unknowns"
                receipt["sources"].append(card)
    except Exception as e:
        landing.update(state="received_uninterpreted" if "bytes" in landing else"not_fetched",reason=type(e).__name__+": "+str(e),robots=robots_for(plan["landing_url"]))
        receipt["sources"].append(landing);receipt["selection"]["reason"]="Official landing route not acquired; no fallback or retry"
    finally:
        receipt["execution"]["collected_at"]=now();payload=json.dumps(receipt,ensure_ascii=False,indent=2)+"\n"
        (OUTPUT/"acquisition.json").write_text(payload,encoding="utf-8")
        print("GOOGLE_PRIMARY_RECEIPT_BEGIN");print(payload,end="");print("GOOGLE_PRIMARY_RECEIPT_END")
if __name__=="__main__":
    def stop(_s,_f):raise CycleDeadline("180 second hard source-cycle deadline")
    signal.signal(signal.SIGALRM,stop);signal.alarm(180);main()
