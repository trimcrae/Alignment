#!/usr/bin/env python3
"""Produced by OpenAI Codex (AI agent, GPT-6); offline collector regressions only."""
import contextlib, importlib.util, io, json, os
from pathlib import Path
import tempfile, unittest
from unittest.mock import patch
import urllib.error

spec=importlib.util.spec_from_file_location("anthropic_collect",Path(__file__).with_name("collect.py"))
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
class FakeResponse:
    status=200
    url="https://www.anthropic.com/news/claude-4"
    headers={"Content-Type":"text/html"}
    def __init__(self,data): self.stream=io.BytesIO(data)
    def read(self,n): return self.stream.read(n)
    def __enter__(self): return self
    def __exit__(self,*args): return False
class CollectorTests(unittest.TestCase):
    def main_receipt(self,sources,fetch,extract=None):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);(p/"acquisition-plan.json").write_text(json.dumps({"authorship":{"agent":"OpenAI Codex","human_review":"not_performed"},"sources":sources}))
            with patch.object(c,"ROOT",p),patch.dict(os.environ,{"RUNNER_TEMP":temp}),patch.object(c,"acquire",side_effect=fetch),contextlib.redirect_stdout(io.StringIO()):
                if extract is None:c.main()
                else:
                    with patch.object(c,"pdf_excerpts",return_value=extract):c.main()
            return json.loads((p/"anthropic-acquisition.json").read_text())
    def test_direct_pdf_uses_planned_pdf_limit_and_received_once(self):
        # The production pointer route must accept a legitimate PDF larger than2MiB.
        raw=b"%PDF-"+b"x"*(3*1024*1024);calls=[]
        url="https://www-cdn.anthropic.com/official.pdf"
        def fetch(u,limit):
            calls.append((u,limit))
            self.assertLessEqual(len(raw),limit)
            return raw,{"status":200,"final_url":url,"content_type":"application/pdf"},{"allowed":True}
        r=self.main_receipt([{"id":"claude-4-card-pointer","url":"https://www.anthropic.com/claude-4-system-card"}],fetch,(1,[]))
        self.assertEqual(calls,[("https://www.anthropic.com/claude-4-system-card",c.PDF_LIMIT)])
        self.assertEqual(r["selection"]["status"],"observed")
        self.assertEqual(r["sources"][1]["bytes"],len(raw))
        self.assertEqual(r["sources"][0]["sha256"],r["sources"][1]["sha256"])
    def test_html_page_retains_small_bound(self):
        calls=[]
        def fetch(u,limit):
            calls.append(limit);return b"<p>No unique system card pointer.</p>",{"status":200,"final_url":u},{"allowed":True}
        r=self.main_receipt([{"id":"claude-4-announcement","url":"https://www.anthropic.com/news/claude-4"}],fetch)
        self.assertEqual(calls,[c.PAGE_LIMIT]);self.assertEqual(r["selection"]["status"],"unknown")
        self.assertEqual(r["selection"]["candidate_urls"],[])
    def test_unique_explicit_provider_link_only(self):
        calls=[]
        def fetch(u,limit):
            calls.append(u)
            if u.endswith(".pdf"):return b"%PDF-synthetic",{"status":200,"final_url":u},{"allowed":True}
            raw=b'<a href="https://www-cdn.anthropic.com/card.pdf">Read the Claude4 system card</a><a href="https://example.org/card.pdf">system card</a>'
            return raw,{"status":200,"final_url":u},{"allowed":True}
        r=self.main_receipt([{"id":"claude-4-announcement","url":"https://www.anthropic.com/news/claude-4"}],fetch,(1,[]))
        self.assertEqual(calls,["https://www.anthropic.com/news/claude-4","https://www-cdn.anthropic.com/card.pdf"])
        self.assertEqual(r["selection"]["candidate_urls"],["https://www-cdn.anthropic.com/card.pdf"])
    def test_ambiguous_official_links_stop_without_pdf_fetch(self):
        calls=[]
        def fetch(u,limit):
            calls.append(u)
            return b'<a href="https://www-cdn.anthropic.com/a.pdf">system card</a><a href="https://www-cdn.anthropic.com/b.pdf">system card</a>',{"status":200,"final_url":u},{"allowed":True}
        r=self.main_receipt([{"id":"claude-4-announcement","url":"https://www.anthropic.com/news/claude-4"}],fetch)
        self.assertEqual(len(calls),1);self.assertEqual(r["selection"]["status"],"unknown")
    def test_external_url_rejected(self):
        with self.assertRaises(ValueError):c.allowed_url("https://example.org/card.pdf")
    def test_credentials_rejected(self):
        with self.assertRaises(ValueError):c.allowed_url("https://user:pass@www.anthropic.com/card.pdf")
    def test_non_https_rejected(self):
        with self.assertRaises(ValueError):c.allowed_url("http://www.anthropic.com/card.pdf")
    def test_nonstandard_port_rejected(self):
        with self.assertRaises(ValueError):c.allowed_url("https://www.anthropic.com:8443/card.pdf")
    def test_page_size_bound_enforced_by_actual_reader(self):
        response=FakeResponse(b"x"*(c.PAGE_LIMIT+1))
        with patch.object(c.OPENER,"open",return_value=response):
            with self.assertRaises(ValueError):c.raw_get(response.url,c.PAGE_LIMIT)
    def test_same_large_response_with_pdf_limit(self):
        data=b"x"*(c.PAGE_LIMIT+1);response=FakeResponse(data)
        with patch.object(c.OPENER,"open",return_value=response):
            raw,_=c.raw_get(response.url,c.PDF_LIMIT)
        self.assertEqual(raw,data)
    def test_denied_robots_prevents_get(self):
        with patch.object(c,"robots",return_value={"allowed":False}),patch.object(c,"raw_get") as fetch:
            with self.assertRaises(PermissionError):c.acquire("https://www.anthropic.com/news/claude-4",c.PAGE_LIMIT)
            fetch.assert_not_called()
    def test_redirect_checks_new_host_robots_before_get(self):
        trace=[];pdf="https://www-cdn.anthropic.com/card.pdf"
        def robots(u):trace.append(("robots",u));return {"allowed":True}
        def fetch(u,limit):
            trace.append(("get",u))
            if u!=pdf:raise urllib.error.HTTPError(u,307,"redirect",{"Location":pdf},None)
            return b"PDF",{"status":200,"final_url":pdf}
        with patch.object(c,"robots",side_effect=robots),patch.object(c,"raw_get",side_effect=fetch):
            c.acquire("https://www.anthropic.com/claude-4-system-card",c.PDF_LIMIT)
        self.assertEqual(trace,[("robots","https://www.anthropic.com/claude-4-system-card"),("get","https://www.anthropic.com/claude-4-system-card"),("robots",pdf),("get",pdf)])
    def test_redirect_to_external_host_refused(self):
        def fetch(u,limit):raise urllib.error.HTTPError(u,307,"redirect",{"Location":"https://example.org/card.pdf"},None)
        with patch.object(c,"robots",return_value={"allowed":True}),patch.object(c,"raw_get",side_effect=fetch) as f:
            with self.assertRaises(ValueError):c.acquire("https://www.anthropic.com/claude-4-system-card",c.PDF_LIMIT)
            self.assertEqual(f.call_count,1)
    def test_hard_stop_baseexception_not_swallowed_and_receipt_preserved(self):
        class Deadline(BaseException):pass
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);(p/"acquisition-plan.json").write_text(json.dumps({"authorship":{},"sources":[{"id":"claude-4-card-pointer","url":"https://www.anthropic.com/claude-4-system-card"}]}))
            with patch.object(c,"ROOT",p),patch.dict(os.environ,{"RUNNER_TEMP":temp}),patch.object(c,"acquire",side_effect=Deadline()),contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(Deadline):c.main()
            self.assertTrue((p/"anthropic-acquisition.json").is_file())
    def test_html_scripts_do_not_create_evidence_text(self):
        p=c.Page();p.feed("<script>ASL-3 invented</script><p>Actual release statement</p>")
        self.assertEqual(c.normalized(" ".join(p.text)),"Actual release statement")
if __name__=="__main__":unittest.main(verbosity=2)
