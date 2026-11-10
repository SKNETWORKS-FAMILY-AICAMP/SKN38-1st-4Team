import pandas as pd
import pytest

from analysis.build_parking_risk import _read, build, district_of
from core.parking import load


@pytest.fixture
def raw() -> dict[str, pd.DataFrame]:
    lots = pd.DataFrame(
        {
            "parking_lot_id": ["111-1", "122-1", "111-2"],
            "parking_name": ["불광", "역삼", "갈현"],
            "address": ["서울특별시 은평구 불광동 1", "서울특별시 강남구 역삼동 2", "서울특별시 은평구 갈현동 3"],
            "latitude": [37.61, 37.50, 37.62],
            "longitude": [126.93, 127.04, 126.91],
        }
    )
    results = pd.DataFrame(
        {
            "parking_lot_id": ["111-1", "122-1", "111-2"],
            "rainfall_risk_score": [91.0, 0.0, 91.0],
            "lowland_risk_score": [100.0, 5.0, 12.34],
            "flood_risk_score": [48.73, 0.0, 0.0],
            "total_risk_score": [74.23, 1.25, 30.39],
        }
    )
    rainfall = pd.DataFrame({"district_name": ["은평구"], "rainfall_score": [91.0]})
    return {"lots": lots, "results": results, "rainfall": rainfall}


def test_district_is_read_from_address():
    addresses = pd.Series(["서울특별시 서대문구 홍은동 1", "경기도 고양시 덕양구 1"])
    assert district_of(addresses).tolist()[0] == "서대문구"
    assert pd.isna(district_of(addresses).tolist()[1])


def test_only_districts_with_rainfall_data_are_kept(raw):
    df = build(raw["lots"], raw["results"], raw["rainfall"])
    assert df["parking_id"].tolist() == ["111-1", "111-2"]


def test_scores_are_scaled_to_0_1_under_app_column_names(raw):
    row = build(raw["lots"], raw["results"], raw["rainfall"]).iloc[0]
    assert row["name"] == "불광"
    assert (row["lat"], row["lon"]) == (37.61, 126.93)
    assert row["rain_risk"] == pytest.approx(0.91)
    assert row["terrain_risk"] == pytest.approx(1.0)
    assert row["flood_history_risk"] == pytest.approx(0.4873)


def test_parking_lot_without_scores_is_an_error(raw):
    results = raw["results"][raw["results"]["parking_lot_id"] != "111-2"]
    with pytest.raises(ValueError, match="111-2"):
        build(raw["lots"], results, raw["rainfall"])


def test_app_data_is_up_to_date_with_raw_data():
    expected = build(_read("parking_lot.csv"), _read("parking_risk_result.csv"), _read("rainfall_risk.csv"))
    pd.testing.assert_frame_equal(load(), expected)
