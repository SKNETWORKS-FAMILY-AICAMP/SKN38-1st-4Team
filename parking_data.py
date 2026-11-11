"""Load the supplied parking inventory without inventing risk measurements."""
from pathlib import Path

import pandas as pd
import streamlit as st
from risk_data import attach_risk_data
from service_config import PARKING_DATA_VERSION, SERVICE_DISTRICTS

DATA_VERSION = PARKING_DATA_VERSION


@st.cache_data
def load_parking_data(path, modified_at):
    frame = pd.read_csv(path, encoding="utf-8-sig", dtype=str).rename(columns={
        "주차장관리번호(수정)": "parking_code", "주차장명": "name",
        "소재지주소": "address", "위도": "lat", "경도": "lon",
    })
    frame.insert(0, "id", range(1, len(frame) + 1))
    frame["district"] = frame["address"].str.extract(r"서울(?:특별시)?\s*([가-힣]+?구)", expand=False).fillna("구 미확인")
    for column in ("lat", "lon"):
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    if not (frame["lat"].between(-90, 90) & frame["lon"].between(-180, 180)).all():
        raise ValueError("주차장 목록에 유효하지 않은 좌표가 있습니다.")
    for column in ("score", "rain", "terrain", "history"):
        frame[column] = float("nan")
    return frame


def parking_inventory():
    path = Path(__file__).parent / "data" / "seoul_parking.csv"
    parking = load_parking_data(str(path), path.stat().st_mtime_ns)
    sources = ["lowland.csv", "rainfall.csv", "flood_depth.xlsx", "risk_config.json"]
    versions = tuple((name, (path.parent / name).stat().st_mtime_ns) for name in sources)
    return attach_risk_data(parking, str(path.parent), versions)


def service_inventory():
    """Parking the app shows: service districts only, scored against the full inventory."""
    frame = parking_inventory()
    return frame[frame["district"].isin(SERVICE_DISTRICTS)].reset_index(drop=True)
