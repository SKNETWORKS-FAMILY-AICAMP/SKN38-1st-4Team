"""앱 입력 자료(data/parking_risk.csv) 읽기와 검증.

형식은 docs/risk-index.md 「앱 입력 자료」를 따른다.
"""

from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "parking_risk.csv"

ID_COLUMN = "parking_id"
TEXT_COLUMNS = (ID_COLUMN, "name", "address")
RISK_COLUMNS = ("rain_risk", "terrain_risk", "flood_history_risk")
COLUMNS = (*TEXT_COLUMNS, "lat", "lon", *RISK_COLUMNS)

# 서울을 넉넉히 감싸는 범위. 위도·경도가 뒤바뀌거나 잘못 들어간 값을 잡는다.
LAT_RANGE = (37.4, 37.75)
LON_RANGE = (126.7, 127.3)


class ParkingDataError(ValueError):
    """앱 입력 자료가 형식에 맞지 않을 때 낸다."""


def _ids(df: pd.DataFrame, mask: pd.Series) -> str:
    return ", ".join(df.loc[mask, ID_COLUMN].astype(str).head(5))


def validate(df: pd.DataFrame) -> pd.DataFrame:
    """형식이 맞으면 정해진 열 순서로 돌려주고, 틀리면 ParkingDataError 를 낸다."""
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ParkingDataError(f"꼭 있어야 할 열이 없습니다: {', '.join(missing)}")
    if df.empty:
        raise ParkingDataError("주차장이 한 곳도 없습니다.")

    blank = [c for c in COLUMNS if df[c].isna().any()]
    if blank:
        raise ParkingDataError(f"빈 값이 있는 열: {', '.join(blank)}")

    duplicated = df[ID_COLUMN].duplicated(keep=False)
    if duplicated.any():
        raise ParkingDataError(f"주차장 번호가 겹칩니다: {_ids(df, duplicated)}")

    for column in ("lat", "lon", *RISK_COLUMNS):
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ParkingDataError(f"{column} 열에 숫자가 아닌 값이 있습니다.")

    for column in RISK_COLUMNS:
        outside = ~df[column].between(0, 1)
        if outside.any():
            raise ParkingDataError(f"{column} 값이 0~1 을 벗어났습니다: {_ids(df, outside)}")

    for column, (low, high) in (("lat", LAT_RANGE), ("lon", LON_RANGE)):
        outside = ~df[column].between(low, high)
        if outside.any():
            raise ParkingDataError(f"{column} 값이 서울 범위({low}~{high})를 벗어났습니다: {_ids(df, outside)}")

    return df.loc[:, list(COLUMNS)].reset_index(drop=True)


def load(path: Path = DATA_PATH) -> pd.DataFrame:
    """앱 입력 자료를 읽어 검증한 뒤 돌려준다."""
    df = pd.read_csv(path, encoding="utf-8-sig", dtype={c: str for c in TEXT_COLUMNS})
    return validate(df)
