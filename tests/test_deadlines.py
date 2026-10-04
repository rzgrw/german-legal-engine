import unittest
from datetime import date
from german_legal_engine.deadlines import calculate_deadline, get_public_holidays

class TestDeadlines(unittest.TestCase):
    def test_regular_deadline_no_shift(self):
        # Wednesday 2026-10-07 + 1 week -> Wednesday 2026-10-14 (no holiday)
        res = calculate_deadline(date(2026, 10, 7), 1, "wochen", state="BY")
        self.assertEqual(res["frist_beginn"], "2026-10-08")
        self.assertEqual(res["endgueltiges_ende"], "2026-10-14")
        self.assertFalse(res["shifted_by_193_bgb"])
        self.assertNotIn("—", res["citation"])

    def test_saturday_shift_to_monday(self):
        # Event on Saturday 2026-10-03 + 1 week -> Saturday 2026-10-10 -> shifts to Monday 2026-10-12
        res = calculate_deadline(date(2026, 10, 3), 1, "wochen", state="BY")
        self.assertEqual(res["regulaeres_ende"], "2026-10-10") # Saturday
        self.assertEqual(res["endgueltiges_ende"], "2026-10-12") # Monday
        self.assertTrue(res["shifted_by_193_bgb"])
        self.assertIn("Samstag", res["shift_reasons"][0])

    def test_month_deadline_exact_day(self):
        # October 15, 2026 + 1 month -> November 15, 2026 (Sunday) -> shifts to Monday November 16
        res = calculate_deadline(date(2026, 10, 15), 1, "monate", state="BY")
        self.assertEqual(res["regulaeres_ende"], "2026-11-15")
        self.assertEqual(res["endgueltiges_ende"], "2026-11-16")
        self.assertTrue(res["shifted_by_193_bgb"])

    def test_month_deadline_short_month_clamp(self):
        # § 188 Abs. 3 BGB: Jan 31 + 1 month -> Feb 28 (non-leap year 2026)
        res = calculate_deadline(date(2026, 1, 31), 1, "monate", state="BY")
        self.assertEqual(res["regulaeres_ende"], "2026-02-28") # Saturday
        self.assertEqual(res["endgueltiges_ende"], "2026-03-02") # Monday

    def test_tag_der_deutschen_einheit(self):
        holidays = get_public_holidays(2026, state="BY")
        self.assertIn(date(2026, 10, 3), holidays)
        self.assertEqual(holidays[date(2026, 10, 3)], "Tag der Deutschen Einheit")

    def test_state_specific_holidays(self):
        # Berlin has Frauentag on March 8
        h_be = get_public_holidays(2026, state="BE")
        self.assertIn(date(2026, 3, 8), h_be)
        self.assertEqual(h_be[date(2026, 3, 8)], "Internationaler Frauentag")

        # Sachsen has Buß- und Bettag (Wednesday before Nov 23)
        h_sn = get_public_holidays(2026, state="SN")
        self.assertTrue(any("Buß" in name for name in h_sn.values()))

    def test_audit_trail_statutory_derivation(self):
        # Verify complete step-by-step statutory derivation under §§ 187, 188, 193 BGB
        res = calculate_deadline(date(2026, 10, 3), 1, "wochen", state="BY")
        self.assertIn("audit_trail", res)
        trail = res["audit_trail"]
        self.assertEqual(len(trail), 4)
        
        # Step 1: § 187 Abs. 1 BGB
        self.assertEqual(trail[0]["step"], 1)
        self.assertEqual(trail[0]["rule"], "§ 187 Abs. 1 BGB")
        self.assertIn("Ereignisfrist", trail[0]["title"])
        
        # Step 2: § 188 Abs. 2 Alt. 1 BGB
        self.assertEqual(trail[1]["step"], 2)
        self.assertIn("§ 188", trail[1]["rule"])
        
        # Step 3: § 193 BGB
        self.assertEqual(trail[2]["step"], 3)
        self.assertIn("§ 193 BGB", trail[2]["rule"])
        self.assertIn("Samstag", trail[2]["description"])
        
        # Step 4: Final legal determination
        self.assertEqual(trail[3]["step"], 4)
        self.assertIn("Rechtswirksamer Fristablauf", trail[3]["title"])

if __name__ == "__main__":
    unittest.main()
