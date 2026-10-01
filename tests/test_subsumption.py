import unittest
from german_legal_engine.subsumption import analyze_subsumption
from german_legal_engine.sanitizer import sanitize_zero_dashes, format_court_citation

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

    def test_subsumption_bgb_280(self):
        res = analyze_subsumption("BGB", "280")
        self.assertTrue(res["success"])
        bp = res["blueprint"]
        self.assertIn("Pflichtverletzung", bp["title"])
        merkmale = [m["merkmal"] for m in bp["tatbestandsmerkmale"]]
        self.assertTrue(any("Schuldverhältnis" in m for m in merkmale))

    def test_subsumption_bgb_626(self):
        res = analyze_subsumption("BGB", "626")
        self.assertTrue(res["success"])
        bp = res["blueprint"]
        self.assertIn("fristlose Kündigung", bp["title"])
        merkmale = [m["merkmal"] for m in bp["tatbestandsmerkmale"]]
        self.assertTrue(any("Zwei-Wochen-Ausschlussfrist" in m for m in merkmale))

    def test_zero_dashes_replaces_dashes(self):
        raw = "Das Urteil — Az. VIII ZR 125/22 – mit Leitsatz - weiterer Zusatz"
        clean = sanitize_zero_dashes(raw)
        self.assertNotIn("—", clean)
        self.assertNotIn("–", clean)
        self.assertEqual(clean, "Das Urteil, Az. VIII ZR 125/22, mit Leitsatz, weiterer Zusatz")

    def test_zero_dashes_preserves_paragraphs_and_ranges(self):
        multiline = "(1) Erste Bestimmung gem. §§ 187–193 BGB.\n\n(2) Zweite Bestimmung — mit Erläuterung."
        clean = sanitize_zero_dashes(multiline)
        self.assertIn("\n\n", clean)
        self.assertIn("187-193", clean)
        self.assertNotIn("—", clean)

    def test_court_citation_formatting(self):
        cit = format_court_citation("Bundesgerichtshof", "15.03.2023", "VIII ZR 125/22")
        self.assertEqual(cit, "BGH, Entscheidung vom 15.03.2023, Az. VIII ZR 125/22")

if __name__ == "__main__":
    unittest.main()
