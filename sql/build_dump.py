"""Write sql/skn_1st_4team.sql: the team's final MySQL dump, aligned to what the frontend shows.

Tables, column names and the file layout follow the team dump
dump-skn_1st_4team-202611102110.sql (7 tables, mysqldump format). Values come from
parking_inventory() (the frame app.py draws), data/flood_depth.xlsx, data/rainfall.csv and
the FAQ list in app.py, so the database holds what the screens show. Run from the project folder:

    python sql/build_dump.py
"""
import ast
import logging
import math
import sys
from collections import namedtuple
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
logging.getLogger("streamlit").setLevel(logging.ERROR)

import pandas as pd  # noqa: E402

DATA = ROOT / "data"
OUTPUT = Path(__file__).resolve().parent / "skn_1st_4team.sql"
DATABASE = "skn_1st_4team"
TABLE_OPTIONS = "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
# mysql_real_escape_string, which mysqldump uses for string values.
ESCAPES = {"\0": "\\0", "\n": "\\n", "\r": "\\r", "\\": "\\\\", "'": "\\'", '"': '\\"', "\x1a": "\\Z"}

Table = namedtuple("Table", "name definition columns rows")


def literal(value, scale=None):
    """Return a MySQL literal; NaN/None become NULL, decimals are written at the column scale."""
    if value is None or value is pd.NA:
        return "NULL"
    if isinstance(value, str):
        return "'" + "".join(ESCAPES.get(char, char) for char in value) + "'"
    number = float(value)
    if not math.isfinite(number):
        return "NULL"
    if scale is None:
        if not number.is_integer():
            raise ValueError(f"정수 열에 소수 값이 들어왔습니다: {value}")
        return str(int(number))
    return f"{number:.{scale}f}"


def table_sql(table):
    """One table in mysqldump layout: structure, then data inside LOCK/UNLOCK."""
    names = ",".join(f"`{name}`" for name, _ in table.columns)
    values = ",\n".join(
        "(" + ",".join(literal(row[i], scale) for i, (_, scale) in enumerate(table.columns)) + ")"
        for row in table.rows)
    return "\n".join([
        "--",
        f"-- Table structure for table `{table.name}`",
        "--",
        "",
        f"DROP TABLE IF EXISTS `{table.name}`;",
        "/*!40101 SET @saved_cs_client     = @@character_set_client */;",
        "/*!50503 SET character_set_client = utf8mb4 */;",
        f"CREATE TABLE `{table.name}` (",
        ",\n".join("  " + line for line in table.definition),
        f") {TABLE_OPTIONS};",
        "/*!40101 SET character_set_client = @saved_cs_client */;",
        "",
        "--",
        f"-- Dumping data for table `{table.name}` ({len(table.rows)}행)",
        "--",
        "",
        f"LOCK TABLES `{table.name}` WRITE;",
        f"/*!40000 ALTER TABLE `{table.name}` DISABLE KEYS */;",
        f"INSERT INTO `{table.name}` ({names}) VALUES\n{values};" if table.rows else "",
        f"/*!40000 ALTER TABLE `{table.name}` ENABLE KEYS */;",
        "UNLOCK TABLES;",
        "",
    ])


HEADER = """/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
"""

FOOTER = """/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
"""


def faq_rows():
    """Read the FAQ literal from app.py without running the Streamlit page."""
    tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "FAQ" for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError("app.py 에서 FAQ 목록을 찾지 못했습니다.")


# The team dump's calculated_at; the screens never read it, so it stays as the team wrote it.
CALCULATED_AT = "2026-11-09 23:15:07"

