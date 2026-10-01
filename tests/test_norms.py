import unittest
from bs4 import BeautifulSoup
from german_legal_engine.norms import COMMON_LAW_SLUGS, fetch_statute_norm
from german_legal_engine.sanitizer import sanitize_zero_dashes

SAMPLE_JUR_ABSATZ_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="iso-8859-1"><title>§ 823 BGB</title></head>
<body>
<div class="jnheader"><h1>Bürgerliches Gesetzbuch<br><span class="jnenbez">§ 823</span> <span class="jnentitel">Schadensersatzpflicht</span></h1></div>
<div class="jnhtml">
  <div>
    <div class="jurAbsatz">(1) Wer vorsätzlich oder fahrlässig das Eigentum verletzt.</div>
    <div class="jurAbsatz">(2) Die gleiche Verpflichtung trifft denjenigen, welcher gegen ein Schutzgesetz verstößt.</div>
  </div>
</div>
</body>
</html>
"""

class TestNorms(unittest.TestCase):
    def test_slug_mappings(self):
        # Critical slugs that previously caused 404
        self.assertEqual(COMMON_LAW_SLUGS["aufenthg"], "aufenthg_2004")
        self.assertEqual(COMMON_LAW_SLUGS["owig"], "owig_1968")
        self.assertEqual(COMMON_LAW_SLUGS["vvg"], "vvg_2008")
        self.assertEqual(COMMON_LAW_SLUGS["bgb"], "bgb")
        self.assertEqual(COMMON_LAW_SLUGS["zpo"], "zpo")

    def test_offline_jur_absatz_parsing(self):
        soup = BeautifulSoup(SAMPLE_JUR_ABSATZ_HTML, "html.parser")
        absatz_divs = soup.find_all("div", class_="jurAbsatz")
        paragraphs = [div.get_text(" ", strip=True) for div in absatz_divs]
        full_text = "\n\n".join(paragraphs)
        clean = sanitize_zero_dashes(full_text)
        self.assertEqual(len(paragraphs), 2)
        self.assertIn("vorsätzlich", clean)
        self.assertIn("\n\n", clean)

    def test_live_statute_fetch(self):
        res = fetch_statute_norm("BGB", "823")
        if not res.get("success"):
            self.skipTest(f"gesetze-im-internet.de unreachable from this network: {res.get('error')}")
        self.assertEqual(res["title"], "Schadensersatzpflicht")
        self.assertIn("Leben, den Körper, die Gesundheit", res["content_clean"])
        self.assertIn("vorsätzlich", res["content_clean"])
        self.assertNotIn("—", res["content_clean"])
        self.assertTrue(res["is_official_verbatim"])
        self.assertIn("source_name", res)
        self.assertIn("retrieved_at", res)

if __name__ == "__main__":
    unittest.main()
