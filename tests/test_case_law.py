import unittest
from german_legal_engine.case_law import search_case_law, get_decision_text
from german_legal_engine.bayern import search_bayern_court_decisions

class TestCaseLaw(unittest.TestCase):
    def test_bayern_search(self):
        res = search_bayern_court_decisions("Mietkaution", limit=2)
        self.assertIsInstance(res, list)
        if res and "error" not in res[0]:
            first = res[0]
            self.assertEqual(first["jurisdiction"], "BY")
            self.assertTrue(first["doc_id"].startswith("Y-"))
            self.assertIn("Az.", first["citation"])
            self.assertNotIn("—", first["title"])

    def test_federal_search(self):
        res = search_case_law("Mietkaution", limit=2, source="BUND")
        self.assertIsInstance(res, list)
        if res and "error" not in res[0]:
            first = res[0]
            self.assertEqual(first["jurisdiction"], "BUND")
            self.assertIn("Az.", first["citation"])

    def test_all_search_routing(self):
        res = search_case_law("Mietvertrag", limit=4, source="ALL")
        self.assertIsInstance(res, list)
        self.assertGreater(len(res), 0)

if __name__ == "__main__":
    unittest.main()