def notes(tables):
    """The header comment. The new counts, the depth maximum and the grade bands are read from the tables and
    parking_marker.RISK_BANDS so they cannot go stale; the team dump's numbers (204, 137, 3단계, 27) are text,
    and verify_mysql_load.py checks every number here against the team dump and the frontend."""
    from parking_marker import RISK_BANDS

    count = {table.name: len(table.rows) for table in tables}
    by_name = {table.name: table for table in tables}

    def column(table_name, column_name):
        table = by_name[table_name]
        at = [name for name, _ in table.columns].index(column_name)
        return [row[at] for row in table.rows]

    unscored = sum(1 for value in column("parking_risk_result", "total_risk_score") if pd.isna(value))
    scored = count["parking_risk_result"] - unscored
    depth_max = max(float(value) for value in column("flood_area", "depth_m"))
    bands = ", ".join(f"{band[4]} {band[1]}" for band in RISK_BANDS)
    return f"""-- {DATABASE} 정렬판 (MySQL 8) — sql/build_dump.py 가 만든 파일입니다. 직접 고치지 말고 생성기를 다시 실행하세요.
-- 기준: 팀 최종 덤프 dump-skn_1st_4team-202611102110.sql 의 7테이블·열 이름·형식.
--       값은 프론트엔드 parking_inventory() 가 계산해 화면에 보여 주는 값과 app.py 의 FAQ 입니다.
-- 적재(데이터베이스를 먼저 만들어 두세요. 같은 이름의 테이블 {len(tables)}개는 지우고 다시 만듭니다):
--   mysql -u <사용자> -p --default-character-set=utf8mb4 {DATABASE} < sql/{OUTPUT.name}
--   PowerShell 은 < 를 쓸 수 없으므로: mysql -u <사용자> -p --default-character-set=utf8mb4 {DATABASE} -e "source sql/{OUTPUT.name}"
--   이 DB 의 ALL 권한이 있는 계정으로 적재하세요(팀 덤프와 같음). LOCK TABLES 권한이 없으면 faq 에서,
--   REFERENCES 권한이 없으면 parking_flood_distance 에서 멈춥니다. 다른 연결(Workbench 탭 등)이 이 DB 의 트랜잭션을
--   열어 두면 DROP TABLE 에서 출력 없이 기다리니 닫고 실행하세요. 멈추거나 끊겼으면 같은 명령을 처음부터 다시 실행합니다.
-- 팀 덤프와 다른 점:
--   parking_lot.latitude DECIMAL(10,7) → (11,8): 원본 위도 소수 8자리를 그대로 담습니다(기준점 거리 표시).
--   parking_lowland.lowland_score DECIMAL(6,2) → (8,4): 저지대 상대점수 .1f 표시가 같아지는 자릿수입니다.
--   flood_area.depth_m DECIMAL(5,2) 추가: 원 침수심(단위 m 는 추정). depth_score 는 그대로 침수심 ÷ {depth_max:g} 입니다.
--   parking_flood_distance 204 → {count["parking_flood_distance"]}행(주차장마다 가장 가까운 침수 지점 하나), distance_m DECIMAL(10,2) → (11,3),
--     flood_risk_score = 침수심 점수 × 0.6 + 거리 점수 × 0.4 (0~100 척도: 침수심 점수 = depth_score × 100,
--     거리 점수 = (1 − 거리 ÷ 전체 최대 거리) × 100).
--   parking_risk_result 137 → {count["parking_risk_result"]}행: result_id = 프론트 주차장 번호(원본 CSV 순서, 화면 정렬 기준이므로 ORDER BY result_id 로 읽기),
--     total_risk_score DECIMAL(5,2) → (7,4) = 화면 위험지수, rainfall_risk_score = 정규화 강수(원값 ÷ 최댓값 × 100),
--     risk_grade 는 팀의 3단계(낮음·보통·높음) 대신 화면의 {len(RISK_BANDS)}단계입니다(위험지수의 정수 부분 기준).
--     등급 구간: {bands}.
--     risk_rank 는 total_risk_score(소수 4자리) 내림차순 순위로 다시 매겼습니다(동점은 같은 순위, 산정된 {scored}곳).
--     강수 자료가 없는 자치구의 {unscored}행은 total_risk_score·rainfall_risk_score·risk_rank·analysis_year 가 NULL, risk_grade '미산정'.
--   faq: 팀 FAQ 27개 대신 화면(app.py)의 FAQ {count["faq"]}개입니다.
"""


