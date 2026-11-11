"""Verify the registered pages and the displayed service coverage."""
from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from services.faq import load_faq
from services.parking_data import parking_inventory, service_inventory
from services.parking_map import render_map


class AppNavigationTests(unittest.TestCase):
    def test_unscored_parking_is_excluded_from_map_search_and_comparison(self):
        app = Path(__file__).resolve().parents[1] / "app.py"
        service = service_inventory()
        full = parking_inventory()
        missing = full[full["score"].isna() & full["district"].isin(service["district"])]
        excluded = missing[~missing["name"].isin(service["name"])].iloc[0]
        screen = AppTest.from_file(str(app))
        screen.session_state["parking_dataset_version"] = "rainfall-districts-v4"
        screen.session_state["compare_ids"] = [int(excluded["id"])]
        screen.session_state["selected_id"] = int(excluded["id"])
        with patch("services.parking_map.render_map", wraps=render_map) as draw:
            screen.run()
            self.assertFalse(screen.exception)
            self.assertEqual(screen.session_state["compare_ids"], [])
            self.assertIsNone(screen.session_state["selected_id"])
            screen.session_state["parking_scope"] = "전체 지역"
            screen.session_state["parking_district"] = "전체 지역"
            screen.run()
            self.assertFalse(screen.exception)
            plotted = draw.call_args.args[0]
            self.assertEqual(set(plotted["id"]), set(service["id"]))
            self.assertTrue(plotted["score"].notna().all())
            screen.text_input(key="parking_query").set_value(excluded["name"]).run()
            self.assertFalse(screen.exception)
            self.assertTrue(draw.call_args.args[0].empty)
            screen.text_input(key="parking_query").set_value("").run()
            screen.radio[0].set_value("주차장 상세 비교").run()
            self.assertFalse(screen.exception)
            self.assertEqual(len(screen.multiselect[0].options), 137)
            self.assertNotIn(excluded["name"], screen.multiselect[0].options)
            screen.multiselect[0].set_value(service["id"].head(2).tolist()).run()
            self.assertFalse(screen.exception)
            self.assertEqual(len(screen.metric), 2)
            self.assertTrue(all("미산정" not in metric.value for metric in screen.metric))

    def test_selected_parking_detail_shows_kakao_route_panel(self):
        app = Path(__file__).resolve().parents[1] / "app.py"
        target = service_inventory().iloc[0]
        screen = AppTest.from_file(str(app)).run()
        screen.session_state["parking_scope"] = "전체 지역"
        screen.session_state["parking_district"] = "전체 지역"
        screen.session_state["selected_id"] = int(target["id"])
        route ={"distance": 2120.0, "duration": 360.0, "toll": None,
                 "paths": [{"path": [[127.0, 37.6], [127.01, 37.61]]}]}
        with patch("services.kakao_navi.directions", return_value=route) as request:
            screen.run()
            self.assertFalse(screen.exception)
            self.assertIn("#### 카카오 자동차 길찾기", [item.value for item in screen.markdown])
            screen.button(key=f'route_button_{int(target["id"])}').click().run()
            self.assertFalse(screen.exception)
        origin, destination, priority = request.call_args.args
        self.assertEqual(destination, (float(target["lon"]), float(target["lat"])))
        self.assertEqual(priority, "RECOMMEND")
        metrics = {metric.label: metric.value for metric in screen.metric}
        self.assertEqual(metrics["자동차 이동 거리"], "2.12 km")
        self.assertEqual(metrics["예상 소요 시간"], "6분")

    def test_home_faq_and_analysis(self):
        app = Path(__file__).resolve().parents[1] / "app.py"
        screen = AppTest.from_file(str(app)).run()
        self.assertFalse(screen.exception)
        self.assertEqual(
            [button.label for button in screen.sidebar.button],
            ["홈 (주차장 탐색)", "FAQ", "분석 데이터 결과"],
        )
        self.assertTrue(any("추정 위험점수 산정 주차장 137개" in item.value for item in screen.caption))
        self.assertFalse(any("미산정" in item.value for item in screen.caption))

        screen.switch_page("pages/1_FAQ.py").run()
        self.assertFalse(screen.exception)
        self.assertEqual(len(screen.expander), 27)

        screen.switch_page("pages/2_Analysis_Results.py").run()
        self.assertFalse(screen.exception)
        metrics = {metric.label: metric.value for metric in screen.metric}
        self.assertEqual(metrics["분석 대상 주차장"], "137개")
        self.assertNotIn("상대 위험도 미산정", metrics)
        self.assertEqual(sum(int(value.removesuffix("개")) for key, value in metrics.items() if key.startswith("상대 위험도")), 137)
        self.assertFalse(any("미산정" in item.value for item in screen.caption))
        for table in screen.dataframe:
            self.assertEqual(table.value["위험지수"].dtype.kind, "i")

    def test_faq_categories_filter_questions_and_answers(self):
        page = Path(__file__).resolve().parents[1] / "pages" / "1_FAQ.py"
        screen = AppTest.from_file(str(page)).run()
        self.assertFalse(screen.exception)
        categories = ["서비스 이용", "침수 위험도 지수", "데이터 및 분석 기준", "분석 범위 및 데이터 활용"]
        self.assertEqual(screen.radio[0].options, ["전체 질문", *categories])
        self.assertEqual(len(screen.expander), 27)
        self.assertEqual([item.value for item in screen.subheader][1:], [
            "서비스 이용 · 4개", "침수 위험도 지수 · 5개",
            "데이터 및 분석 기준 · 11개", "분석 범위 및 데이터 활용 · 7개",
        ])
        entries = load_faq()
        for category in categories:
            with self.subTest(category=category):
                screen.radio[0].set_value(category).run()
                self.assertFalse(screen.exception)
                expected = [entry for entry in entries if entry.category == category]
                self.assertEqual([item.label for item in screen.expander], [f"Q. {entry.question}" for entry in expected])
                self.assertEqual([item.value for item in screen.markdown], [entry.answer for entry in expected])
                self.assertEqual(screen.subheader[0].value, f"자주 묻는 질문 {len(expected)}")
        screen.radio[0].set_value("전체 질문").run()
        self.assertFalse(screen.exception)
        self.assertEqual(len(screen.expander), 27)
