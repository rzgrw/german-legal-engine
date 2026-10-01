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

    def test_saturday_shift_to_monday(self):
        # Event on Friday 2026-10-03 + 1 week -> Saturday 2026-10-10 -> shifts to Monday 2026-10-12
        res = calculate_deadline(date(2026, 10, 3), 1, "wochen", state="BY")
        self.assertEqual(res["regulaeres_ende"], "2026-10-10") # Saturday
        self.assertEqual(res["endgueltiges_ende"], "2026-10-12") # Monday
        self.assertTrue(res["shifted_by_193_bgb"])
        self.assertIn("Samstag", res["shift_reasons"][0])

    def test_tag_der_deutschen_einheit(self):
        # 03.10 is Tag der Deutschen Einheit
        holidays = get_public_holidays(2026, state="BY")
        self.assertIn(date(2026, 10, 3), holidays)
        self.assertEqual(holidays[date(2026, 10, 3)], "Tag der Deutschen Einheit")

if __name__ == "__main__":
    unittest.main()
