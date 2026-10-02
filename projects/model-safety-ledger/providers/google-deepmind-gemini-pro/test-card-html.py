#!/usr/bin/env python3
"""AI-authored OpenAI Codex/GPT-6: synthetic exact-stage fixtures, not scientific evidence."""
import contextlib,importlib.util,io,json,os,tempfile,unittest,urllib.error
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("cardcollector",ROOT/"collect-card-html.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
URL="https://deepmind.google/models/model-cards/gemini-3-1-pro"
class CardStage(unittest.TestCase):
    def execute(self,raw,mime="text/html"):
        calls=[]
        def get(u,robots=False,limit_override=None):
            calls.append((u,robots,limit_override))
            return raw,{"status":200,"final_url":u,"content_type":mime,"applied_byte_limit":2097152,"content_encoding":None}
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{"RUNNER_TEMP":tmp}),patch.object(m.c,"get_raw",side_effect=get),contextlib.redirect_stdout(io.StringIO()):
            m.main();out=Path(tmp)/"google-html-card"
            r=json.loads((out/"card-acquisition.json").read_text())
            self.assertEqual((out/"card-response.bin").read_bytes(),raw)
        self.assertEqual(calls,[(URL,False,2097152)]);return r
    def test_exact_html_and_no_child_following(self):
        raw=b'<html><title>Synthetic card fixture</title><body>Gemini fixture Frontier Safety Framework <a href="https://example.org/child.pdf">child</a></body></html>'
        r=self.execute(raw);self.assertEqual(r["source"]["state"],"observed_html_card")
        self.assertEqual(r["method"]["source_requests"],1);self.assertEqual(r["source"]["title"],"Synthetic card fixture")
    def test_received_pdf_is_retained_but_not_parsed(self):
        r=self.execute(b"%PDF-synthetic","application/pdf")
        self.assertEqual(r["source"]["state"],"received_uninterpreted")
        self.assertIn("requires an HTML card",r["source"]["reason"])
    def test_bad_utf8_retained(self):
        r=self.execute(b"<html>\xff</html>");self.assertEqual(r["source"]["state"],"received_uninterpreted")
        self.assertIn("UnicodeDecodeError",r["source"]["reason"])
    def test_redirect_refused_without_following(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{"RUNNER_TEMP":tmp}),patch.object(m.c,"get_raw",side_effect=urllib.error.HTTPError(URL,302,"redirect",{"Location":"https://example.org/"},None)) as get,contextlib.redirect_stdout(io.StringIO()):
            m.main();r=json.loads((Path(tmp)/"google-html-card/card-acquisition.json").read_text())
            self.assertEqual(get.call_count,1);self.assertEqual(r["source"]["state"],"not_fetched")
            self.assertFalse((Path(tmp)/"google-html-card/card-response.bin").exists())
    def test_deadline_not_swallowed_and_receipt_retained(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{"RUNNER_TEMP":tmp}),patch.object(m.c,"get_raw",side_effect=m.c.CycleDeadline("synthetic deadline")),contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(m.c.CycleDeadline):m.main()
            r=json.loads((Path(tmp)/"google-html-card/card-acquisition.json").read_text())
            self.assertEqual(r["method"]["source_requests"],1)
if __name__=="__main__":unittest.main(verbosity=2)
