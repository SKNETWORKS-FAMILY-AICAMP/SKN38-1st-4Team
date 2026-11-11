"""주차장 지도, 주변 검색, 상세 조회와 비교 화면."""
from math import atan2, cos, radians, sin, sqrt

import pandas as pd
import streamlit as st

from services.parking_data import service_inventory
from services.parking_map import PREVIEW_LOCATION, render_map
from services.parking_marker import RISK_BANDS, marker_icon, marker_svg, risk_band
from services.risk_model import NOTE
from services.service_config import SERVICE_AREA, SERVICE_DISTRICTS
from services.ui import LOGO


def distance(lat, lon, target_lat, target_lon):
    """Straight-line distance in meters, not walking/driving distance."""
    a1, a2 = radians(lat), radians(target_lat)
    dlat, dlon = a2 - a1, radians(target_lon - lon)
    a = sin(dlat / 2) ** 2 + cos(a1) * cos(a2) * sin(dlon / 2) ** 2
    return 6371000 * 2 * atan2(sqrt(a), sqrt(max(0, 1 - a)))


def badge(value):
    text = risk_band(value)[1]
    st.badge(text, color="gray" if text == "미산정" else "blue")


# Kakao navigation is temporarily disabled; implementation is in services/kakao_navi_view.py.

def detail(row):
    st.subheader(row["name"])
    st.caption(row["address"])
    st.caption(f'주차장관리번호: {row["parking_code"]}')
    st.metric("상대적 침수 위험지수", "미산정" if pd.isna(row["score"]) else f'{row["score"]} / 100'
    badge(row["score"])
    st.caption(NOTE)
    st.caption(f'기준점에서 {row["distance"]:,.0f}m · 직선거리')
    st.markdown("#### 참고 지표")
    for label, key in [("침수심 점수", "depth"), ("침수 대표좌표 거리 점수", "distance_risk"), ("강수위험도", "rain"), ("저지대 상대점수", "terrain")]:
        if pd.isna(row[key]):
            st.write(f"{label} · **미산정**")
        else:
            st.write(f'{label} · **{row[key]:.0f} / 100**')
            st.progress(float(row[key]) / 100)
    if pd.notna(row["rain_raw"]):
        st.caption(f'강수 원값 {row["rain_raw"]:.1f} · {int(row["rain_year"])}년 · 1시간 최대 {row["rain_max_1h_mm"]:g}mm · 3시간 최대 {row["rain_max_3h_mm"]:g}mm · 집중호우 {int(row["heavy_rain_days"])}일')
    if pd.notna(row.get("flood_distance_m", float("nan"))):
        st.caption(f'가장 가까운 침수 대표좌표까지 {row["flood_distance_m"]:,.0f}m · 구역 경계까지의 거리가 아닙니다.')
        st.caption(f'정규화 기준: 침수심 {row["depth_reference_max"]:g} · 최대 최소거리 {row["distance_reference_max_m"]:,.0f}m · 강수위험도 {row["rain_reference_max"]:g}')
    if pd.isna(row["score"]):
        st.info(row["risk_missing_reason"])
    st.info("점수가 낮더라도 안전을 보장하지 않습니다. 현장 상황과 기상특보를 확인하세요.")


def toggle_compare(identifier):
    current = st.session_state["compare_ids"]
    if identifier in current:
        st.session_state["compare_ids"] = [i for i in current if i != identifier]
    elif len(current) < 3:
        st.session_state["compare_ids"] = current + [identifier]


def sync_compare():
    st.session_state["compare_ids"] = list(st.session_state["compare_picker"])


def legend(map_data, color_min, color_max, per_row=6):
    """기존 water-legend: 점수 구간별 자동차·물방울 핀 + 미산정 핀."""
    items = []
    if map_data["score"].notna().any():
        items += [(marker_svg(float(score), False, color_min, color_max), label, interval)
                  for score, label, _, _, interval in RISK_BANDS]
    if map_data["score"].isna().any():
        items.append((marker_svg(None, False, color_min, color_max), "미산정", "입력 데이터 확인 중"))
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

frame = service_inventory()
lat, lon = st.session_state.get("current_location", PREVIEW_LOCATION)
frame["distance"] = frame.apply(lambda row: distance(lat, lon, row["lat"], row["lon"]), axis=1)
frame["level"] = frame["score"].map(lambda score: risk_band(score)[1])
unscored_count = int(frame["score"].isna().sum())
scored_values = frame["score"].dropna()
color_min = float(scored_values.min()) if not scored_values.empty else 0
color_max = float(scored_values.max()) if not scored_values.empty else 100

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
    st.caption("전체보기 · 서비스 지역의 주차장을 표시합니다." if district == "전체 지역" else f"{district} 주차장을 표시합니다.")
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
            st.info("일치하는 주차장이 없습니다. 다른 이름이나 주소로 검색해 보세요." if searching else "선택한 지역에는 등록된 주차장이 없습니다." if district_view else "반경 안에 주차장이 없습니다. 반경을 넓히거나 ‘전체보기’를 누르세요.")
        for _, row in matches.head(3).iterrows():
            identifier = int(row["id"])
            with st.container(border=True):
                st.markdown(f'**{row["name"]}**')
                st.caption(row["address"])
                st.write(f'{row["distance"]:,.0f}m · 위험지수 미산정' if pd.isna(row["score"]) else f'{row["distance"]:,.0f}m · 위험지수 **{row["score"]}** / 100')
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
        map_data["icon"] = [marker_icon(score, int(identifier) == selected_id, color_min, color_max)
                            for identifier, score in zip(map_data["id"], map_data["score"])]
        show_all = scope == "전체 지역" and st.session_state.get("parking_district") == "전체 지역" and not searching
        render_map(map_data, lat, lon, radius if has_location and scope == "내 주변" and not searching else 0,
                   selected_id, show_all=show_all, has_location=has_location,
                   fit_rows=searching or district_view)
        legend(map_data, color_min, color_max, per_row=3 if selected_id is not None else 6)
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
    source_tab, reference_tab = st.tabs(["데이터 출처", "참고 지표"])
    with source_tab:
        st.write("최종 위험지수는 제공된 점수 CSV의 `total_risk_score`를 주차장 관리번호로 연결합니다.")
        st.caption("점수 파일에 값이 없는 주차장은 미산정으로 표시합니다.")
    with reference_tab:
        st.caption("상세 화면의 침수심·거리·강수·저지대 점수는 참고 지표입니다.")
        st.caption("침수 파일에는 구역 경계 도형이 없어 대표좌표까지의 직선거리와 해당 좌표의 침수심을 사용한 추정 점수입니다. 미관측 지역의 침수 여부를 확정하는 값은 아닙니다.")
        st.write("강수위험도 = 연최대1시간강수량 × 0.4 + 3시간최대강수량 × 0.4 + 집중호우발생빈도(일) × 0.2")
        st.caption("3시간 강수량은 같은 날짜 안에서 1·2·3시, 2·3·4시처럼 연속 합산한 뒤 연간 최대값을 사용합니다. 날짜를 넘는 구간은 제외합니다. 60mm를 초과한 날은 여러 번 발생해도 하루 한 번만 셉니다. 현재 파일은 집계값이며 시간별 원자료가 없어 해당 집계 과정을 재검증하지는 못했습니다.")
