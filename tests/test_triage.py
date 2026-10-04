import unittest
from german_legal_engine.triage import LegalTriage, get_laya_agent
from german_legal_engine.client import LegalEngine

class DummyLayaAgent:
    """Mock Laya agent returning calibrated probabilities in standard Laya format."""
    def predict(self, state, questions, lang="de"):
        return {
            "answers": {
                "rechtsgebiet": {
                    "choice": "arbeitsrecht",
                    "confidence": 0.94,
                    "probabilities": {
                        "arbeitsrecht": 0.94,
                        "mietrecht": 0.02,
                        "verkehrsrecht_owig": 0.01,
                        "vertragsrecht_schadensersatz": 0.02,
                        "deliktsrecht": 0.01,
                        "allgemein": 0.00
                    }
                },
                "dringlichkeit": {
                    "score": 2.8,
                    "confidence": 0.91,
                    "probabilities": [0.05, 0.15, 0.80]
                },
                "droht_fristablauf": {
                    "noul": 0.96,
                    "confidence": 0.92
                },
                "erfordert_sofortige_eskalation": {
                    "noul": 0.89,
                    "confidence": 0.88
                }
            },
            "usage": {"input_tokens": 42}
        }

class TestLegalTriage(unittest.TestCase):
    def test_triage_questions_schema(self):
        q = LegalTriage.get_triage_questions()
        self.assertIn("rechtsgebiet", q)
        self.assertIn("dringlichkeit", q)
        self.assertIn("droht_fristablauf", q)
        self.assertIn("erfordert_sofortige_eskalation", q)
        self.assertEqual(q["rechtsgebiet"]["type"], "choice")
        self.assertEqual(q["dringlichkeit"]["type"], "score")
        self.assertEqual(q["droht_fristablauf"]["type"], "noul")

    def test_heuristic_triage_arbeitsrecht(self):
        text = "Mein Arbeitgeber hat mir am 02.10.2026 eine fristlose Kündigung überreicht."
        res = LegalEngine.triage_mandate(text, state="BY")
        self.assertTrue(res["success"])
        self.assertEqual(res["domain"], "arbeitsrecht")
        self.assertGreater(res["urgency_score"], 1.0)
        self.assertTrue(res["requires_escalation"])
        self.assertIn("02.10.2026", res["detected_event_dates"])
        self.assertTrue(any("KSchG" in n["norm"] for n in res["suggested_statutory_norms"]))

    def test_heuristic_triage_mietrecht(self):
        text = "Der Vermieter verlangt die Kaution und hat wegen Mängeln die Miete nicht gemindert."
        res = LegalEngine.triage_mandate(text, state="NW")
        self.assertTrue(res["success"])
        self.assertEqual(res["domain"], "mietrecht")
        self.assertTrue(any("551" in n["norm"] or "535" in n["norm"] for n in res["suggested_statutory_norms"]))

    def test_neural_laya_agent_integration(self):
        dummy_agent = DummyLayaAgent()
        text = "Kündigung erhalten, bitte um Fristenprüfung."
        res = LegalEngine.triage_mandate(text, state="BY", agent=dummy_agent)
        self.assertTrue(res["success"])
        self.assertEqual(res["domain"], "arbeitsrecht")
        self.assertEqual(res["domain_confidence"], 0.94)
        self.assertEqual(res["urgency_score"], 2.8)
        self.assertTrue(res["requires_escalation"])
        self.assertEqual(res["raw_triage"]["engine"], "laya_multilingual")
        self.assertTrue(res["raw_triage"]["laya_model_active"])

if __name__ == "__main__":
    unittest.main()
