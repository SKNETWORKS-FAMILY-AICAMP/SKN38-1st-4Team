"""Load the supplied parking inventory without inventing risk measurements."""
import pandas as pd
import streamlit as st

from services.data_paths import FLOOD_XLSX, LOWLAND_CSV, PARKING_CSV, RAINFALL_CSV, RISK_CONFIG, RISK_RESULTS_CSV
from services.risk_data import attach_risk_data
from services.service_config import PARKING_DATA_VERSION, SERVICE_DISTRICTS

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
    return frame


def parking_inventory():
    parking = load_parking_data(str(PARKING_CSV), PARKING_CSV.stat().st_mtime_ns)
    sources = (LOWLAND_CSV, RAINFALL_CSV, FLOOD_XLSX, RISK_CONFIG, RISK_RESULTS_CSV)
    versions = tuple((str(path), path.stat().st_mtime_ns) for path in sources)
    return attach_risk_data(parking, versions)


def service_inventory():
    """Return all parking locations in the five service districts."""
    frame = parking_inventory()
    return frame[frame["district"].isin(SERVICE_DISTRICTS)].reset_index(drop=True)
