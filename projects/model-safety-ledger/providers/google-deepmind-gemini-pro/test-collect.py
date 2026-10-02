#!/usr/bin/env python3
"""AI-authored OpenAI Codex/GPT-6: meaningful network-free source boundary regressions."""
import contextlib,gzip,importlib.util,io,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("collector",ROOT/"collect.py")
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
BASE="https://deepmind.google/models/gemini/pro/"
CARD="https://storage.googleapis.com/deepmind-media/model-card.pdf"
def page(html):
    p=c.Landing();p.feed(html);return p
class Boundary(unittest.TestCase):
    def test_official_host(self):self.assertEqual(c.safe_url(BASE).hostname,"deepmind.google")
    def test_storage_bucket(self):self.assertEqual(c.safe_url(CARD).hostname,"storage.googleapis.com")
    def test_other_bucket(self):
        with self.assertRaises(ValueError):c.safe_url("https://storage.googleapis.com/other/card.pdf")
    def test_other_host(self):
        with self.assertRaises(ValueError):c.safe_url("https://example.org/model-card.pdf")
    def test_http(self):
        with self.assertRaises(ValueError):c.safe_url(BASE.replace("https:","http:"))
    def test_credentials(self):
        with self.assertRaises(ValueError):c.safe_url("https://user:pass@deepmind.google/models/")
    def test_port(self):
        with self.assertRaises(ValueError):c.safe_url("https://deepmind.google:444/models/")
    def test_encoded_traversal(self):
        with self.assertRaises(ValueError):c.safe_url("https://storage.googleapis.com/deepmind-media/%2e%2e/other/card.pdf")
    def test_explicit_anchor(self):
        self.assertEqual(c.card_candidates(page('<a href="'+CARD+'">Model Card</a>'),BASE)[0]["url"],CARD)
    def test_aria_label(self):
        self.assertEqual(len(c.card_candidates(page('<a href="'+CARD+'" aria-label="Model card">Download</a>'),BASE)),1)
    def test_technical_report_not_card(self):
        self.assertEqual(c.card_candidates(page('<a href="'+CARD+'">Technical report</a>'),BASE),[])
    def test_other_bucket_not_candidate(self):
        self.assertEqual(c.card_candidates(page('<a href="https://storage.googleapis.com/other/card.pdf">Model Card</a>'),BASE),[])
    def test_identity_html(self):
        raw=b"<html>Gemini example</html>";body,m=c.decode_entity(raw,{"content_type":"text/html"})
        self.assertEqual(body,raw);self.assertEqual(m["encoding_basis"],"identity")
    def test_gzip_header_missing_but_magic(self):
        raw=gzip.compress(b'<a href="'+CARD.encode()+b'">Model Card</a>')
        body,m=c.decode_entity(raw,{"content_type":"text/html"})
        self.assertEqual(len(c.card_candidates(page(body.decode()),BASE)),1);self.assertEqual(m["encoding_basis"],"gzip_magic")
        self.assertIsNone(m["content_encoding_header"])
    def test_gzip_header(self):
        self.assertEqual(c.decode_entity(gzip.compress(b"abc"),{"content_type":"text/html","content_encoding":"gzip"})[0],b"abc")
    def test_gzip_header_bad_magic(self):
        with self.assertRaises(ValueError):c.decode_entity(b"abc",{"content_type":"text/html","content_encoding":"gzip"})
    def test_unsupported_encoding(self):
        with self.assertRaises(ValueError):c.decode_entity(b"abc",{"content_type":"text/html","content_encoding":"br"})
    def test_gzip_html_bomb_bound(self):
        with patch.object(c,"HTML_LIMIT",128):
            with self.assertRaises(ValueError):c.decode_entity(gzip.compress(b"a"*129),{"content_type":"text/html"})
    def test_decoded_robots_bound(self):
        with self.assertRaises(ValueError):c.decode_entity(gzip.compress(b"a"*129),{"content_type":"text/plain"},128)
    def test_pdf_magic_gets_pdf_limit(self):
        with patch.object(c,"HTML_LIMIT",128),patch.object(c,"PDF_LIMIT",512):
            raw=b"%PDF-"+b"x"*200;body,m=c.decode_entity(raw,{"content_type":"application/octet-stream"})
            self.assertEqual(body,raw);self.assertEqual(m["applied_decoded_byte_limit"],512)
    def test_pdf_mime_magic_required(self):
        with self.assertRaises(ValueError):c.decode_entity(b"not pdf",{"content_type":"application/pdf"})
    def test_gzip_pdf_limit(self):
        with patch.object(c,"HTML_LIMIT",128),patch.object(c,"PDF_LIMIT",512):
            body,m=c.decode_entity(gzip.compress(b"%PDF-"+b"x"*200),{"content_type":"application/pdf"})
            self.assertEqual(len(body),205);self.assertEqual(m["applied_decoded_byte_limit"],512)
    def test_pdf_limit_exceeded(self):
        with patch.object(c,"PDF_LIMIT",128):
            with self.assertRaises(ValueError):c.decode_entity(gzip.compress(b"%PDF-"+b"x"*124),{"content_type":"application/pdf"})
    def test_gzip_pdf_through_actual_encoded_reader(self):
        entity=b"%PDF-"+b"x"*(2*1024*1024+1);raw=gzip.compress(entity)
        class Response(io.BytesIO):
            headers={"Content-Type":"application/pdf","Content-Encoding":"gzip"};status=200;url=CARD
        class Opener:
            def open(self,*a,**k):return Response(raw)
        with patch.object(c,"OPENER",Opener()):
            received,meta=c.get_raw(CARD)
            self.assertEqual(received,raw);self.assertEqual(meta["applied_byte_limit"],c.PDF_LIMIT)
            decoded,interp=c.decode_entity(received,meta)
            self.assertEqual(decoded,entity);self.assertEqual(interp["content_encoding_header"],"gzip")
    def test_forced_html_received_cap(self):
        class Response(io.BytesIO):
            headers={"Content-Type":"application/pdf"};status=200;url=BASE
        class Opener:
            def open(self,*a,**k):return Response(b"%PDF-"+b"x"*124)
        with patch.object(c,"OPENER",Opener()):
            with self.assertRaises(ValueError):c.get_raw(BASE,limit_override=128)
    def test_deadline_bypasses_exception(self):self.assertFalse(issubclass(c.CycleDeadline,Exception))
    def test_received_pdf_saved_before_parse_failure(self):
        html=('<a href="'+CARD+'">Model Card</a>').encode();pdf=b"%PDF-retained-but-parser-fails"
        meta={"status":200,"final_url":BASE,"content_type":"text/html"}
        rr={"allowed":True}
        def acquire(u):
            if u==BASE:return html,meta,rr
            if u==CARD:return pdf,{**meta,"final_url":CARD,"content_type":"application/pdf"},rr
            raise AssertionError("Unexpected source")
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{"RUNNER_TEMP":tmp,"GITHUB_SHA":"test","GITHUB_RUN_ID":"test","GITHUB_JOB":"test"}),patch.object(c,"acquire",side_effect=acquire),patch.object(c,"robots_for",return_value=rr),patch.object(c,"excerpts",side_effect=ValueError("synthetic extraction failure")),contextlib.redirect_stdout(io.StringIO()):
            c.main();out=Path(tmp)/"google-primary-source";r=json.loads((out/"acquisition.json").read_text())
            self.assertEqual((out/"model-card.pdf").read_bytes(),pdf)
            self.assertEqual(r["sources"][1]["state"],"received_uninterpreted")
            self.assertEqual(r["sources"][1]["sha256"],c.sha(pdf));self.assertEqual(r["selection"]["status"],"unknown")
if __name__=="__main__":unittest.main(verbosity=2)
