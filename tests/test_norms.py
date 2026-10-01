import unittest
from german_legal_engine.norms import COMMON_LAW_SLUGS, fetch_statute_norm

class TestNorms(unittest.TestCase):
    def test_slug_mappings(self):
        # Critical slugs that previously caused 404
        self.assertEqual(COMMON_LAW_SLUGS["aufenthg"], "aufenthg_2004")
        self.assertEqual(COMMON_LAW_SLUGS["owig"], "owig_1968")
        self.assertEqual(COMMON_LAW_SLUGS["vvg"], "vvg_2008")
        self.assertEqual(COMMON_LAW_SLUGS["bgb"], "bgb")
        self.assertEqual(COMMON_LAW_SLUGS["zpo"], "zpo")

    def test_live_statute_fetch(self):
        res = fetch_statute_norm("BGB", "823")
        self.assertTrue(res["success"])
        self.assertEqual(res["title"], "Schadensersatzpflicht")
        self.assertIn("Leben, den Körper, die Gesundheit", res["content_clean"])
        # Ensure umlauts are preserved
        self.assertIn("vorsätzlich", res["content_clean"])
        # Ensure zero-dashes compliance
        self.assertNotIn("—", res["content_clean"])

if __name__ == "__main__":
    unittest.main()
