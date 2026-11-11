"""Verify the registered pages and the displayed service coverage."""
from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest


class AppNavigationTests(unittest.TestCase):
    def test_home_faq_and_analysis(self):
        app = Path(__file__).resolve().parents[1] / "app.py"
        screen = AppTest.from_file(str(app)).run()
        self.assertFalse(screen.exception)
        self.assertEqual(
            [button.label for button in screen.sidebar.button],
            ["홈 (주차장 탐색)", "FAQ", "분석 데이터 결과"],
        )
        self.assertTrue(any("전체 등록 주차장 163개" in item.value for item in screen.caption))

        screen.switch_page("pages/1_FAQ.py").run()
        self.assertFalse(screen.exception)
        self.assertEqual(len(screen.expander), 5)

        screen.switch_page("pages/2_Analysis_Results.py").run()
        self.assertFalse(screen.exception)
        metrics = {metric.label: metric.value for metric in screen.metric}
        self.assertEqual(metrics["분석 대상 주차장"], "163개")
        self.assertEqual(metrics["상대 위험도 미산정"], "26개")
        for table in screen.dataframe:
            self.assertEqual(table.value["위험지수"].dtype.kind, "i")
