"""Convert dataframe missing/non-finite numbers to strict JSON null values."""
import json


def json_records(frame):
    # pandas' JSON encoder handles every numeric column, including NaN/Infinity.
    # Returning ordinary records also prevents a later encoder seeing raw NaNs.
    records = json.loads(frame.to_json(orient="records", force_ascii=False, double_precision=15))
    json.dumps(records, allow_nan=False)
    return records
