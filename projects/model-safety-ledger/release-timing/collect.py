#!/usr/bin/env python3
"""AI-authored one-cycle public metadata collector; no PDF or repository writes."""
from __future__ import annotations
import hashlib, json, os, re, sys, time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
import urllib.error, urllib.parse, urllib.request, urllib.robotparser

ROOT = Path(__file__).resolve().parent
USER_AGENT = "AlignmentReleaseTiming/0.1 (+https://github.com/trimcrae/Alignment)"
MAX_BYTES = 3 * 1024 * 1024
MAX_ROBOTS_BYTES = 256 * 1024
SOCKET_TIMEOUT = 12
REQUEST_BUDGET = 25
CYCLE_BUDGET = 150
MAX_REDIRECTS = 3

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def permitted_url(url, host):
    p = urllib.parse.urlsplit(url)
    return p.scheme == "https" and p.hostname == host and p.port in (None, 443) and not p.username and not p.password

class BoundedRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, host):
        super().__init__()
        self.host, self.count = host, 0
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.count += 1
        if self.count > MAX_REDIRECTS or not permitted_url(newurl, self.host):
            raise ValueError("Redirect exceeded fixed HTTPS host/count boundary")
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def fetch(url, host, limit, cycle_deadline):
    if not permitted_url(url, host):
        raise ValueError("URL outside fixed HTTPS source host")
    deadline = min(time.monotonic() + REQUEST_BUDGET, cycle_deadline)
    if deadline <= time.monotonic():
        raise TimeoutError("Cycle budget exhausted")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/json,text/plain;q=0.9"})
    opener = urllib.request.build_opener(BoundedRedirect(host))
    timeout = min(SOCKET_TIMEOUT, max(0.1, deadline - time.monotonic()))
    with opener.open(req, timeout=timeout) as response:
        parts, size = [], 0
        while True:
            if time.monotonic() >= deadline:
                raise TimeoutError("Request total read budget exhausted")
            chunk = response.read(min(65536, limit + 1 - size))
            size += len(chunk)
            if size > limit:
                raise ValueError("Response exceeded byte boundary")
            if not chunk:
                break
            parts.append(chunk)
        raw = b"".join(parts)
        if time.monotonic() >= deadline:
            raise TimeoutError("Request total read budget exhausted")
        return raw, {"status": response.status, "final_url": response.url,
                     "content_type": response.headers.get("Content-Type"),
                     "last_modified": response.headers.get("Last-Modified"),
                     "etag": response.headers.get("ETag")}

def get_robots(host, cycle_deadline):
    url = "https://" + host + "/robots.txt"
    receipt = {"url": url, "user_agent": USER_AGENT, "observed_at": now()}
    parser = urllib.robotparser.RobotFileParser(url)
    try:
        raw, metadata = fetch(url, host, MAX_ROBOTS_BYTES, cycle_deadline)
        parser.parse(raw.decode("utf-8", errors="replace").splitlines())
        receipt.update({"status": metadata["status"], "sha256": hashlib.sha256(raw).hexdigest(), "state": "parsed"})
    except urllib.error.HTTPError as exc:
        receipt.update({"status": exc.code, "state": "missing" if exc.code in (404, 410) else "unavailable"})
    except Exception as exc:
        receipt.update({"status": None, "state": "unavailable", "error": type(exc).__name__ + ": " + str(exc)})
    return parser, receipt

class MetadataHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text, self.meta, self.links, self.ld = [], [], [], []
        self.skip, self.ld_depth, self.ld_text = 0, 0, []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style"):
            self.skip += 1
            if tag == "script" and a.get("type", "").lower() == "application/ld+json":
                self.ld_depth = self.skip
                self.ld_text = []
        if tag == "meta" and len(self.meta) < 100:
            key = a.get("name") or a.get("property")
            if key and a.get("content"):
                self.meta.append({"key": key, "content": a["content"]})
        if tag == "a" and len(self.links) < 1000 and a.get("href"):
            self.links.append(a["href"])
        if tag == "time" and a.get("datetime"):
            self.meta.append({"key": "time:datetime", "content": a["datetime"]})
    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            if self.ld_depth == self.skip:
                self.ld.append("".join(self.ld_text))
                self.ld_depth = 0
            self.skip = max(0, self.skip - 1)
        if tag in ("p", "div", "section", "h1", "h2", "li"):
            self.text.append(" ")
    def handle_data(self, data):
        if self.ld_depth:
            self.ld_text.append(data)
        elif not self.skip:
            self.text.append(data)

