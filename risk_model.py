"""The agreed risk formula. All four score inputs use the 0–1 scale."""
from collections import defaultdict
from math import isfinite


def finite_number(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if isfinite(value) else None


def normalize_by_max(value, maximum):
    value, maximum = finite_number(value), finite_number(maximum)
    if value is None or maximum is None or maximum <= 0:
        return None
    if value < 0 or value > maximum:
        raise ValueError("정규화 값은 0 이상, 기준 최대값 이하여야 합니다.")
    return value / maximum


def distance_score(distance_m, maximum_m, direction):
    normalized = normalize_by_max(distance_m, maximum_m)
    if normalized is None:
        return None
    if direction == "nearer_higher":
        return 1 - normalized
    if direction == "farther_higher":
        return normalized
    return None


def rainfall_risk(max_1h_mm, max_3h_mm, heavy_rain_days):
    values = [finite_number(v) for v in (max_1h_mm, max_3h_mm, heavy_rain_days)]
    if any(v is None for v in values):
        return None
    if any(v < 0 for v in values) or not values[2].is_integer():
        raise ValueError("강수량은 음수일 수 없으며 집중호우 빈도는 일 단위 정수입니다.")
    return values[0] * 0.4 + values[1] * 0.4 + values[2] * 0.2


def weighted_risk(depth, distance, rain, lowland):
    """Return a 0–100 display score; preserve missing inputs as unavailable."""
    values = [finite_number(v) for v in (depth, distance, rain, lowland)]
    if any(v is None for v in values):
        return None
    if any(not 0 <= v <= 1 for v in values):
        raise ValueError("위험점수 입력은 모두 0~1이어야 합니다.")
    depth, distance, rain, lowland = values
    return ((depth * 0.6 + distance * 0.4) * 0.45 + rain * 0.3 + lowland * 0.25) * 100


def annual_rainfall_metrics(samples):
    """Aggregate (date, hour, rainfall_mm), with hours 1–24 on the observation date.

    Each date must contain 24 distinct hourly observations. Windows never cross
    dates. A day contributes at most one occurrence, strictly above 60 mm.
    Missing observations remain an error instead of being treated as zero rain.
    """
    days = defaultdict(dict)
    for date, hour, rainfall_mm in samples:
        if type(hour) is not int or not 1 <= hour <= 24:
            raise ValueError("관측 시각은 해당 날짜의 1~24시로 입력하세요.")
        value = finite_number(rainfall_mm)
        if value is None or value < 0 or hour in days[date]:
            raise ValueError("결측·음수 강수량이나 중복 시각이 있습니다.")
        days[date][hour] = value
    if not days:
        return {"max_1h_mm": None, "max_3h_mm": None, "heavy_rain_days": None}
    if len({str(date)[:4] for date in days}) != 1:
        raise ValueError("연간 계산에는 한 해의 관측값만 입력하세요.")
    if any(len(hours) != 24 for hours in days.values()):
        raise ValueError("하루 24시간 관측값이 필요합니다. 결측값을 0으로 대체하지 않습니다.")
    daily_maxima = [max(sum(hours[h + offset] for offset in range(3)) for h in range(1, 23)) for hours in days.values()]
    return {
        "max_1h_mm": max(max(hours.values()) for hours in days.values()),
        "max_3h_mm": max(daily_maxima),
        "heavy_rain_days": sum(value > 60 for value in daily_maxima),
    }
