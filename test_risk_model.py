import unittest

from risk_model import annual_rainfall_metrics, distance_score, normalize_by_max, rainfall_risk, weighted_risk


class RiskModelTests(unittest.TestCase):
    def test_agreed_weights_and_endpoints(self):
        self.assertAlmostEqual(weighted_risk(1, 0, 0, 0), 27)
        self.assertAlmostEqual(weighted_risk(0, 1, 0, 0), 18)
        self.assertAlmostEqual(weighted_risk(0, 0, 1, 0), 30)
        self.assertAlmostEqual(weighted_risk(0, 0, 0, 1), 25)
        self.assertAlmostEqual(weighted_risk(1, 1, 1, 1), 100)
        self.assertEqual(weighted_risk(0, 0, 0, 0), 0)
        self.assertAlmostEqual(weighted_risk(0.6, 0.75, 0.8, 0.4), 63.7)

    def test_missing_is_not_zero_and_invalid_scale_rejected(self):
        self.assertIsNone(weighted_risk(1, 1, None, 1))
        self.assertIsNone(weighted_risk(1, float("nan"), 1, 1))
        with self.assertRaises(ValueError):
            weighted_risk(1, 1, 66.6, 1)

    def test_depth_and_distance_normalization(self):
        self.assertAlmostEqual(normalize_by_max(0.3, 0.5), 0.6)
        self.assertAlmostEqual(distance_score(25, 100, "nearer_higher"), 0.75)
        self.assertAlmostEqual(distance_score(25, 100, "farther_higher"), 0.25)
        self.assertIsNone(distance_score(25, 100, None))
        self.assertIsNone(normalize_by_max(0, 0))

    def test_rainfall_formula(self):
        self.assertAlmostEqual(rainfall_risk(52.5, 113.5, 1), 66.6)
        self.assertAlmostEqual(rainfall_risk(41.5, 56.5, 0), 39.2)

    def test_rolling_windows_day_dedup_and_strict_threshold(self):
        samples = []
        for date, values in [
            ("2025-07-01", {1: 20, 2: 20, 3: 20}),
            ("2025-07-02", {1: 21, 2: 21, 3: 21, 4: 21}),
            ("2025-07-03", {2: 30, 3: 30, 4: 30}),
        ]:
            samples.extend((date, hour, values.get(hour, 0)) for hour in range(1, 25))
        self.assertEqual(annual_rainfall_metrics(samples), {"max_1h_mm": 30, "max_3h_mm": 90, "heavy_rain_days": 2})

    def test_windows_never_cross_dates(self):
        samples = [("2025-07-01", h, 25 if h in (23, 24) else 0) for h in range(1, 25)]
        samples += [("2025-07-02", h, 25 if h == 1 else 0) for h in range(1, 25)]
        result = annual_rainfall_metrics(samples)
        self.assertEqual(result["max_3h_mm"], 50)
        self.assertEqual(result["heavy_rain_days"], 0)

    def test_missing_and_duplicate_hours_are_rejected(self):
        with self.assertRaises(ValueError):
            annual_rainfall_metrics([("2025-07-01", 1, 0)])
        with self.assertRaises(ValueError):
            annual_rainfall_metrics([("2025-07-01", 1, 0), ("2025-07-01", 1, 0)])


if __name__ == "__main__":
    unittest.main()
