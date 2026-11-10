"""팀 분석 결과(data/raw/)로 앱 입력 자료(data/parking_risk.csv)를 만든다.

실행: python -m analysis.build_parking_risk

- 분석 대상 지역은 강수 자료(rainfall_risk.csv)가 있는 자치구다. 그 밖의 주차장은 넣지 않는다.
- 세 위험 점수(0~100)를 100 으로 나눠 0~1 로 넣는다.
- 받은 자료의 종합 점수·등급·순위는 쓰지 않는다. 앱이 core/risk.py 의 가중치와 등급 경계로 다시 계산한다.
"""

from pathlib import Path

import pandas as pd

from core.parking import DATA_PATH, validate

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

# 받은 자료의 점수 열(0~100) → 앱 입력 자료의 위험 열(0~1)
SCORE_COLUMNS = {
    "rainfall_risk_score": "rain_risk",
    "lowland_risk_score": "terrain_risk",
    "flood_risk_score": "flood_history_risk",
}


def district_of(address: pd.Series) -> pd.Series:
    """「서울특별시 은평구 …」 주소에서 자치구 이름을 꺼낸다. 형식이 다르면 빈 값."""
    return address.str.extract(r"^서울특별시\s+(\S+구)", expand=False)


def build(lots: pd.DataFrame, results: pd.DataFrame, rainfall: pd.DataFrame) -> pd.DataFrame:
    """주차장·위험 점수·강수 표를 합쳐 앱 입력 자료 형식으로 만든다."""
    in_scope = lots[district_of(lots["address"]).isin(set(rainfall["district_name"]))]
    merged = in_scope.merge(results, on="parking_lot_id", how="left", validate="one_to_one")

    no_score = merged[list(SCORE_COLUMNS)].isna().any(axis=1)
    if no_score.any():
        ids = ", ".join(merged.loc[no_score, "parking_lot_id"].head(5))
        raise ValueError(f"위험 점수가 없는 주차장이 있습니다: {ids}")

    out = pd.DataFrame(
        {
            "parking_id": merged["parking_lot_id"],
            "name": merged["parking_name"],
            "address": merged["address"],
            "lat": merged["latitude"],
            "lon": merged["longitude"],
            **{new: (merged[old] / 100).round(4) for old, new in SCORE_COLUMNS.items()},
        }
    )
    return validate(out.sort_values("parking_id"))


def _read(name: str) -> pd.DataFrame:
    return pd.read_csv(RAW_DIR / name, encoding="utf-8-sig", dtype={"parking_lot_id": str})


def main() -> None:
    df = build(_read("parking_lot.csv"), _read("parking_risk_result.csv"), _read("rainfall_risk.csv"))
    # BOM 을 붙여 엑셀에서 열어도 한글이 깨지지 않게 한다.
    df.to_csv(DATA_PATH, index=False, encoding="utf-8-sig")
    print(f"{DATA_PATH.name}: 주차장 {len(df)}곳")


if __name__ == "__main__":
    main()
