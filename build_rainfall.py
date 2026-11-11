"""Rebuild data/rainfall.csv from KMA hourly rainfall downloads (기상자료개방포털 CSV).

Download the 2025 hourly rainfall CSV (방재기상관측 AWS 시간자료, 종관기상관측 ASOS 시간자료 for
station 108) into data/kma_hourly/, then run from the project folder:

    python build_rainfall.py              # check, then write data/rainfall.csv
    python build_rainfall.py --check-only # check only

Each district uses one station (STATIONS below). Annual metrics come from
risk_model.annual_rainfall_metrics, the same rules the app documents. Rows already in
rainfall.csv must be reproduced exactly from the downloads before anything is written.
"""
import argparse
import csv
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from risk_model import annual_rainfall_metrics, rainfall_risk

ROOT = Path(__file__).resolve().parent
YEAR = 2025
# District -> KMA station number. The station named after the district when one exists,
# otherwise the station whose address (기상자료개방포털 관측지점정보, 2026-11-11) lies in that district.
STATIONS = {
    "강남구": 400, "강동구": 402, "강북구": 424, "강서구": 404, "관악구": 509, "광진구": 413,
    "구로구": 423, "금천구": 417, "노원구": 407, "도봉구": 406, "동대문구": 408, "동작구": 410,
    "서대문구": 412, "서초구": 401, "성동구": 421, "성북구": 414, "송파구": 403, "양천구": 405,
    "영등포구": 510, "용산구": 415, "은평구": 416, "종로구": 108, "중구": 419, "중랑구": 409,
}
COLUMNS = ["자치구", "지점", "연도", "연최대1시간강수량(mm)", "3시간최대강수량(mm)", "연간집중호우발생빈도(일)", "강수위험도"]
METRIC_COLUMNS = {"max_1h_mm": COLUMNS[3], "max_3h_mm": COLUMNS[4], "heavy_rain_days": COLUMNS[5]}


def read_text(path):
    raw = Path(path).read_bytes()
    for encoding in ("utf-8-sig", "cp949"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"{path}: UTF-8 또는 CP949 로 읽을 수 없습니다.")


def column(header, path, *candidates, required=True):
    for name in candidates:
        if name in header:
            return header.index(name)
    if required:
        raise ValueError(f"{path}: {candidates[0]} 열이 없습니다. 열 목록: {header}")
    return None


def read_hourly(paths):
    """Return {station: [(date, hour 1-24, mm), ...]} for observations inside YEAR.

    KMA hourly rows are stamped at the end of the hour, so 00:00 belongs to the previous
    date as hour 24. A blank rainfall cell means no rain unless its QC flag says missing (9).
    """
    samples = defaultdict(list)
    for path in paths:
        rows = list(csv.reader(read_text(path).splitlines()))
        header = [name.strip() for name in rows[0]]
        station_at = column(header, path, "지점", "지점번호")
        time_at = column(header, path, "일시", "시간")
        rain_at = column(header, path, "강수량(mm)")
        flag_at = next((i for i, name in enumerate(header) if "강수량" in name and "QC" in name.upper()), None)
        for line, row in enumerate(rows[1:], start=2):
            if not any(cell.strip() for cell in row):
                continue
            stamp = datetime.strptime(row[time_at].strip(), "%Y-%m-%d %H:%M")
            if stamp.minute:
                raise ValueError(f"{path}:{line}: 정시 자료가 아닙니다 ({row[time_at]}).")
            date, hour = (stamp - timedelta(days=1), 24) if stamp.hour == 0 else (stamp, stamp.hour)
            if date.year != YEAR:
                continue
            value = row[rain_at].strip()
            flag = row[flag_at].strip() if flag_at is not None and flag_at < len(row) else ""
            if flag == "9":
                continue  # 결측: leave the hour out so the day is reported as incomplete
            samples[int(row[station_at])].append((date.strftime("%Y-%m-%d"), hour, float(value) if value else 0.0))
    return samples


def gaps(observations):
    """Dates of YEAR that lack any of the 24 hourly observations."""
    hours = defaultdict(set)
    for date, hour, _ in observations:
        hours[date].add(hour)
    day, end, missing = datetime(YEAR, 1, 1), datetime(YEAR + 1, 1, 1), []
    while day < end:
        key = day.strftime("%Y-%m-%d")
        if len(hours.get(key, ())) != 24:
            missing.append(f"{key}({24 - len(hours.get(key, ()))}시간)")
        day += timedelta(days=1)
    return missing


def build(paths, existing_path):
    samples = read_hourly(paths)
    problems, rows = [], []
    for district, station in STATIONS.items():
        observations = samples.get(station, [])
        missing = gaps(observations)
        if missing:
            problems.append(f"{district}({station}): 관측이 빠진 날 {len(missing)}일 — {', '.join(missing[:5])}")
            continue
        metrics = annual_rainfall_metrics(observations)
        row = {"자치구": district, "지점": station, "연도": YEAR}
        row.update({METRIC_COLUMNS[key]: value for key, value in metrics.items()})
        row["강수위험도"] = round(rainfall_risk(metrics["max_1h_mm"], metrics["max_3h_mm"], metrics["heavy_rain_days"]), 2)
        rows.append(row)

    built = {row["자치구"]: row for row in rows}
    if existing_path.exists():
        with existing_path.open(encoding="utf-8-sig", newline="") as source:
            for old in csv.DictReader(source):
                new = built.get(old["자치구"])
                if new is None:
                    problems.append(f'{old["자치구"]}: 기존 행을 다시 계산하지 못했습니다.')
                    continue
                for name in COLUMNS[1:]:
                    if abs(float(old[name]) - float(new[name])) > 1e-9:
                        problems.append(f'{old["자치구"]} {name}: 기존 {old[name]} ≠ 다시 계산 {new[name]}')
    return sorted(rows, key=lambda row: row["자치구"]), problems


def number(value):
    """Integers as is; decimals with one place at least (57.0) and two at most (66.64)."""
    if not isinstance(value, float):
        return str(value)
    text = f"{value:.2f}".rstrip("0")
    return text + "0" if text.endswith(".") else text


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("inputs", nargs="*", help="기상청 시간자료 CSV 파일 또는 폴더 (기본: data/kma_hourly)")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "rainfall.csv")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args(argv)

    paths = []
    for item in map(Path, args.inputs or [ROOT / "data" / "kma_hourly"]):
        paths += sorted(item.glob("*.csv")) if item.is_dir() else [item]
    if not paths:
        print("기상청 시간자료 CSV 가 없습니다. data/kma_hourly/ 에 내려받은 파일을 두세요.", file=sys.stderr)
        return 2

    rows, problems = build(paths, args.output)
    for row in rows:
        print(" · ".join(f"{name} {number(row[name])}" for name in COLUMNS))
    if problems:
        print("\n중단 — 아래를 해결하기 전에는 강수 파일을 바꾸지 않습니다.", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1
    if args.check_only:
        print(f"\n확인 완료 — {len(rows)}개 구. --check-only 라서 파일은 그대로입니다.")
        return 0
    with args.output.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.writer(target, lineterminator="\n")
        writer.writerow(COLUMNS)
        writer.writerows([[number(row[name]) for name in COLUMNS] for row in rows])
    print(f"\n{args.output} 에 {len(rows)}개 구를 썼습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
