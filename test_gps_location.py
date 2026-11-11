import unittest
from pathlib import Path
from unittest import mock

from streamlit.testing.v1 import AppTest

import parking_map
from parking_map import GPS_ERRORS, GPS_INSECURE_ORIGIN, read_gps_result

APP = str(Path(__file__).resolve().parent / "app.py")
CITY_HALL = {"coords": {"latitude": 37.5663, "longitude": 126.9779, "accuracy": 24.6}, "timestamp": 0}


class ReadGpsResultTests(unittest.TestCase):
    def test_no_answer_yet(self):
        self.assertEqual(read_gps_result(None), (None, None))

    def test_coordinates_and_accuracy(self):
        self.assertEqual(read_gps_result(CITY_HALL), ((37.5663, 126.9779, 24.6), None))

    def test_missing_accuracy_is_none(self):
        position, error = read_gps_result({"coords": {"latitude": 37.5, "longitude": 127.0, "accuracy": None}})
        self.assertEqual((position, error), ((37.5, 127.0, None), None))

    def test_permission_denied(self):
        self.assertEqual(read_gps_result({"error": {"code": 1, "message": "User denied Geolocation"}}),
                         (None, GPS_ERRORS[1]))

    def test_insecure_origin(self):
        value = {"error": {"code": 1, "message": "Only secure origins are allowed (see: https://goo.gl/Y0ZkNV)."}}
        self.assertEqual(read_gps_result(value), (None, GPS_INSECURE_ORIGIN))

    def test_broken_or_out_of_range_coordinates(self):
        for coords in ({}, {"latitude": "x", "longitude": 127}, {"latitude": 95, "longitude": 127},
                       {"latitude": float("nan"), "longitude": 127}):
            position, error = read_gps_result({"coords": coords})
            self.assertIsNone(position)
            self.assertTrue(error)


class GpsButtonFlowTests(unittest.TestCase):
    def run_gps(self, answer):
        with mock.patch.object(parking_map, "get_geolocation", return_value=answer) as browser:
            app = AppTest.from_file(APP, default_timeout=60).run()
            app.button(key="gps_button").click().run()
        self.assertFalse(app.exception)
        browser.assert_called_with(component_key="gps_request_1")
        return app

    def test_gps_answer_moves_reference_point(self):
        app = self.run_gps(CITY_HALL)
        self.assertEqual(app.session_state["current_location"], (37.5663, 126.9779))
        self.assertEqual((app.session_state["location_lat"], app.session_state["location_lon"]), (37.5663, 126.9779))
        self.assertFalse(app.session_state["gps_pending"])
        self.assertIn("GPS 현재 위치 기준 · 오차 약 ±25m", [caption.value for caption in app.caption])

    def test_denied_keeps_previous_point_and_warns(self):
        app = self.run_gps({"error": {"code": 1, "message": "User denied Geolocation"}})
        self.assertEqual(app.session_state["current_location"], (37.6333382, 127.0206239))
        self.assertEqual([warning.value for warning in app.warning], [GPS_ERRORS[1]])

    def test_waiting_for_browser(self):
        app = self.run_gps(None)
        self.assertTrue(app.session_state["gps_pending"])
        self.assertEqual(app.session_state["current_location"], (37.6333382, 127.0206239))


if __name__ == "__main__":
    unittest.main()
