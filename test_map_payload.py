import json
import unittest

import pandas as pd

from map_payload import json_records


class MapPayloadTests(unittest.TestCase):
    def test_all_missing_and_infinite_fields_become_json_null(self):
        frame = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["강북구 주차장", "서대문구 주차장", "은평구 주차장"],
            "lat": [37.5, 37.6, 37.7],
            "score": [float("nan"), 0, 63.7],
            "rain": [float("nan"), float("inf"), -float("inf")],
            "terrain": [12.5, None, 0],
        })
        records = json_records(frame)
        payload = json.dumps(records, allow_nan=False, ensure_ascii=False)
        self.assertNotIn("NaN", payload)
        self.assertNotIn("Infinity", payload)
        self.assertIsNone(records[0]["score"])
        self.assertTrue(all(row["rain"] is None for row in records))
        self.assertEqual(records[1]["score"], 0)
        self.assertEqual(records[2]["score"], 63.7)
        self.assertEqual(records[0]["name"], "강북구 주차장")
        self.assertEqual(records[0]["lat"], 37.5)

    def test_icons_and_empty_frame_remain_valid(self):
        frame = pd.DataFrame([{"id": 1, "score": None, "icon": {"url": "data:image/svg+xml,test", "width": 96}}])
        records = json_records(frame)
        self.assertEqual(records[0]["icon"]["width"], 96)
        json.dumps(records, allow_nan=False)
        self.assertEqual(json_records(frame.iloc[:0]), [])


if __name__ == "__main__":
    unittest.main()
