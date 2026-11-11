"""Code-native car/drop markers whose water level represents a relative score."""
from functools import lru_cache
from urllib.parse import quote
from math import isfinite

MARKER_VERSION = "glossy-car-score-v13"


def normalized_marker_score(score):
    try:
        value = float(score)
    except (TypeError, ValueError, OverflowError):
        return None
    if not isfinite(value):
        return None
    return max(0, min(100, int(value)))

RISK_BANDS = (
    (19, "매우 낮음", "#7dd3fc", "#effaff", "0–19"),
    (39, "낮음", "#4aaffe", "#e5f1f8", "20–39"),
    (59, "보통", "#168bff", "#dce8f3", "40–59"),
    (79, "높음", "#1056aa", "#d6e1ee", "60–79"),
    (100, "매우 높음", "#0b2254", "#d3ddeb", "80–100"),
)

COLORS = {band[1]: band[2] for band in RISK_BANDS}
COLORS["미산정"] = "#64748b"


def risk_band(score):
    value = normalized_marker_score(score)
    if value is None:
        return (100, "미산정", "#64748b", "#e2e8f0", "위험점수 없음")
    return next(band for band in RISK_BANDS if value <= band[0])


@lru_cache(maxsize=512)
def marker_svg(score, selected=False, color_min=0, color_max=100):
    color_score = float(score) if normalized_marker_score(score) is not None else 0
    score = normalized_marker_score(score)
    unscored = score is None
    drawing_score = 0 if unscored else score
    # Use vivid blue between sky and navy to avoid a grey intermediate color.
    t = max(0, min(1, (color_score - color_min) / (color_max - color_min))) if color_max > color_min else 0
    stops = ((125, 211, 252), (22, 139, 255)) if t <= 0.5 else ((22, 139, 255), (11, 34, 84))
    t = t * 2 if t <= 0.5 else (t - 0.5) * 2
    rgb = tuple(round(a + (b - a) * t) for a, b in zip(*stops))
    water_color = "#%02x%02x%02x" % rgb
    water_light = "#%02x%02x%02x" % tuple(round(c + (255 - c) * 0.35) for c in rgb)
    # Water height remains based on the risk score, not physical flood depth.
    water_y = 94 - drawing_score * 0.84
    edge = "#087bff" if selected else "#163c70"
    pin = "M48 7C26 7 10 23 10 44C10 65 31 87 48 103C65 87 86 65 86 44C86 23 70 7 48 7Z"
    wave = (f"M0 {water_y:.2f} Q12 {water_y-5:.2f} 24 {water_y:.2f} "
            f"T48 {water_y:.2f} T72 {water_y:.2f} T96 {water_y:.2f} V110H0Z")
    halo = f'<path d="{pin}" fill="none" stroke="#9bcfff" stroke-width="11"/>' if selected else ""
    water = f'<path d="{pin}" fill="#edf2f7"/>' if unscored else (
        f'<path d="{wave}" fill="url(#water)"/>'
        f'<path d="M18 {water_y+8:.2f} Q33 {water_y+3:.2f} 48 {water_y+8:.2f} T78 {water_y+8:.2f}" fill="none" stroke="white" stroke-opacity=".5" stroke-width="2"/>'
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="96" height="112" viewBox="0 0 96 112">
<defs>
<clipPath id="drop"><path d="{pin}"/></clipPath>
<linearGradient id="water" x1="0" y1="0" x2="0.35" y2="1">
<stop stop-color="{water_light}"/><stop offset="1" stop-color="{water_color}"/></linearGradient>
<linearGradient id="shell" x1="0" y1="0" x2="0.8" y2="1"><stop stop-color="#eaf7ff"/><stop offset="0.48" stop-color="#6fbaff"/><stop offset="1" stop-color="{water_color}"/></linearGradient>
<linearGradient id="gloss" x1="0" y1="0" x2="0" y2="1"><stop stop-color="white" stop-opacity=".96"/><stop offset="1" stop-color="#e4f2ff" stop-opacity=".65"/></linearGradient>
<linearGradient id="car" x1="0" y1="0" x2="0" y2="1"><stop stop-color="white"/><stop offset="1" stop-color="#eaf4ff"/></linearGradient>
</defs>
<ellipse cx="48" cy="106" rx="16" ry="3" fill="#06275c" opacity=".14"/>
{halo}<path d="{pin}" fill="url(#shell)"/>
<g clip-path="url(#drop)">
{water}
<path d="M13 32C17 14 33 7 48 7S78 14 83 33Q48 39 13 32Z" fill="url(#gloss)"/>
</g>
<path d="{pin}" fill="none" stroke="{edge}" stroke-width="2.8"/>
<g stroke="#064581" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
<path d="M22 37H29V43H22Q18 43 18 40Q18 37 22 37ZM67 37H74Q78 37 78 40Q78 43 74 43H67Z" fill="white"/>
<path d="M25 43L32 27Q34 24 38 24H58Q62 24 64 27L71 43Z" fill="url(#car)"/>
<path d="M26 42H70Q77 45 77 53V60Q77 64 72 64H24Q19 64 19 60V53Q19 46 26 42Z" fill="url(#car)"/>
<path d="M25 64V68Q25 70 28 70H32Q35 70 35 68V64M61 64V68Q61 70 64 70H68Q71 70 71 68V64" fill="#064581"/>
<path d="M26 49H36Q36 53 31 53Q26 53 26 49ZM60 49H70Q70 53 65 53Q60 53 60 49Z" fill="#064581" stroke="none"/>
</g>
</svg>'''


def marker_icon(score, selected=False, color_min=0, color_max=100):
    score = None if normalized_marker_score(score) is None else float(score)
    return {"url": "data:image/svg+xml;charset=utf-8," + quote(marker_svg(score, selected, color_min, color_max), safe=""),
            "width": 96, "height": 112, "anchorX": 48, "anchorY": 103, "mask": False}
