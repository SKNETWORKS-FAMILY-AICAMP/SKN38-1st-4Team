"""sql/Table07_faq.sql의 FAQ를 화면과 SQL 덤프에서 함께 읽는다."""
from pathlib import Path
import re
from typing import NamedTuple


FAQ_SQL = Path(__file__).resolve().parents[1] / "sql" / "Table07_faq.sql"
_STRING = r"'(?:\\.|''|[^'\\])*'"
_ROW = re.compile(r"\(\s*" + r"\s*,\s*".join([f"({_STRING})"] * 4) + r"\s*\)", re.DOTALL)
_INSERT = re.compile(
    r"INSERT\s+INTO\s+`?faq`?\s+VALUES\s*(?P<rows>"
    + _ROW.pattern + r"(?:\s*,\s*" + _ROW.pattern + r")*)\s*;",
    re.IGNORECASE | re.DOTALL,
)
_ESCAPES = {"0": "\0", "b": "\b", "n": "\n", "r": "\r", "t": "\t", "Z": "\x1a"}


class FAQEntry(NamedTuple):
    faq_id: str
    category: str
    question: str
    answer: str


def _decode_string(value):
    """MySQL 문자열의 따옴표와 줄바꿈 등을 복원한다. SQL은 실행하지 않는다."""
    return re.sub(
        r"\\(.)", lambda match: _ESCAPES.get(match[1], match[1]),
        value[1:-1].replace("''", "'"), flags=re.DOTALL,
    )


def load_faq(path=FAQ_SQL):
    """네 문자열 열(faq_id, category, question, answer)을 가진 팀 덤프를 읽는다."""
    sql = Path(path).read_text(encoding="utf-8-sig")
    entries = [
        FAQEntry(*(_decode_string(value) for value in row.groups()))
        for insert in _INSERT.finditer(sql)
        for row in _ROW.finditer(insert["rows"])
    ]
    if not entries:
        raise ValueError(f"FAQ INSERT 데이터를 찾을 수 없습니다: {path}")
    if len({entry.faq_id for entry in entries}) != len(entries):
        raise ValueError(f"FAQ 관리번호가 중복되었습니다: {path}")
    return entries
