#!/usr/bin/env python3
"""Produced by OpenAI Codex (AI agent, GPT-6); offline source-boundary regressions."""
import contextlib, importlib.util, io, json, os
from pathlib import Path
import tempfile, unittest
from unittest.mock import patch
import urllib.error
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject,NameObject,TextStringObject,RectangleObject

spec=importlib.util.spec_from_file_location("rsp_collect",Path(__file__).with_name("collect.py"))
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
URL="https://www.anthropic.com/responsible-scaling-policy"
PDF="https://www-cdn.anthropic.com/policy.pdf"
class Response:
    status=200;url=URL
    def __init__(self,raw,mime):self.data=io.BytesIO(raw);self.headers={"Content-Type":mime}
    def read(self,n):return self.data.read(n)
    def __enter__(self):return self
    def __exit__(self,*a):return False
def page(anchor,href=PDF):
    p=c.PolicyPage();p.feed('<a href="'+href+'">'+anchor+'</a>');return p
def synthetic_card(pages=124):
    w=PdfWriter()
    for _ in range(pages):w.add_blank_page(width=100,height=100)
    if pages>10:
        for n,u in[(0,URL),(8,URL),(9,"https://example.org/responsible-scaling-policy")]:
            a=DictionaryObject({NameObject("/Type"):NameObject("/Annot"),NameObject("/Subtype"):NameObject("/Link"),
                NameObject("/Rect"):RectangleObject([1,2,3,4]),
                NameObject("/A"):DictionaryObject({NameObject("/S"):NameObject("/URI"),NameObject("/URI"):TextStringObject(u)})})
            w.add_annotation(page_number=n,annotation=a)
    b=io.BytesIO();w.write(b);return b.getvalue()
