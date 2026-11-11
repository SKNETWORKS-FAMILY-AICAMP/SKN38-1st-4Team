"""침착: Streamlit frontend using explicitly labeled demonstration data.

Python + Streamlit 전용 버전: HTML/CSS/JS 파일과 unsafe_allow_html 없이 동작합니다.
"""
import os
from pathlib import Path

# Support VS Code's "Run Python File" as well as `streamlit run app.py`.
if __name__ == "__main__":
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        direct_run = get_script_run_ctx(suppress_warning=True) is None
    except ModuleNotFoundError as error:
        if error.name != "streamlit":
            raise
        direct_run = True

    if direct_run:
        app_path = Path(__file__).resolve()
        os.chdir(app_path.parent)
        if os.name == "nt":
            import subprocess

            raise SystemExit(subprocess.call(
                [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", "실행.bat"],
                cwd=app_path.parent,
            ))
        from launch import main
        raise SystemExit(main())

from math import radians, sin, cos, atan2, sqrt

import altair as alt
import pandas as pd
import streamlit as st

import parking_marker as marker_source
from parking_data import service_inventory
from parking_map import render_map
from service_config import PARKING_DATA_VERSION, SERVICE_DISTRICTS

risk_band = marker_source.risk_band
RISK_BANDS = marker_source.RISK_BANDS

st.set_page_config(page_title="침착 | 주차장 침수 위험도", page_icon="💧", layout="wide", initial_sidebar_state="expanded")
# 카카오 길찾기(현재 비활성) 키는 코드에 적지 않고 환경 변수에서만 읽습니다.
st.session_state["_kakao_rest_api_key"] = os.environ.get("KAKAO_REST_API_KEY", "").strip()

NOTE = "침수 대표좌표와 지정 가중식 기반 추정 위험도 · 실시간 침수 예측이 아닙니다."
ASSETS = Path(__file__).resolve().parent / "assets"
LOGO = str(ASSETS / "chimchak-logo.png")
FRAME = service_inventory()
SERVICE_AREA = "·".join(SERVICE_DISTRICTS)
scored_values = FRAME["score"].dropna()
COLOR_MIN = float(scored_values.min()) if not scored_values.empty else 0
COLOR_MAX = float(scored_values.max()) if not scored_values.empty else 100


def marker_icon(score, selected=False):
    return marker_source.marker_icon(score, selected, color_min=COLOR_MIN, color_max=COLOR_MAX)


COLORS = {band[1]: band[2] for band in RISK_BANDS}
COLORS["미산정"] = "#64748b"
FAQ = [
    ("위험지수", "위험지수는 무엇을 의미하나요?", "침수심·최소거리 복합점수 45%, 강수위험도 30%, 저지대 점수 25%를 합산하는 상대 위험도입니다. 침수 복합점수 안에서는 침수심 60%, 거리 40%를 사용합니다. 필요한 데이터가 없거나 정규화 기준이 미확정이면 미산정으로 표시합니다."),
    ("위험지수", "위험도가 낮으면 안전한가요?", "상대적으로 낮은 점수는 안전을 보장하지 않습니다. 현장 통제와 기상특보를 함께 확인하세요."),
    ("서비스 이용", "실시간 침수 상황을 알 수 있나요?", "실시간 상황을 관측하거나 미래 침수를 예측하지 않습니다. 2025년 데이터 분석을 전제로 한 프로토타입입니다."),
    ("서비스 이용", "위치를 허용하지 않아도 이용할 수 있나요?", "네. 처음에는 색동공원(강북구)을 임시 기준점으로 사용합니다. 지도 위 ‘◎ 현재 위치’에서 ‘GPS로 내 위치 찾기’를 누르고 브라우저 위치 권한을 허용하면 기기 위치를, 허용하지 않으면 기준 위치를 고르거나 좌표를 입력해 검색 반경, 주변 주차장 목록과 거리를 그 위치 기준으로 갱신합니다."),
    ("데이터", "어떤 데이터와 계산식을 사용하나요?", "제공된 주차장 목록·저지대 점수·자치구별 강수량·침수심 파일을 사용합니다. 집중호우는 같은 날짜의 연속 3시간 강수량이 60mm를 초과한 날을 하루 한 번 집계합니다. 강수 원본이 없는 구의 값을 0으로 대체하지 않습니다."),
]


def level(value):
    if pd.isna(value):
        return "미산정"
    return risk_band(value)[1]


def distance(lat, lon, target_lat, target_lon):
    """Straight-line distance in meters, not walking/driving distance."""
    a1, a2 = radians(lat), radians(target_lat)
    dlat, dlon = a2 - a1, radians(target_lon - lon)
    a = sin(dlat / 2) ** 2 + cos(a1) * cos(a2) * sin(dlon / 2) ** 2
    return 6371000 * 2 * atan2(sqrt(a), sqrt(max(0, 1 - a)))


def badge(value):
    text = level(value)
    st.badge(text, color="gray" if text == "미산정" else "blue")


# Kakao navigation is temporarily disabled; implementation is in kakao_panel.py.

def detail(row):
    st.subheader(row["name"])
    st.caption(row["address"])
    st.caption(f'주차장관리번호: {row["parking_code"]}')
    st.metric("상대적 침수 위험지수", "미산정" if pd.isna(row["score"]) else f'{row["score"]:.1f} / 100')
    badge(row["score"])
    st.caption(NOTE)
    st.caption(f'기준점에서 {row["distance"]:,.0f}m · 직선거리')
    st.markdown("#### 위험지수 구성")
    for label, key in [("침수심 (최종 가중치 27%)", "depth"), ("침수 대표좌표 거리 (18%)", "distance_risk"), ("강수위험도 (30%)", "rain"), ("저지대 상대점수 (25%)", "terrain")]:
        if pd.isna(row[key]):
            st.write(f"{label} · **미산정**")
        else:
            st.write(f'{label} · **{row[key]:.1f} / 100**')
            st.progress(float(row[key]) / 100)
    if pd.notna(row["rain_raw"]):
        st.caption(f'강수 원값 {row["rain_raw"]:.1f} · {int(row["rain_year"])}년 · 1시간 최대 {row["rain_max_1h_mm"]:g}mm · 3시간 최대 {row["rain_max_3h_mm"]:g}mm · 집중호우 {int(row["heavy_rain_days"])}일')
    if pd.notna(row.get("flood_distance_m", float("nan"))):
        st.caption(f'가장 가까운 침수 대표좌표까지 {row["flood_distance_m"]:,.0f}m · 구역 경계까지의 거리가 아닙니다.')
        st.caption(f'정규화 기준: 침수심 {row["depth_reference_max"]:g} · 최대 최소거리 {row["distance_reference_max_m"]:,.0f}m · 강수위험도 {row["rain_reference_max"]:g}')
    if pd.isna(row["score"]):
        st.info(row["risk_missing_reason"] or "위험도 계산에 필요한 입력을 확인 중입니다.")
    st.info("점수가 낮더라도 안전을 보장하지 않습니다. 현장 상황과 기상특보를 확인하세요.")


def toggle_compare(identifier):
    current = st.session_state["compare_ids"]
    if identifier in current:
        st.session_state["compare_ids"] = [i for i in current if i != identifier]
    elif len(current) < 3:
        st.session_state["compare_ids"] = current + [identifier]


def sync_compare():
    st.session_state["compare_ids"] = list(st.session_state["compare_picker"])


def legend(map_data, per_row=6):
    """기존 water-legend: 점수 구간별 자동차·물방울 핀 + 미산정 핀."""
    items = []
    if map_data["score"].notna().any():
        items += [(marker_source.marker_svg(float(score), False, COLOR_MIN, COLOR_MAX), label, interval)
                  for score, label, _, _, interval in RISK_BANDS]
    if map_data["score"].isna().any():
        items.append((marker_source.marker_svg(None, False, COLOR_MIN, COLOR_MAX), "미산정", "입력 데이터 확인 중"))
    if not items:
        return
    with st.container(border=True):
        per_row = min(per_row, len(items))
        for start in range(0, len(items), per_row):
            for column, (svg, label, interval) in zip(st.columns(per_row), items[start:start + per_row]):
                with column:
                    icon, text = st.columns([1, 2.4], vertical_alignment="center")
                    icon.image(svg, width=34)
                    text.markdown(f"**{label}**  \n:gray[{interval}]")


# ---------------- 상단 브랜드 바 ----------------
brand_logo, brand_text = st.columns([1, 3], vertical_alignment="center")
brand_logo.image(LOGO, width=138)
brand_text.caption("침수 위험을 살피는 주차 습관")
st.divider()

unscored_count = int(FRAME["score"].isna().sum())
st.caption(f'서비스 지역 {len(SERVICE_DISTRICTS)}개 구({SERVICE_AREA}) · 주차장 {len(FRAME):,}개 · 추정 위험점수 산정 {FRAME["score"].notna().sum():,}개'
           + (f" · 미산정 {unscored_count:,}개" if unscored_count else ""))
st.caption("강수 자료가 있는 구부터 서비스합니다. 내 주변 또는 구별 보기로 확인하세요.")

if st.session_state.get("parking_dataset_version") != PARKING_DATA_VERSION:
    st.session_state.update(parking_dataset_version=PARKING_DATA_VERSION, compare_ids=[], selected_id=None, parking_district=SERVICE_DISTRICTS[0])
if "compare_ids" not in st.session_state:
    st.session_state["compare_ids"] = [1, 2]
if "selected_id" not in st.session_state:
    st.session_state["selected_id"] = None

# The same reference point drives search, detail, comparison, and distances.
# Temporary preview: 4 scored parking locations within 300m of Saekdong Park.
preview_location = (37.6333382, 127.0206239)
if st.session_state.get("preview_location_version") != "gangbuk-scored-parking-v3":
    st.session_state.update(
        preview_location_version="gangbuk-scored-parking-v3",
        current_location=preview_location,
        parking_view_request="nearby",
        selected_id=None,
    )
lat, lon = st.session_state.get("current_location", preview_location)
with st.sidebar:
    st.image(LOGO, width=170)
    st.caption("침수 위험을 살피는 주차 습관")
    st.session_state.setdefault("sidebar_page", "홈 (주차장 탐색)")
    for item in ["홈 (주차장 탐색)", "FAQ", "분석 데이터 결과"]:
        st.button(item, key=f"nav_{item}", width="stretch",
                  type="primary" if st.session_state["sidebar_page"] == item else "secondary",
                  on_click=st.session_state.__setitem__, args=("sidebar_page", item))
    page = st.session_state["sidebar_page"]
    st.divider()
    st.caption(NOTE)
frame = FRAME.copy()
frame["distance"] = frame.apply(lambda p: distance(lat, lon, p["lat"], p["lon"]), axis=1)
frame["level"] = frame["score"].map(level)

if page == "홈 (주차장 탐색)":
    # ---------------- 히어로 ----------------
    with st.container(border=True):
        hero_copy, hero_art = st.columns([1.8, 1], vertical_alignment="center", gap="large")
        with hero_copy:
            st.markdown(":blue[**PARK WITH INSIGHT**]")
            st.markdown("# 비 오는 날에도,\n# 주차 전 한 번 더 :blue[침착.]")
            st.markdown(":gray[내 주변 주차장의 침수 위험을 살펴보고,]  \n:gray[데이터를 바탕으로 더 신중하게 선택하세요.]")
            st.markdown(":blue-badge[주변 주차장 검색] :blue-badge[침수 위험 비교] :blue-badge[데이터로 확인]")
        with hero_art:
            st.image(LOGO, width="stretch")

    has_location = "current_location" in st.session_state
    view_request = st.session_state.pop("parking_view_request", None)
    if view_request == "nearby":
        st.session_state.update(parking_scope="내 주변", parking_query="", selected_id=None)
    elif view_request == "all":
        st.session_state.update(parking_scope="전체 지역", parking_query="", parking_district="전체 지역", selected_id=None)
    query = st.text_input("주차장 이름 또는 주소", placeholder="지역이나 주차장을 검색하세요 · 거리 제한 없이 찾아드려요", key="parking_query")
    searching = bool(query.strip())
    scope = st.session_state.setdefault("parking_scope", "내 주변")
    radius = st.session_state.setdefault("parking_radius", 300)
    radius_label = f"{radius}m" if radius < 1000 else f"{radius / 1000:g}km"
    district_view = scope == "전체 지역" and not searching
    if district_view:
        st.session_state.setdefault("parking_district", sorted(frame["district"].unique())[0])
        districts = ["전체 지역"] + list(SERVICE_DISTRICTS)
        district = st.selectbox("구별 주차장 보기", districts, key="parking_district")
    if searching:
        st.caption("검색 중 · 거리 제한 없이 표시합니다. 검색어를 지우면 이전 목록 범위로 돌아갑니다.")
    elif district_view:
        st.caption("전체보기 · 위험점수가 산정된 주차장만 표시합니다." if district == "전체 지역" else f"{district}에서 위험점수가 산정된 주차장만 표시합니다.")
    elif not has_location:
        st.caption("전체 지역 표시 중 · 지도 위 ‘◎ 현재 위치’를 누르면 내 주변을 볼 수 있습니다.")
    elif scope == "내 주변":
        st.caption(f"내 위치에서 {radius_label} 이내의 주차장만 지도와 목록에 표시합니다. 모든 주차장은 ‘전체보기’를 누르세요.")
    else:
        st.caption("전체 지역 · 거리 제한 없이 모든 주차장을 표시합니다.")
    matches = frame
    if query.strip():
        needle = query.strip()
        matches = matches[matches["name"].str.contains(needle, regex=False) | matches["address"].str.contains(needle, regex=False)]
    if not searching and scope == "내 주변" and has_location:
        matches = matches[matches["distance"] <= radius]
    elif district_view and district != "전체 지역":
        matches = matches[matches["district"] == district]
    if district_view:
        matches = matches[matches["score"].notna()]
    matches = matches.sort_values("distance")
    map_matches = matches.copy()
    st.caption(f"전체 등록 주차장 {len(frame):,}개 · 현재 표시 {len(matches):,}개")
    if matches.empty and not searching and not district_view and has_location:
        nearest_distance = frame["distance"].min()
        st.info(f"현재 위치의 {radius_label} 반경 안에는 등록된 주차장이 없습니다. 가장 가까운 등록 주차장은 약 {nearest_distance / 1000:.1f}km 떨어져 있습니다. 현재 서비스 지역은 {SERVICE_AREA}입니다.")
    mode = st.radio("검색 화면", ["주변 주차장 검색", "주차장 상세 비교"], horizontal=True, label_visibility="collapsed")
    if mode == "주변 주차장 검색":
        # Clear a selected parking when it falls outside the current search.
        if st.session_state["selected_id"] not in map_matches["id"].tolist():
            st.session_state["selected_id"] = None
        selected_id = st.session_state["selected_id"]
        columns = st.columns([1.1, 2, 1.15] if selected_id is not None else [1, 2.5], gap="large")
        with columns[0]:
            result_label = "검색 결과" if searching else f"{district} 주차장" if district_view else "주변 주차장" if has_location else "전체 주차장"
            st.markdown(f"#### {result_label} {len(matches)}개")
            st.caption("가까운 거리순")
            if matches.empty:
                st.info("일치하는 주차장이 없습니다. 다른 이름이나 주소로 검색해 보세요." if searching else "선택한 지역에는 위험점수가 산정된 주차장이 없습니다. 다른 구를 선택해 보세요." if district_view else "반경 안에 주차장이 없습니다. 반경을 넓히거나 ‘전체보기’를 누르세요.")
            for _, row in matches.head(3).iterrows():
                identifier = int(row["id"])
                with st.container(border=True):
                    st.markdown(f'**{row["name"]}**')
                    st.caption(row["address"])
                    st.write(f'{row["distance"]:,.0f}m · 위험지수 미산정' if pd.isna(row["score"]) else f'{row["distance"]:,.0f}m · 추정 위험지수 **{row["score"]:.1f}** / 100')
                    badge(row["score"])
                    if st.button("상세 보기", key=f"detail_{identifier}", width="stretch"):
                        st.session_state["selected_id"] = identifier
                        st.rerun()
                    included = identifier in st.session_state["compare_ids"]
                    st.button("비교에서 제외" if included else "비교에 담기", key=f"add_{identifier}", disabled=not included and len(st.session_state["compare_ids"]) >= 3, on_click=toggle_compare, args=(identifier,))
            st.caption(f'비교함 {len(st.session_state["compare_ids"])} / 3개')
        with columns[1]:
            st.caption("자동차·물방울 핀으로 주차장을 표시합니다." + (" 연한 회색 핀은 위험점수 미산정입니다." if unscored_count else ""))
            map_data = map_matches[["id", "name", "address", "lat", "lon", "score", "level"]].copy()
            map_data["icon"] = [marker_icon(score, int(identifier) == selected_id)
                                for identifier, score in zip(map_data["id"], map_data["score"])]
            show_all = scope == "전체 지역" and st.session_state.get("parking_district") == "전체 지역" and not searching
            render_map(map_data, lat, lon, radius if has_location and scope == "내 주변" and not searching else 0,
                       selected_id, show_all=show_all, has_location=has_location,
                       fit_rows=searching or district_view)
            legend(map_data, per_row=3 if selected_id is not None else 6)
            st.caption("색상은 전체 산정 주차장의 최저 점수(하늘색)부터 최고 점수(남색)까지 이어집니다." + (" 연한 회색은 미산정입니다." if unscored_count else ""))
            st.caption(NOTE)
            st.caption("핀을 누르면 상세 패널이 열립니다. 핀에 마우스를 올리면 이름과 점수가 보입니다. 검색 반경과 거리는 기준 위치를 중심으로 계산됩니다.")
        if selected_id is not None:
            with columns[2]:
                if st.button("상세 닫기", key="close_detail"):
                    st.session_state["selected_id"] = None
                    st.rerun()
                detail(frame.loc[frame["id"] == selected_id].iloc[0])
    else:
        st.subheader("주차장, 나란히 살펴보세요.")
        st.caption("검색 조건이 달라져도 비교함은 유지됩니다. 아래에서 항목을 추가하거나 제외하세요.")
        names = dict(zip(frame["id"], frame["name"]))
        st.session_state["compare_picker"] = list(st.session_state["compare_ids"])
        ids = st.multiselect("비교할 주차장 (최대 3개)", frame["id"].tolist(), format_func=lambda i: names[i], max_selections=3, key="compare_picker", on_change=sync_compare)
        order = st.selectbox("정렬 기준", ["거리순", "위험도 낮은 순", "위험도 높은 순"])
        compared = frame[frame["id"].isin(ids)].sort_values("distance" if order == "거리순" else "score", ascending=order != "위험도 높은 순")
        if len(compared) < 2:
            st.info("주차장을 2~3개 선택하면 나란히 비교할 수 있습니다.")
        if not compared.empty:
            for col, (_, row) in zip(st.columns(len(compared)), compared.iterrows()):
                with col:
                    with st.container(border=True):
                        detail(row)
    st.divider()
    info_col, content = st.columns([1, 2])
    with info_col:
        st.markdown("### 숫자의 근거도, 투명하게.")
        st.caption("위험을 이해하는 첫걸음은 데이터를 아는 것입니다.")
    with content:
        source_tab, formula_tab = st.tabs(["데이터 출처", "계산 방법"])
        with source_tab:
            st.write("분석 항목: **강수량 · 지형·고도 · 과거 침수 이력**")
            st.caption("사용자 제공 주차장 목록·자치구별 강수량·주차장별 저지대 점수·침수심 파일을 사용합니다. 빠진 원본값은 0으로 대체하지 않습니다.")
        with formula_tab:
            st.code("[(침수심 × 0.6 + 거리 × 0.4) × 0.45 + 강수위험도 × 0.3 + 저지대 × 0.25] × 100", language=None)
            st.caption(f'네 입력은 0~1 척도로 맞춥니다. 침수심은 원본 최대값({FRAME["depth_reference_max"].iloc[0]:g})으로, 강수위험도는 제공된 강수자료의 최대값({FRAME["rain_reference_max"].iloc[0]:g})으로, 저지대 점수는 100으로 나눕니다. 거리 점수는 1 − (최소거리 ÷ 전체 등록 주차장의 최대 최소거리)입니다. 검색 조건에 따라 정규화 기준이 바뀌지 않습니다.')
            st.caption("침수 파일에는 구역 경계 도형이 없어 대표좌표까지의 직선거리와 해당 좌표의 침수심을 사용한 추정 점수입니다. 미관측 지역의 침수 여부를 확정하는 값은 아닙니다.")
            st.write("강수위험도 = 연최대1시간강수량 × 0.4 + 3시간최대강수량 × 0.4 + 집중호우발생빈도(일) × 0.2")
            st.caption("3시간 강수량은 같은 날짜 안에서 1·2·3시, 2·3·4시처럼 연속 합산한 뒤 연간 최대값을 사용합니다. 날짜를 넘는 구간은 제외합니다. 60mm를 초과한 날은 여러 번 발생해도 하루 한 번만 셉니다. 현재 파일은 집계값이며 시간별 원자료가 없어 해당 집계 과정을 재검증하지는 못했습니다.")

elif page == "분석 데이터 결과":
    st.title("데이터로 살펴보는 침수 위험")
    st.info(NOTE)
    st.caption(f"전체 통계는 검색 반경과 무관하게 서비스 지역({SERVICE_AREA}) 주차장 {len(frame):,}개를 기준으로 집계합니다."
               + (" 위험점수가 없는 주차장은 미산정으로 집계합니다." if unscored_count else ""))
    counts = frame["level"].value_counts().reindex(list(COLORS), fill_value=0)
    if not unscored_count:
        counts = counts.drop("미산정")
    metrics = [("분석 대상 주차장", len(frame))] + [(f"상대 위험도 {name}", counts[name]) for name in reversed(counts.index)]
    for offset in range(0, len(metrics), 3):
        for col, (label, count) in zip(st.columns(3), metrics[offset:offset + 3]):
            col.metric(label, f"{count}개")
    left, right = st.columns(2)
    color = alt.Color("등급:N", scale=alt.Scale(domain=list(counts.index), range=[COLORS[name] for name in counts.index]), sort=list(counts.index))
    with left:
        st.subheader("위험 등급별 분포")
        chart_data = pd.DataFrame({"등급": counts.index, "주차장 수": counts.values})
        st.altair_chart(alt.Chart(chart_data).mark_arc(innerRadius=70).encode(theta="주차장 수:Q", color=color, tooltip=["등급:N", "주차장 수:Q"]), width="stretch")
    with right:
        st.subheader("위험지수 구간별 분포")
        bins = frame["score"].dropna().map(lambda value: risk_band(value)[4])  # 등급 배지와 같은 기준(위험지수의 정수 부분)
        distribution = bins.value_counts().reindex([band[4] for band in RISK_BANDS], fill_value=0)
        chart_data = pd.DataFrame({"점수 구간": distribution.index.astype(str), "주차장 수": distribution.values})
        st.altair_chart(alt.Chart(chart_data).mark_bar(color="#1685ff", cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(x=alt.X("점수 구간:N", sort=None), y=alt.Y("주차장 수:Q", axis=alt.Axis(tickMinStep=1)), tooltip=["점수 구간:N", "주차장 수:Q"]), width="stretch")
    for col, ascending in zip(st.columns(2), [False, True]):
        with col:
            st.subheader("위험지수 하위 주차장" if ascending else "위험지수 상위 주차장")
            ranking = frame.dropna(subset=["score"]).sort_values("score", ascending=ascending).head(3)
            if ranking.empty:
                st.info("위험점수가 연결되면 순위를 표시합니다.")
            st.dataframe(ranking[["name", "address", "score", "level"]].rename(columns={"name": "주차장", "address": "주소", "score": "위험지수", "level": "상대 등급"}), hide_index=True, width="stretch")
    st.caption("예시 5등급: 매우 낮음 0–19 / 낮음 20–39 / 보통 40–59 / 높음 60–79 / 매우 높음 80–100. 실제 분석 기준 확정 시 변경될 수 있습니다.")
else:
    st.title("궁금한 점을 확인하세요.")
    category = st.radio("질문 카테고리", ["전체 질문", "위험지수", "서비스 이용", "데이터"], horizontal=True)
    questions = [q for q in FAQ if category == "전체 질문" or q[0] == category]
    st.subheader(f"자주 묻는 질문 {len(questions)}")
    for index, (_, question, answer) in enumerate(questions):
        with st.expander(f"Q. {question}", expanded=index == 0):
            st.write(answer)

# ---------------- 푸터 ----------------
st.divider()
foot_left, foot_right = st.columns(2)
foot_left.markdown("**침착**  \n:gray[침수 위험을 살피는 주차 습관]")
foot_right.caption("제공된 서울시 주차장 데이터 기반  \n대표좌표 기반 추정 위험도 · 실시간 침수 예측이 아닙니다.")
