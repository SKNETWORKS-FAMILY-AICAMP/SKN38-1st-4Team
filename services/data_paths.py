"""침착의 원본, 가공 데이터 및 설정 경로."""
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

PARKING_CSV = RAW_DIR / "seoul_parking.csv"
LOWLAND_CSV = RAW_DIR / "lowland.csv"
FLOOD_XLSX = RAW_DIR / "flood_depth.xlsx"
KMA_HOURLY_DIR = RAW_DIR / "kma_hourly"
RAINFALL_CSV = PROCESSED_DIR / "rainfall.csv"
RISK_CONFIG = DATA_DIR / "risk_config.json"
RISK_RESULTS_CSV = RAW_DIR / "parking_risk_result_recalculated.csv"