def date_fields(value, path="$"):
    rows = []
    if isinstance(value, dict):
        for k, v in value.items():
            if k in ("datePublished", "dateModified", "uploadDate", "name", "headline", "@type"):
                rows.append({"path": path + "." + k, "value": v})
            if isinstance(v, (dict, list)):
                rows.extend(date_fields(v, path + "." + k))
    elif isinstance(value, list):
        for i, item in enumerate(value):
            rows.extend(date_fields(item, path + "[" + str(i) + "]"))
    return rows

def extract_html(raw):
    parser = MetadataHTML()
    parser.feed(raw.decode("utf-8", errors="replace"))
    text = re.sub(r"\s+", " ", "".join(parser.text)).strip()
    markers = re.compile(r"August\s+(?:[4-9]|1[0-9]),?\s+2025|2025-08-\d\d|\[v\d+\]|Submission history|Submitted on|gpt-oss.{0,70}(?:release|available)|releas.{0,90}gpt-oss|model card", re.I)
    spans = [(0, min(1500, len(text)))]
    for match in markers.finditer(text):
        start, end = max(0, match.start() - 180), min(len(text), match.end() + 300)
        spans.append((start, end))
    spans = sorted(spans)
    merged = []
    for start, end in spans:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    ld = []
    for script in parser.ld[:15]:
        try:
            ld.extend(date_fields(json.loads(script)))
        except (ValueError, TypeError):
            ld.append({"parse_status": "invalid_json"})
    return {"normalization": "HTML data text excluding script/style; Unicode whitespace collapsed; stripped",
            "normalized_text_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "normalized_text_chars": len(text),
            "spans": [{"start_char": s, "end_char": e, "text": text[s:e]} for s, e in merged[:30]],
            "metadata": parser.meta,
            "json_ld_fields": ld[:80],
            "artifact_links": [u for u in parser.links if any(x in u for x in ("model-card", "cdn.openai.com", "2508.10925"))][:30]}

def main():
    plan = json.loads((ROOT / "acquisition-plan.json").read_text())
    deadline = time.monotonic() + CYCLE_BUDGET
    cache, results = {}, []
    for source in plan["sources"]:
        host = source["allowed_host"]
        if host not in cache:
            cache[host] = get_robots(host, deadline)
        parser, base_robot = cache[host]
        robot = dict(base_robot)
        robot["allowed"] = base_robot["state"] == "missing" or (base_robot["state"] == "parsed" and parser.can_fetch(USER_AGENT, source["url"]))
        result = {"id": source["id"], "kind": source["kind"], "requested_url": source["url"], "observed_at": now(), "robots": robot}
        if not robot["allowed"]:
            result.update({"state": "not_fetched", "reason": "Robots unavailable or disallows fixed source path"})
        else:
            try:
                raw, metadata = fetch(source["url"], host, MAX_BYTES, deadline)
                if raw.startswith(b"%PDF-") or "application/pdf" in (metadata["content_type"] or ""):
                    raise ValueError("PDF response outside metadata-only scope")
                result.update({"state": "observed", "response": metadata, "bytes": len(raw), "received_byte_sha256": hashlib.sha256(raw).hexdigest()})
                if source["kind"] == "archive_index_only":
                    rows = json.loads(raw)
                    if not isinstance(rows, list) or len(rows) > 26:
                        raise ValueError("Archive index outside bounded row shape")
                    result["archive_index"] = rows
                    result["interpretation"] = "Capture index only; no replayed bytes acquired or edition inferred"
                else:
                    result["extraction"] = extract_html(raw)
            except urllib.error.HTTPError as exc:
                result.update({"state": "not_fetched", "http_status": exc.code, "reason": str(exc)})
            except Exception as exc:
                result.update({"state": "not_fetched", "reason": type(exc).__name__ + ": " + str(exc)})
        results.append(result)
    receipt = {"schema_version": 1, "authorship": plan["authorship"],
               "method": {"collector": "collect.py", "python": sys.version.split()[0], "max_bytes": MAX_BYTES,
                          "socket_timeout_seconds": SOCKET_TIMEOUT, "request_budget_seconds": REQUEST_BUDGET,
                          "cycle_budget_seconds": CYCLE_BUDGET, "max_redirects": MAX_REDIRECTS,
                          "scope": "Selected current HTML metadata/text and optional archive index; no PDF or historical replay bytes"},
               "execution": {"source_commit": os.getenv("GITHUB_SHA"), "run_id": os.getenv("GITHUB_RUN_ID"), "job_name": os.getenv("GITHUB_JOB"), "collected_at": now()},
               "sources": results}
    print("RELEASE_TIMING_RECEIPT_JSON_BEGIN")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    print("RELEASE_TIMING_RECEIPT_JSON_END")

if __name__ == "__main__":
    main()
