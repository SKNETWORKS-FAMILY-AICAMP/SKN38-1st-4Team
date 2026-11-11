"""Compare the production loader against independent source-data calculations."""
import hashlib
import json
from pathlib import Path
import unittest

from map_payload import json_records
from parking_data import parking_inventory, service_inventory
from parking_marker import marker_icon, risk_band
from service_config import SERVICE_DISTRICTS


class RiskInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Path(__file__).parent / "data"
        cls.audit = json.loads((cls.base / "risk_audit.json").read_text(encoding="utf-8"))
        cls.frame = parking_inventory()

    def test_source_snapshot_and_coverage(self):
        for name, expected_hash in self.audit["source_sha256"].items():
            with self.subTest(source=name):
                self.assertEqual(hashlib.sha256((self.base / name).read_bytes()).hexdigest(), expected_hash)
        self.assertEqual(len(self.frame), self.audit["total"])
        self.assertEqual(int(self.frame["score"].notna().sum()), self.audit["scored"])
        self.assertEqual(int(self.frame["score"].isna().sum()), self.audit["unscored"])
        self.assertTrue(self.frame["lowland_raw"].notna().all())
        self.assertTrue(self.frame["depth"].notna().all())
        self.assertTrue(self.frame["distance_risk"].notna().all())

    def test_score_and_nearest_point_examples(self):
        rows = self.frame.set_index("id")
        for expected in self.audit["cases"]:
            with self.subTest(parking=expected["code"]):
                row = rows.loc[expected["id"]]
                self.assertEqual(row["parking_code"], expected["code"])
                self.assertEqual(str(row["nearest_flood_id"]), str(expected["nearest_flood_id"]))
                self.assertAlmostEqual(row["flood_distance_m"], expected["minimum_distance_m"], places=6)
                self.assertAlmostEqual(row["score"], expected["score"], places=7)

    def test_missing_rain_does_not_become_a_low_risk_score(self):
        missing = self.frame[self.frame["rain_raw"].isna()]
        self.assertTrue(missing["score"].isna().all())
        self.assertTrue(missing["risk_missing_reason"].str.contains("강수 데이터 없음").all())
        self.assertTrue(all(risk_band(score)[1] == "미산정" for score in missing["score"]))

    def test_service_shows_only_districts_with_every_score_input(self):
        service = service_inventory()
        self.assertEqual(SERVICE_DISTRICTS, tuple(sorted(self.audit["scored_by_district"])))
        self.assertEqual(sorted(service["district"].unique()), list(SERVICE_DISTRICTS))
        self.assertEqual(len(service), self.audit["scored"])
        self.assertTrue(service["score"].notna().all())
        # Narrowing the view must not change scores computed against the full inventory.
        full = self.frame.set_index("id")["score"]
        self.assertTrue((service.set_index("id")["score"] == full.loc[service["id"]]).all())

    def test_every_marker_has_valid_json_with_no_nan(self):
        frame = self.frame[["id", "name", "lat", "lon", "score"]].copy()
        frame["icon"] = [marker_icon(score) for score in frame["score"]]
        records = json_records(frame)
        self.assertEqual(len(records), 806)
        json.dumps(records, allow_nan=False)
        self.assertTrue(all(record["icon"]["url"].startswith("data:image/svg+xml") for record in records))


if __name__ == "__main__":
    unittest.main()
