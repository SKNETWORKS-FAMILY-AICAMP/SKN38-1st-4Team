import unittest

from services.parking_marker import marker_icon, marker_svg, normalized_marker_score, risk_band


class ParkingMarkerTests(unittest.TestCase):
    def test_missing_and_nonfinite_scores(self):
        for value in (None, float("nan"), float("inf"), -float("inf"), "NaN", "", "invalid"):
            with self.subTest(value=value):
                self.assertIsNone(normalized_marker_score(value))
                self.assertEqual(risk_band(value)[1], "미산정")
                self.assertIn('fill="#edf2f7"', marker_svg(value))
                self.assertIn('id="car"', marker_svg(value))
                self.assertNotIn('<rect x="31" y="54"', marker_svg(value))
                self.assertNotIn(">P</text>", marker_svg(value))
                self.assertIn("svg", marker_icon(value)["url"])

    def test_zero_is_scored_and_boundaries_are_preserved(self):
        for score, label in [(0, "매우 낮음"), (19, "매우 낮음"), (20, "낮음"), (39, "낮음"), (40, "보통"), (59, "보통"), (60, "높음"), (79, "높음"), (80, "매우 높음"), (100, "매우 높음")]:
            with self.subTest(score=score):
                self.assertEqual(risk_band(score)[1], label)
                self.assertNotIn(">P</text>", marker_svg(score))
        self.assertEqual(normalized_marker_score(-1), 0)
        self.assertEqual(normalized_marker_score(101), 100)


if __name__ == "__main__":
    unittest.main()
