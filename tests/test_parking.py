import pandas as pd
import pytest

from core.parking import COLUMNS, RISK_COLUMNS, ParkingDataError, load, validate


@pytest.fixture
def lots() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "parking_id": ["A", "B"],
            "name": ["가 주차장", "나 주차장"],
            "address": ["서울특별시 은평구 1", "서울특별시 강서구 2"],
            "lat": [37.60, 37.55],
            "lon": [126.92, 126.85],
            "rain_risk": [0.0, 1.0],
            "terrain_risk": [0.5, 0.25],
            "flood_history_risk": [1.0, 0.0],
        }
    )


def test_valid_data_comes_back_in_column_order(lots):
    shuffled = lots[list(reversed(lots.columns))].assign(extra=1)
    assert list(validate(shuffled).columns) == list(COLUMNS)


@pytest.mark.parametrize("column", COLUMNS)
def test_missing_column_is_an_error(lots, column):
    with pytest.raises(ParkingDataError, match=column):
        validate(lots.drop(columns=column))


def test_empty_data_is_an_error(lots):
    with pytest.raises(ParkingDataError):
        validate(lots.iloc[0:0])


def test_blank_value_is_an_error(lots):
    lots.loc[0, "name"] = None
    with pytest.raises(ParkingDataError, match="name"):
        validate(lots)


def test_duplicate_id_is_an_error(lots):
    lots.loc[1, "parking_id"] = "A"
    with pytest.raises(ParkingDataError, match="겹칩니다"):
        validate(lots)


@pytest.mark.parametrize("column", RISK_COLUMNS)
@pytest.mark.parametrize("value", [-0.01, 1.01])
def test_risk_outside_0_to_1_is_an_error(lots, column, value):
    lots[column] = lots[column].astype(float)
    lots.loc[1, column] = value
    with pytest.raises(ParkingDataError, match=column):
        validate(lots)


def test_non_numeric_risk_is_an_error(lots):
    lots["rain_risk"] = ["0.1", "높음"]
    with pytest.raises(ParkingDataError, match="rain_risk"):
        validate(lots)


def test_swapped_coordinates_are_an_error(lots):
    lots[["lat", "lon"]] = lots[["lon", "lat"]].to_numpy()
    with pytest.raises(ParkingDataError, match="lat"):
        validate(lots)


def test_load_reads_the_app_data():
    df = load()
    assert len(df) > 0
    assert list(df.columns) == list(COLUMNS)