def build_tables():
    from parking_data import parking_inventory
    from parking_marker import risk_band
    from risk_data import read_flood_points

    frame = parking_inventory().sort_values("parking_code").reset_index(drop=True)
    if frame["parking_code"].duplicated().any() or frame["id"].duplicated().any():
        raise ValueError("주차장 관리번호나 프론트 번호가 중복되었습니다.")
    for column in ("depth_reference_max", "distance_reference_max_m", "rain_reference_max"):
        if frame[column].nunique(dropna=False) != 1:
            raise ValueError(f"{column} 가 주차장마다 달라 한 기준으로 저장할 수 없습니다.")
    depth_max = float(frame["depth_reference_max"].iloc[0])
    flood = read_flood_points(DATA / "flood_depth.xlsx")
    flood["flood_id"] = pd.to_numeric(flood["flood_id"], errors="raise").astype(int)
    flood = flood.sort_values("flood_id")
    if float(flood["depth"].max()) != depth_max:
        raise ValueError("전체 침수 지점의 최대 침수심이 화면의 정규화 기준과 다릅니다.")
    rain = pd.read_csv(DATA / "rainfall.csv", encoding="utf-8-sig").sort_values("지점")

    total_text = frame["score"].map(lambda value: None if pd.isna(value) else f"{value:.4f}")
    stored_total = pd.to_numeric(total_text, errors="coerce")
    frame["risk_rank"] = stored_total.rank(method="min", ascending=False)
    frame["level"] = frame["score"].map(lambda value: risk_band(value)[1])

    return [
        Table("faq", [
            "`faq_id` varchar(20) NOT NULL",
            "`category` varchar(50) DEFAULT NULL",
            "`question` varchar(255) DEFAULT NULL",
            "`answer` text",
            "PRIMARY KEY (`faq_id`)",
        ], [("faq_id", None), ("category", None), ("question", None), ("answer", None)],
            [(f"FAQ{number:03d}", category, question, answer)
             for number, (category, question, answer) in enumerate(faq_rows(), start=1)]),
        Table("flood_area", [
            "`flood_id` int NOT NULL",
            "`address` varchar(150) DEFAULT NULL",
            "`latitude` decimal(10,7) DEFAULT NULL",
            "`longitude` decimal(10,7) DEFAULT NULL",
            "`depth_score` decimal(5,2) DEFAULT NULL",
            "`depth_m` decimal(5,2) DEFAULT NULL",
            "PRIMARY KEY (`flood_id`)",
        ], [("flood_id", None), ("address", None), ("latitude", 7), ("longitude", 7), ("depth_score", 2),
            ("depth_m", 2)],
            [(r["flood_id"], r["정제주소"], r["lat"], r["lon"], r["depth"] / depth_max, r["depth"])
             for _, r in flood.iterrows()]),
        Table("parking_flood_distance", [
            "`parking_lot_id` varchar(20) NOT NULL",
            "`flood_id` int NOT NULL",
            "`distance_m` decimal(11,3) DEFAULT NULL",
            "`flood_risk_score` decimal(5,2) DEFAULT NULL",
            "PRIMARY KEY (`parking_lot_id`,`flood_id`)",
            "KEY `FK_FLOOD_AREA_TO_PARKING_FLOOD_DISTANCE_1` (`flood_id`)",
            "CONSTRAINT `FK_FLOOD_AREA_TO_PARKING_FLOOD_DISTANCE_1` FOREIGN KEY (`flood_id`) "
            "REFERENCES `flood_area` (`flood_id`)",
            "CONSTRAINT `FK_PARKING_LOT_TO_PARKING_FLOOD_DISTANCE_1` FOREIGN KEY (`parking_lot_id`) "
            "REFERENCES `parking_lot` (`parking_lot_id`)",
        ], [("parking_lot_id", None), ("flood_id", None), ("distance_m", 3), ("flood_risk_score", 2)],
            [(r["parking_code"], int(r["nearest_flood_id"]), r["flood_distance_m"], r["history"])
             for _, r in frame.iterrows() if pd.notna(r["flood_distance_m"])]),
        Table("parking_lot", [
            "`parking_lot_id` varchar(20) NOT NULL",
            "`parking_name` varchar(100) DEFAULT NULL",
            "`address` varchar(100) DEFAULT NULL",
            "`latitude` decimal(11,8) DEFAULT NULL",
            "`longitude` decimal(10,7) DEFAULT NULL",
            "PRIMARY KEY (`parking_lot_id`)",
        ], [("parking_lot_id", None), ("parking_name", None), ("address", None), ("latitude", 8), ("longitude", 7)],
            [(r["parking_code"], r["name"], r["address"], r["lat"], r["lon"]) for _, r in frame.iterrows()]),
        Table("parking_lowland", [
            "`parking_lot_id` varchar(20) NOT NULL",
            "`lowland_score` decimal(8,4) DEFAULT NULL",
            "PRIMARY KEY (`parking_lot_id`)",
            "CONSTRAINT `FK_PARKING_LOT_TO_PARKING_LOWLAND_1` FOREIGN KEY (`parking_lot_id`) "
            "REFERENCES `parking_lot` (`parking_lot_id`)",
        ], [("parking_lot_id", None), ("lowland_score", 4)],
            [(r["parking_code"], r["lowland_raw"]) for _, r in frame.iterrows() if pd.notna(r["lowland_raw"])]),
        Table("parking_risk_result", [
            "`parking_lot_id` varchar(20) NOT NULL",
            "`analysis_year` smallint DEFAULT NULL",
            "`flood_risk_score` decimal(5,2) DEFAULT NULL",
            "`rainfall_risk_score` decimal(5,2) DEFAULT NULL",
            "`lowland_risk_score` decimal(5,2) DEFAULT NULL",
            "`total_risk_score` decimal(7,4) DEFAULT NULL",
            "`risk_grade` varchar(10) DEFAULT NULL",
            "`risk_rank` int DEFAULT NULL",
            "`calculated_at` datetime DEFAULT NULL",
            "`result_id` int DEFAULT NULL",
            "PRIMARY KEY (`parking_lot_id`)",
            "CONSTRAINT `FK_PARKING_LOT_TO_PARKING_RISK_RESULT_1` FOREIGN KEY (`parking_lot_id`) "
            "REFERENCES `parking_lot` (`parking_lot_id`)",
        ], [("parking_lot_id", None), ("analysis_year", None), ("flood_risk_score", 2), ("rainfall_risk_score", 2),
            ("lowland_risk_score", 2), ("total_risk_score", 4), ("risk_grade", None), ("risk_rank", None),
            ("calculated_at", None), ("result_id", None)],
            [(r["parking_code"], r["rain_year"], r["history"], r["rain"], r["terrain"], r["score"], r["level"],
              r["risk_rank"], CALCULATED_AT, r["id"]) for _, r in frame.iterrows()]),
        Table("rainfall_risk", [
            "`district_id` int NOT NULL",
            "`district_name` varchar(20) DEFAULT NULL",
            "`max_rain_1h` decimal(6,2) DEFAULT NULL",
            "`max_rain_3h` decimal(6,2) DEFAULT NULL",
            "`heavy_rain_days` int DEFAULT NULL",
            "`rainfall_score` decimal(5,2) DEFAULT NULL",
            "PRIMARY KEY (`district_id`)",
        ], [("district_id", None), ("district_name", None), ("max_rain_1h", 2), ("max_rain_3h", 2),
            ("heavy_rain_days", None), ("rainfall_score", 2)],
            [(r["지점"], r["자치구"], r["연최대1시간강수량(mm)"], r["3시간최대강수량(mm)"], r["연간집중호우발생빈도(일)"],
              r["강수위험도"]) for _, r in rain.iterrows()]),
    ]


def render(tables):
    parts = [notes(tables), HEADER] + [table_sql(table) for table in tables]
    parts += ["--", f"-- Dumping routines for database '{DATABASE}'", "--", FOOTER, "-- 생성 완료\n"]
    return "\n".join(parts)


def main():
    tables = build_tables()
    OUTPUT.write_text(render(tables), encoding="utf-8")
    for table in tables:
        print(f"{table.name}\t{len(table.rows)}")
    print(f"written\t{OUTPUT}")


if __name__ == "__main__":
    main()
