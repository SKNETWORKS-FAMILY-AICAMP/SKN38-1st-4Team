"""Service coverage: districts that have both parking records and a rainfall source row.

Every parking record is still scored, so normalization references and the SQL dump keep using
the full inventory. The app shows only these districts, where all four score inputs exist.
A district enters the service when its row is added to data/rainfall.csv (build_rainfall.py).
"""
import csv
from pathlib import Path
import re

PARKING_DATA_VERSION = "rainfall-districts-v4"
DATA = Path(__file__).parent / "data"

with (DATA / "seoul_parking.csv").open(encoding="utf-8-sig", newline="") as source:
    PARKING_DISTRICTS = {
        match.group(1)
        for row in csv.DictReader(source)
        if (match := re.search(r"서울(?:특별시)?\s*([가-힣]+?구)", row["소재지주소"]))
    }
with (DATA / "rainfall.csv").open(encoding="utf-8-sig", newline="") as source:
    RAINFALL_DISTRICTS = {row["자치구"] for row in csv.DictReader(source)}

SERVICE_DISTRICTS = tuple(sorted(PARKING_DISTRICTS & RAINFALL_DISTRICTS))
