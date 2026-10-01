import unittest
from german_legal_engine.subsumption import analyze_subsumption
from german_legal_engine.sanitizer import sanitize_zero_dashes

class TestSubsumption(unittest.TestCase):
    def test_subsumption_bgb_823(self):
        res = analyze_subsumption("BGB", "823")
        self.assertTrue(res["success"])
        bp = res["blueprint"]
        self.assertEqual(bp["norm"], "§ 823 Abs. 1 BGB")
        self.assertGreaterEqual(len(bp["tatbestandsmerkmale"]), 5)
        merkmale = [m["merkmal"] for m in bp["tatbestandsmerkmale"]]
        self.assertTrue(any("Rechtsgut" in m for m in merkmale))
        self.assertTrue(any("Kausalität" in m for m in merkmale))

    def test_zero_dashes(self):
        raw = "Das Urteil — Az. VIII ZR 125/22 – mit Leitsatz"
        clean = sanitize_zero_dashes(raw)
        self.assertNotIn("—", clean)
        self.assertNotIn("–", clean)
        self.assertEqual(clean, "Das Urteil, Az. VIII ZR 125/22, mit Leitsatz")

if __name__ == "__main__":
    unittest.main()
