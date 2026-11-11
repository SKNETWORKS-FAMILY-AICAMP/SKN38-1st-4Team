"""FAQ 원본의 카테고리와 MySQL 문자열이 손실 없이 표시되는지 확인한다."""
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from services.faq import FAQEntry, load_faq


class FAQDataTests(unittest.TestCase):
    def test_supplied_faq_ids_categories_and_multiline_answers(self):
        entries = load_faq()
        self.assertEqual([entry.faq_id for entry in entries], [f"FAQ{i:03d}" for i in range(1, 28)])
        self.assertEqual(Counter(entry.category for entry in entries), {
            "서비스 이용": 4,
            "침수 위험도 지수": 5,
            "데이터 및 분석 기준": 11,
            "분석 범위 및 데이터 활용": 7,
        })
        self.assertEqual(entries[0].question, "이 서비스는 어떤 서비스인가요?")
        self.assertEqual(entries[-1].question, "침수 위험도 정보는 실시간으로 업데이트되나요?")
        self.assertIn("\n\n계산식:\n", entries[13].answer)
        self.assertNotIn(r"\n", entries[13].answer)

    def test_mysql_escaping_and_original_identifiers(self):
        sql = r"""INSERT INTO `faq` VALUES
('FAQ042','새 카테고리','따옴표 \'와 '' 및 쉼표, 세미콜론;','첫 줄\n둘째 줄\n\n경로 C:\\faq');"""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "faq.sql"
            path.write_text(sql, encoding="utf-8-sig")
            self.assertEqual(load_faq(path), [FAQEntry(
                "FAQ042", "새 카테고리", "따옴표 '와 ' 및 쉼표, 세미콜론;",
                "첫 줄\n둘째 줄\n\n경로 C:\\faq",
            )])

    def test_missing_or_duplicate_faq_is_rejected(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "faq.sql"
            path.write_text("CREATE TABLE faq (faq_id TEXT);", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "INSERT"):
                load_faq(path)
            path.write_text(
                "INSERT INTO `faq` VALUES ('FAQ001','분류','질문','답변'),"
                "('FAQ001','다른 분류','다른 질문','다른 답변');", encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "중복"):
                load_faq(path)


if __name__ == "__main__":
    unittest.main()