class Tests(unittest.TestCase):
    def test_usage_policy_counterexample_is_not_rsp(self):
        candidates,explicit=c.select_policy_links(page("Claude 4 usage policy version 2025"),URL)
        self.assertEqual(candidates,[]);self.assertEqual(explicit,[])
    def test_generic_policy_not_rsp(self):
        self.assertEqual(c.select_policy_links(page("Claude 4 policy version 2025 applicable to release"),URL),([],[]))
    def test_rsp_chronology_only_does_not_bind_card(self):
        candidates,explicit=c.select_policy_links(page("RSP version2.2 May2025"),URL)
        self.assertEqual(len(candidates),1);self.assertEqual(explicit,[])
    def test_rsp_model_and_date_without_relation_not_bound(self):
        candidates,explicit=c.select_policy_links(page("RSP version 2.2 Claude 4 2025"),URL)
        self.assertEqual(len(candidates),1);self.assertEqual(explicit,[])
    def test_explicit_rsp_model_version_applicability_candidate(self):
        candidates,explicit=c.select_policy_links(page("Responsible Scaling Policy version 2.2 governing Claude Opus 4 May2025"),URL)
        self.assertEqual(len(candidates),1);self.assertEqual(explicit,candidates)
    def test_newer_claude4_5_not_scoped(self):
        _,explicit=c.select_policy_links(page("RSP version 2.2 applicable to Claude 4.5 in2025"),URL)
        self.assertEqual(explicit,[])
    def test_off_provider_policy_link_not_candidate(self):
        self.assertEqual(c.select_policy_links(page("RSP version 2.2 applicable to Claude4 in2025","https://example.org/rsp.pdf"),URL),([],[]))
    def test_pdf_mime_larger_than_html_cap_uses_pdf_cap(self):
        raw=b"%PDF-"+b"x"*(c.HTML_LIMIT+1);response=Response(raw,"application/pdf")
        with patch.object(c.OPENER,"open",return_value=response):got,meta=c.get_raw(URL)
        self.assertEqual(got,raw);self.assertEqual(meta["applied_byte_limit"],c.PDF_LIMIT)
    def test_pdf_magic_larger_than_html_cap_uses_pdf_cap(self):
        raw=b"%PDF-"+b"x"*(c.HTML_LIMIT+1);response=Response(raw,"application/octet-stream")
        with patch.object(c.OPENER,"open",return_value=response):got,meta=c.get_raw(URL)
        self.assertEqual(got,raw);self.assertEqual(meta["applied_byte_limit"],c.PDF_LIMIT)
    def test_html_cap_not_relaxed(self):
        with patch.object(c.OPENER,"open",return_value=Response(b"x"*(c.HTML_LIMIT+1),"text/html")):
            with self.assertRaises(ValueError):c.get_raw(URL)
    def test_pdf_cap_not_relaxed(self):
        with patch.object(c.OPENER,"open",return_value=Response(b"%PDF-"+b"x"*c.PDF_LIMIT,"application/pdf")):
            with self.assertRaises(ValueError):c.get_raw(URL)
    def test_pdf_mime_masquerading_html_rejected(self):
        with patch.object(c.OPENER,"open",return_value=Response(b"<html>fakePDF</html>","application/pdf")):
            with self.assertRaises(ValueError):c.get_raw(URL)
    def test_robots_limit_independent_of_pdf_magic(self):
        with patch.object(c.OPENER,"open",return_value=Response(b"%PDF-"+b"x"*c.ROBOTS_LIMIT,"application/pdf")):
            with self.assertRaises(ValueError):c.get_raw(URL,robots=True)
    def test_reused_card_wrong_hash_refused_before_parse(self):
        with self.assertRaisesRegex(ValueError,"previously acquired"):c.card_pointers(b"%PDF-not-original")
    def test_real_pdf_annotation_scope_and_identity(self):
        raw=synthetic_card()
        with patch.object(c,"CARD_SHA",c.digest(raw)):got=c.card_pointers(raw)
        self.assertEqual(len(got),1);self.assertEqual(got[0]["pdf_page"],9);self.assertEqual(got[0]["uri"],URL)
        self.assertEqual(got[0]["annotation_rectangle"],[1.0,2.0,3.0,4.0])
    def test_reused_pdf_wrong_page_count_refused(self):
        raw=synthetic_card(1)
        with patch.object(c,"CARD_SHA",c.digest(raw)):
            with self.assertRaisesRegex(ValueError,"page count"):c.card_pointers(raw)
    def test_no_fresh_source_request_when_reused_card_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);(p/"acquisition-plan.json").write_text(json.dumps({"authorship":{},"official_policy_route":URL}))
            with patch.object(c,"ROOT",p),patch.dict(os.environ,{"RUNNER_TEMP":temp,"REUSED_CARD_DIR":temp}),patch.object(c,"acquire") as get,contextlib.redirect_stdout(io.StringIO()):
                c.main()
            get.assert_not_called();r=json.loads((p/"rsp-version-acquisition.json").read_text())
            self.assertEqual(r["reused_card"]["state"],"not_verified");self.assertEqual(r["sources"],[])
    def test_robots_denial_prevents_source_get(self):
        with patch.object(c,"robots",return_value={"allowed":False}),patch.object(c,"get_raw") as get:
            with self.assertRaises(PermissionError):c.acquire(URL)
            get.assert_not_called()
    def test_redirect_checks_target_robots(self):
        events=[]
        def robots(u):events.append(("robots",u));return {"allowed":True}
        def get(u):
            events.append(("get",u))
            if u==URL:raise urllib.error.HTTPError(u,307,"redirect",{"Location":PDF},None)
            return b"%PDF-x",{"status":200,"final_url":PDF}
        with patch.object(c,"robots",side_effect=robots),patch.object(c,"get_raw",side_effect=get):c.acquire(URL)
        self.assertEqual(events,[("robots",URL),("get",URL),("robots",PDF),("get",PDF)])
    def test_off_provider_redirect_refused(self):
        def get(u):raise urllib.error.HTTPError(u,307,"redirect",{"Location":"https://example.org/rsp.pdf"},None)
        with patch.object(c,"robots",return_value={"allowed":True}),patch.object(c,"get_raw",side_effect=get) as fetch:
            with self.assertRaises(ValueError):c.acquire(URL)
            self.assertEqual(fetch.call_count,1)
    def test_hard_deadline_bypasses_exception_catches_preserves_receipt(self):
        raw=synthetic_card()
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);(p/"anthropic-card.pdf").write_bytes(raw);(p/"acquisition-plan.json").write_text(json.dumps({"authorship":{},"official_policy_route":URL}))
            with patch.object(c,"ROOT",p),patch.object(c,"CARD_SHA",c.digest(raw)),patch.dict(os.environ,{"RUNNER_TEMP":temp,"REUSED_CARD_DIR":temp}),patch.object(c,"acquire",side_effect=c.CycleDeadline("stop")),contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(c.CycleDeadline):c.main()
            self.assertTrue((p/"rsp-version-acquisition.json").is_file())
    def test_url_credentials_and_non_https_refused(self):
        for u in["http://www.anthropic.com/rsp","https://u:p@www.anthropic.com/rsp","https://www.anthropic.com:8443/rsp"]:
            with self.assertRaises(ValueError):c.safe_url(u)
if __name__=="__main__":unittest.main(verbosity=2)
