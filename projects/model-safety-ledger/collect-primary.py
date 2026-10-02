#!/usr/bin/env python3
"""AI-authored bounded primary-document acquisition; no inference and no repo writes."""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone

import pypdf

ROOT = Path(__file__).resolve().parent
USER_AGENT = "AlignmentArtifactLedger/0.1 (+https://github.com/trimcrae/Alignment)"
MAX_BYTES = 16 * 1024 * 1024
MAX_ROBOTS_BYTES = 512 * 1024
TIMEOUT = 25
MARKERS = re.compile(
    r"indicative thresholds|Safety Advisory Group|Tracked Categories|"
    r"(?:does not|do not|did not|not) (?:reach|meet|achieve)|"
    r"below.{0,50}(?:High|threshold)|High capability|"
    r"gpt-oss-20b.{0,80}(?:risk|evaluat)|external expert",
    re.IGNORECASE,
)

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

class SameHostRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, host):
        super().__init__()
        self.host = host

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urllib.parse.urlsplit(newurl)
        if parsed.scheme != "https" or parsed.hostname != self.host:
            raise ValueError("Redirect leaves the explicitly allowed HTTPS source host")
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def fetch(url, host, limit):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != host or parsed.username or parsed.password:
        raise ValueError("URL is outside the fixed HTTPS source host")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    opener = urllib.request.build_opener(SameHostRedirect(host))
    with opener.open(request, timeout=TIMEOUT) as response:
        raw = response.read(limit + 1)
        if len(raw) > limit:
            raise ValueError("Response exceeded the bounded byte limit")
        return raw, {
            "status": response.status,
            "final_url": response.url,
            "content_type": response.headers.get("Content-Type"),
            "last_modified": response.headers.get("Last-Modified"),
            "etag": response.headers.get("ETag"),
        }

def robots(source):
    url = "https://" + source["allowed_host"] + "/robots.txt"
    result = {"url": url, "user_agent": USER_AGENT}
    try:
        raw, metadata = fetch(url, source["allowed_host"], MAX_ROBOTS_BYTES)
        parser = urllib.robotparser.RobotFileParser(url)
        parser.parse(raw.decode("utf-8", errors="replace").splitlines())
        result.update({"status": metadata["status"], "sha256": hashlib.sha256(raw).hexdigest(),
                       "allowed": parser.can_fetch(USER_AGENT, source["url"])})
    except urllib.error.HTTPError as exc:
        # A missing robots file is explicitly distinguishable from a blocked request.
        result.update({"status": exc.code, "allowed": exc.code in (404, 410)})
    except Exception as exc:
        result.update({"status": None, "allowed": False, "error": type(exc).__name__ + ": " + str(exc)})
    return result

def extract(reader):
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = re.sub(r"\s+", " ", page.extract_text() or "").strip()
        intervals = [(0, min(len(text), 2200))] if i == 1 else []
        for match in MARKERS.finditer(text):
            start, end = max(0, match.start() - 400), min(len(text), match.end() + 850)
            if intervals and start <= intervals[-1][1]:
                intervals[-1] = (intervals[-1][0], max(intervals[-1][1], end))
            else:
                intervals.append((start, end))
        if intervals:
            pages.append({
                "pdf_page": i,
                "printed_page_label": None,
                "normalized_page_text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "normalization": "Unicode whitespace collapsed to one ASCII space; stripped",
                "spans": [{"start_char": start, "end_char": end, "text": text[start:end]} for start, end in intervals],
            })
    return pages

def main():
    plan = json.loads((ROOT / "acquisition-plan.json").read_text(encoding="utf-8"))
    results = []
    for source in plan["sources"]:
        result = {"id": source["id"], "kind": source["kind"], "requested_url": source["url"],
                  "observed_at": now(), "robots": robots(source)}
        if not result["robots"]["allowed"]:
            result.update({"state": "not_fetched", "reason": "robots unavailable or disallows this user agent/path"})
            results.append(result)
            continue
        try:
            raw, metadata = fetch(source["url"], source["allowed_host"], MAX_BYTES)
            if not raw.startswith(b"%PDF-"):
                raise ValueError("Response is not a PDF")
            reader = pypdf.PdfReader(io.BytesIO(raw), strict=True)
            if reader.is_encrypted or not 1 <= len(reader.pages) <= 200:
                raise ValueError("Encrypted PDF or unsupported page count")
            result.update({"state": "observed", "response": metadata, "bytes": len(raw),
                           "sha256": hashlib.sha256(raw).hexdigest(), "pdf_pages": len(reader.pages),
                           "metadata_title": str(reader.metadata.title) if reader.metadata and reader.metadata.title else None,
                           "excerpts": extract(reader)})
        except Exception as exc:
            result.update({"state": "not_fetched", "reason": type(exc).__name__ + ": " + str(exc)})
        results.append(result)
    receipt = {
        "schema_version": 1,
        "authorship": plan["authorship"],
        "method": {"collector": "collect-primary.py", "python": sys.version.split()[0], "pypdf": pypdf.__version__,
                   "max_document_bytes": MAX_BYTES, "timeout_seconds": TIMEOUT,
                   "scope": "Selected mechanically extracted page spans; not a complete document transcript"},
        "execution": {"source_commit": os.environ.get("GITHUB_SHA"), "run_id": os.environ.get("GITHUB_RUN_ID"),
                      "job_name": os.environ.get("GITHUB_JOB"), "collected_at": now()},
        "sources": results,
    }
    # No committed path is touched. Logs are the reviewable recovery channel.
    print("MODEL_SAFETY_RECEIPT_JSON_BEGIN")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    print("MODEL_SAFETY_RECEIPT_JSON_END")
    if not any(source["state"] == "observed" for source in results):
        raise SystemExit("No primary document could be acquired; preserve unknowns")
if __name__ == "__main__":
    main()
