import unittest
from german_legal_engine.case_law import search_case_law, get_decision_text
from german_legal_engine.bayern import search_bayern_court_decisions

class TestCaseLaw(unittest.TestCase):
    def test_bayern_search(self):
        res = search_bayern_court_decisions("Mietkaution", limit=2)
        self.assertIsInstance(res, list)
        if not res or (isinstance(res[0], dict) and "error" in res[0]):
            self.skipTest("Bavarian court portal unavailable or rate-limited from this network environment")
        first = res[0]
        self.assertEqual(first["jurisdiction"], "BY")
        self.assertTrue(first["doc_id"].startswith("Y-"))
        self.assertIn("Az.", first["citation"])
        self.assertNotIn("—", first["title"])
        self.assertIn("source_name", first)
        self.assertIn("retrieved_at", first)

    def test_federal_search(self):
        res = search_case_law("Mietkaution", limit=2, source="BUND")
        self.assertIsInstance(res, list)
        if not res or (isinstance(res[0], dict) and "error" in res[0]):
            self.skipTest("Federal RII portal unavailable from this network environment")
        first = res[0]
        self.assertEqual(first["jurisdiction"], "BUND")
        self.assertIn("Az.", first["citation"])
        self.assertIn("source_name", first)
        self.assertIn("retrieved_at", first)

    def test_all_search_routing(self):
        res = search_case_law("Mietvertrag", limit=4, source="ALL")
        self.assertIsInstance(res, list)
        if not res or (isinstance(res[0], dict) and "error" in res[0]):
            self.skipTest("Portals unavailable from this network environment")
        self.assertGreater(len(res), 0)

if __name__ == "__main__":
    unittest.main()
