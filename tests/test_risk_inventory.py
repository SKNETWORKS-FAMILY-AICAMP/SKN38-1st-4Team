"""Check imported totals and supporting measurements against their sources."""
import csv
import hashlib
import json
from pathlib import Path
import unittest

from services.data_paths import DATA_DIR, RISK_RESULTS_CSV
from services.map_payload import json_records
from services.parking_data import parking_inventory, service_inventory
from services.parking_marker import marker_icon, risk_band
from services.service_config import SERVICE_DISTRICTS


class RiskInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = Path(__file__).resolve().parent / "fixtures" / "risk_audit.json"
        cls.audit = json.loads(fixture.read_text(encoding="utf-8"))
        with RISK_RESULTS_CSV.open(encoding="utf-8-sig", newline="") as source:
            cls.totals = {row["parking_lot_id"]: int(row["total_risk_score"]) for row in csv.DictReader(source)}
        cls.frame = parking_inventory()

    def test_source_snapshot_and_coverage(self):
        for name, expected_hash in self.audit["source_sha256"].items():
            with self.subTest(source=name):
                self.assertEqual(hashlib.sha256((DATA_DIR / name).read_bytes()).hexdigest(), expected_hash)
        self.assertEqual(len(self.frame), self.audit["total"])
        self.assertTrue(self.frame["lowland_raw"].notna().all())
        self.assertTrue(self.frame["depth"].notna().all())
        self.assertTrue(self.frame["distance_risk"].notna().all())

    def test_nearest_point_examples(self):
        rows = self.frame.set_index("id")
        for expected in self.audit["cases"]:
            with self.subTest(parking=expected["code"]):
                row = rows.loc[expected["id"]]
                self.assertEqual(row["parking_code"], expected["code"])
                self.assertEqual(str(row["nearest_flood_id"]), str(expected["nearest_flood_id"]))
                self.assertAlmostEqual(row["flood_distance_m"], expected["minimum_distance_m"], places=6)

    def test_final_scores_equal_csv_and_missing_ids_stay_unscored(self):
        scores = self.frame.set_index("parking_code")["score"]
        self.assertEqual(str(scores.dtype), "Int64")
        self.assertEqual(scores.dropna().to_dict(), self.totals)
        self.assertEqual(len(self.totals), 137)
        missing = self.frame[~self.frame["parking_code"].isin(self.totals)]
        self.assertTrue(missing["score"].isna().all())
        self.assertTrue(missing["risk_missing_reason"].str.contains("최종 점수가 없습니다").all())
        self.assertTrue(all(risk_band(score)[1] == "미산정" for score in missing["score"]))

    def test_service_keeps_unscored_parking_in_the_five_districts(self):
        service = service_inventory()
        self.assertEqual(SERVICE_DISTRICTS, tuple(sorted(self.audit["scored_by_district"])))
        self.assertEqual(sorted(service["district"].unique()), list(SERVICE_DISTRICTS))
        self.assertEqual(len(service), 163)
        self.assertEqual(int(service["score"].isna().sum()), 26)
        full = self.frame.set_index("id")["score"]
        self.assertTrue(service.set_index("id")["score"].equals(full.loc[service["id"]]))

    def test_every_marker_has_valid_json_with_no_nan(self):
        frame = self.frame[["id", "name", "lat", "lon", "score"]].copy()
        frame["icon"] = [marker_icon(score) for score in frame["score"]]
        records = json_records(frame)
        self.assertEqual(len(records), 806)
        json.dumps(records, allow_nan=False)
        self.assertTrue(all(record["icon"]["url"].startswith("data:image/svg+xml") for record in records))
        self.assertTrue(all(record["score"] is None or type(record["score"]) is int for record in records))


if __name__ == "__main__":
    unittest.main()
