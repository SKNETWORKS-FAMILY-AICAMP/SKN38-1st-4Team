"""Join source measurements and apply only explicitly configured scoring rules."""
import json
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

import numpy as np
import pandas as pd
import streamlit as st

from risk_model import distance_score, normalize_by_max, rainfall_risk, weighted_risk

RISK_DATA_VERSION = "calculated-risk-v1"


def read_flood_points(path):
    """Read values from the supplied single-sheet XLSX; never execute formulas."""
    ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with ZipFile(path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(item.itertext()) for item in root.findall("s:si", ns)]
        root = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    rows = []
    for row in root.findall("s:sheetData/s:row", ns):
        values = {}
        for cell in row.findall("s:c", ns):
            column = "".join(c for c in cell.attrib["r"] if c.isalpha())
            value = cell.findtext("s:v", default="", namespaces=ns)
            if cell.attrib.get("t") == "s":
                value = shared[int(value)]
            elif cell.attrib.get("t") == "inlineStr":
                value = "".join(cell.find("s:is", ns).itertext())
            values[column] = value
        rows.append(values)
    headers = rows.pop(0)
    frame = pd.DataFrame([{headers[col]: value for col, value in row.items()} for row in rows])
    frame = frame.rename(columns={"위도": "lat", "경도": "lon", "침수심": "depth"})
    for column in ("lat", "lon", "depth"):
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    if frame.empty or not (frame["lat"].between(-90, 90) & frame["lon"].between(-180, 180) & frame["depth"].ge(0)).all():
        raise ValueError("침수심 원본의 좌표·침수심을 확인하세요.")
    return frame


@st.cache_data
def attach_risk_data(parking, data_dir, source_versions):
    base = Path(data_dir)
    config = json.loads((base / "risk_config.json").read_text(encoding="utf-8"))
    frame = parking.copy()
    terrain = pd.read_csv(base / "lowland.csv", encoding="utf-8-sig", dtype=str)
    key = "주차장관리번호(수정)"
    terrain = terrain[terrain[key].isin(frame["parking_code"])].copy()
    if terrain[key].duplicated().any():
        raise ValueError("저지대 원본의 주차장 관리번호가 중복되었습니다.")
    terrain_values = pd.to_numeric(terrain.iloc[:, -1], errors="raise")
    terrain_map = pd.Series(terrain_values.to_numpy(), index=terrain[key])
    frame["lowland_raw"] = frame["parking_code"].map(terrain_map)
    frame["terrain"] = frame["lowland_raw"]

    rain = pd.read_csv(base / "rainfall.csv", encoding="utf-8-sig")
    if rain["자치구"].duplicated().any() or rain["연도"].nunique() != 1:
        raise ValueError("강수 원본은 한 해의 자치구별 고유 행이어야 합니다.")
    rain["calculated_risk"] = rain.apply(lambda row: rainfall_risk(
        row["연최대1시간강수량(mm)"], row["3시간최대강수량(mm)"], row["연간집중호우발생빈도(일)"]), axis=1)
    if not np.allclose(rain["calculated_risk"], rain["강수위험도"], atol=1e-6, rtol=0):
        raise ValueError("강수위험도 원본과 0.4·0.4·0.2 계산 결과가 다릅니다.")
    rain_by_district = rain.set_index("자치구")
    frame["rain_raw"] = frame["district"].map(rain_by_district["calculated_risk"])
    frame["rain_year"] = frame["district"].map(rain_by_district["연도"])
    for target, source in [("rain_max_1h_mm", "연최대1시간강수량(mm)"), ("rain_max_3h_mm", "3시간최대강수량(mm)"), ("heavy_rain_days", "연간집중호우발생빈도(일)")]:
        frame[target] = frame["district"].map(rain_by_district[source])
    normalization = config.get("rainfall_normalization")
    rain_max = float(rain["calculated_risk"].max()) if normalization == "source_max" else 100 if normalization == "hundred" else None
    frame["rain"] = frame["rain_raw"].map(lambda value: normalize_by_max(value, rain_max))
    frame["rain"] = pd.to_numeric(frame["rain"], errors="coerce") * 100

    flood = read_flood_points(base / "flood_depth.xlsx")
    flood_districts = flood["정제주소"].str.extract(r"서울(?:특별시)?\s*([가-힣]+?구)", expand=False)
    flood = flood[flood_districts.isin(frame["district"].unique())].copy()
    depth_max = float(flood["depth"].max())
    frame["depth"] = float("nan")
    frame["distance_risk"] = float("nan")
    frame["history"] = float("nan")
    frame["score"] = float("nan")
    if config.get("distance_method") == "representative_point":
        # The source has representative coordinates, not polygon boundaries.
        # This data-based estimate uses source coordinates, not polygon geometry.
        lat1 = np.radians(frame["lat"].to_numpy())[:, None]
        lon1 = np.radians(frame["lon"].to_numpy())[:, None]
        lat2 = np.radians(flood["lat"].to_numpy())[None, :]
        lon2 = np.radians(flood["lon"].to_numpy())[None, :]
        haversine = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
        distances = 6371000 * 2 * np.arcsin(np.sqrt(np.clip(haversine, 0, 1)))
        nearest = distances.argmin(axis=1)
        frame["flood_distance_m"] = distances[np.arange(len(frame)), nearest]
        frame["nearest_flood_id"] = flood.iloc[nearest]["flood_id"].to_numpy()
        frame["depth_raw"] = flood.iloc[nearest]["depth"].to_numpy()
        frame["depth"] = frame["depth_raw"].map(lambda value: normalize_by_max(value, depth_max)) * 100
        distance_max = float(frame["flood_distance_m"].max())
        frame["distance_risk"] = pd.to_numeric(frame["flood_distance_m"].map(
            lambda value: distance_score(value, distance_max, config.get("distance_direction"))), errors="coerce") * 100
        frame["history"] = frame["depth"] * 0.6 + frame["distance_risk"] * 0.4
        frame["distance_reference_max_m"] = distance_max

    frame["depth_reference_max"] = depth_max
    frame["rain_reference_max"] = rain_max
    frame["risk_method"] = "대표좌표 기반 추정"

    def calculate(row):
        return weighted_risk(row["depth"] / 100, row["distance_risk"] / 100, row["rain"] / 100, normalize_by_max(row["lowland_raw"], config["lowland_reference_max"]))

    frame["score"] = pd.to_numeric(frame.apply(calculate, axis=1), errors="coerce")
    def missing_reason(row):
        reasons = []
        if pd.isna(row["rain_raw"]):
            reasons.append(f'{row["district"]} 강수 데이터 없음')
        if normalization not in ("source_max", "hundred"):
            reasons.append("강수 정규화 기준 확인 중")
        if pd.isna(row["lowland_raw"]):
            reasons.append("저지대 점수 없음")
        if config.get("distance_method") != "representative_point":
            reasons.append("침수구역 최소거리 데이터·방식 확인 중")
        elif config.get("distance_direction") not in ("nearer_higher", "farther_higher"):
            reasons.append("거리 정규화 방향 확인 중")
        return " · ".join(reasons)

    frame["risk_missing_reason"] = frame.apply(missing_reason, axis=1)
    return frame
