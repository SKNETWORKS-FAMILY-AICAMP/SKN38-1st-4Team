"""Service coverage: districts that have both parking records and a rainfall source row.

The app keeps all parking records in those districts, including locations without a final score.
Supporting measurements and the SQL dump use the full inventory.
"""
import csv
import re

from services.data_paths import PARKING_CSV, RAINFALL_CSV

PARKING_DATA_VERSION = "rainfall-districts-v4"

with PARKING_CSV.open(encoding="utf-8-sig", newline="") as source:
    PARKING_DISTRICTS = {
        match.group(1)
        for row in csv.DictReader(source)
        if (match := re.search(r"서울(?:특별시)?\s*([가-힣]+?구)", row["소재지주소"]))
    }
with RAINFALL_CSV.open(encoding="utf-8-sig", newline="") as source:
    RAINFALL_DISTRICTS = {row["자치구"] for row in csv.DictReader(source)}

SERVICE_DISTRICTS = tuple(sorted(PARKING_DISTRICTS & RAINFALL_DISTRICTS))
SERVICE_AREA = "·".join(SERVICE_DISTRICTS)
