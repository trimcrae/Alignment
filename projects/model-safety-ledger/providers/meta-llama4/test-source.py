#!/usr/bin/env python3
"""AI-authored OpenAI Codex/GPT-6: UTF8/provenance fixtures, no model evaluation."""
import importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("source_verify",ROOT/"verify-source.py")
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class ByteQuotes(unittest.TestCase):
    def test_actual_owned_bundle(self):self.assertEqual(v.verify()["literal_UTF8_byte_quotes"],14)
    def test_actual_nonascii_offset(self):
        raw=(ROOT/"evidence/MODEL_CARD.md").read_bytes();qs=json.loads((ROOT/"evidence/citations.json").read_text())["citations"]
        q=next(x for x in qs if x["id"]=="model_maverick");v.check_quote(raw,q)
        self.assertNotEqual(q["start_byte"],raw.decode().index(q["quote"]))
    def test_shifted_both_coordinates(self):
        raw=(ROOT/"evidence/MODEL_CARD.md").read_bytes();q={"start_byte":1576,"end_byte":1603,"quote":"Llama 4 Maverick (17Bx128E)"}
        with self.assertRaises(ValueError):v.check_quote(raw,q)
    def test_boolean_coordinate_rejected(self):
        with self.assertRaises(ValueError):v.check_quote(b"ab",{"start_byte":False,"end_byte":1,"quote":"a"})
    def test_negative_coordinate_rejected(self):
        with self.assertRaises(ValueError):v.check_quote(b"ab",{"start_byte":-1,"end_byte":1,"quote":"a"})
    def test_fractional_coordinate_rejected(self):
        with self.assertRaises(ValueError):v.check_quote(b"ab",{"start_byte":0.5,"end_byte":1,"quote":"a"})
    def test_out_of_bounds_rejected(self):
        with self.assertRaises(ValueError):v.check_quote(b"ab",{"start_byte":0,"end_byte":3,"quote":"ab"})
    def test_nonbmp_byte_coordinate(self):
        raw="🌌Meta".encode();v.check_quote(raw,{"start_byte":4,"end_byte":8,"quote":"Meta"})
    def test_character_offset_is_not_byte_offset(self):
        with self.assertRaises(ValueError):v.check_quote("🌌Meta".encode(),{"start_byte":1,"end_byte":5,"quote":"Meta"})
    def test_wrong_quote(self):
        with self.assertRaises(ValueError):v.check_quote(b"Meta",{"start_byte":0,"end_byte":4,"quote":"Meto"})
if __name__=="__main__":unittest.main(verbosity=2)
