"""주차장 지도 (Python + Streamlit 전용).

기존 카카오 지도 컴포넌트(HTML/JS)를 대체합니다. 지도는 Streamlit에 포함된
st.pydeck_chart로 그리며, 자동차·물방울 마커는 parking_marker.py가 만든 SVG를 그대로 씁니다.
카카오 지도 위 버튼(반경 슬라이더·전체보기·현재 위치)은 지도 위 Streamlit 위젯으로 옮겼습니다.
현재 위치는 streamlit-js-eval 라이브러리의 get_geolocation()으로 브라우저(기기 GPS·Wi-Fi) 위치를 받습니다.
"""
from math import isfinite

import pydeck as pdk
import streamlit as st
from streamlit_js_eval import get_geolocation

from map_payload import json_records

# 브라우저 위치 오류 코드(GeolocationPositionError.code)별 안내
GPS_ERRORS = {
    0: "이 브라우저는 위치 기능을 지원하지 않습니다. 아래에서 기준 위치를 직접 고르세요.",
    1: "위치 권한이 거부되었습니다. 주소창의 사이트 설정에서 위치를 ‘허용’으로 바꾼 뒤 다시 누르세요.",
    2: "기기 위치를 찾지 못했습니다. 기기의 위치 서비스(GPS·Wi-Fi)가 켜져 있는지 확인하세요.",
    3: "위치 확인 시간이 초과되었습니다. 잠시 후 다시 누르세요.",
}
GPS_INSECURE_ORIGIN = ("브라우저는 https 주소나 이 컴퓨터의 http://localhost 주소에서만 위치를 알려 줍니다. "
                       "http://192.168… 같은 네트워크 주소로 접속했다면 기준 위치를 직접 고르세요.")

# GPS를 쓸 수 없을 때 고르는 기준 위치 목록
LOCATION_PRESETS = {
    "색동공원 (강북구)": (37.6333382, 127.0206239),
    "강서구청": (37.5509, 126.8495),
    "도봉구청": (37.6688, 127.0471),
    "서대문구청": (37.5791, 126.9368),
    "은평구청": (37.6027, 126.9291),
}


def _show_all_changed():
    st.session_state["parking_view_request"] = "all" if st.session_state["map_show_all"] else "nearby"


def _radius_changed():
    st.session_state["parking_view_request"] = "nearby"


def _preset_changed():
    lat, lon = LOCATION_PRESETS[st.session_state["location_preset"]]
    st.session_state["location_lat"], st.session_state["location_lon"] = lat, lon


def _valid_coordinate(lat, lon):
    return isfinite(lat) and isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180


def _apply_location():
    lat, lon = float(st.session_state["location_lat"]), float(st.session_state["location_lon"])
    if _valid_coordinate(lat, lon):
        # 직접 고른 위치가 늦게 도착한 GPS 응답에 덮이지 않도록 GPS 요청을 끝냅니다.
        st.session_state.update(current_location=(lat, lon), parking_view_request="nearby",
                                gps_pending=False, gps_status=None)


def read_gps_result(value):
    """get_geolocation() 응답을 ((위도, 경도, 오차m 또는 None), None) 또는 (None, 안내 문구)로 바꿉니다.

    브라우저가 아직 답하지 않았으면 (None, None)입니다.
    """
    if not isinstance(value, dict):
        return None, None
    error = value.get("error")
    if error is not None:
        error = error if isinstance(error, dict) else {}
        if "secure origin" in str(error.get("message", "")).lower():
            return None, GPS_INSECURE_ORIGIN
        return None, GPS_ERRORS.get(error.get("code"), "현재 위치를 가져오지 못했습니다. 다시 누르세요.")
    coords = value.get("coords")
    try:
        lat, lon = float(coords["latitude"]), float(coords["longitude"])
    except (KeyError, TypeError, ValueError):
        return None, "브라우저 위치 응답을 읽지 못했습니다. 다시 누르세요."
    if not _valid_coordinate(lat, lon):
        return None, "브라우저가 올바르지 않은 좌표를 보냈습니다. 다시 누르세요."
    try:
        accuracy = float(coords.get("accuracy"))
    except (TypeError, ValueError):
        accuracy = None
    return (lat, lon, accuracy if accuracy is not None and isfinite(accuracy) else None), None


def _request_gps():
    # 요청마다 새 컴포넌트 키를 써야 브라우저가 위치를 다시 읽습니다.
    st.session_state["gps_request"] = st.session_state.get("gps_request", 0) + 1
    st.session_state.update(gps_pending=True, gps_status=None)


def _gps_location():
    """GPS 요청 중이면 브라우저 위치를 받아 기준 위치로 씁니다.

    팝오버의 위도·경도 입력칸보다 먼저 불러야 그 칸을 GPS 좌표로 채울 수 있습니다.
    """
    if not st.session_state.get("gps_pending"):
        return
    value = get_geolocation(component_key=f'gps_request_{st.session_state["gps_request"]}')
    position, error = read_gps_result(value)
    if position is None and error is None:
        st.caption("현재 위치 확인 중 · 브라우저가 위치 권한을 물으면 ‘허용’을 누르세요.")
        return
    st.session_state["gps_pending"] = False
    if error:
        st.session_state["gps_status"] = ("warning", error)
        return
    lat, lon, accuracy = position
    status = "GPS 현재 위치 기준" + ("" if accuracy is None else f" · 오차 약 ±{accuracy:,.0f}m")
    st.session_state.update(location_lat=lat, location_lon=lon, current_location=(lat, lon),
                            parking_view_request="nearby", gps_status=("caption", status))
    # 이번 실행의 거리·목록은 이전 위치로 계산됐으므로 새 위치로 다시 그립니다.
    st.rerun()


def _map_selected():
    event = st.session_state.get("parking_map")
    objects = (event.selection.objects or {}).get("parking", []) if event else []
    if objects:
        st.session_state["selected_id"] = int(objects[0]["id"])


def map_controls(show_all, lat, lon):
    """카카오 지도 안의 반경 슬라이더·전체보기·현재 위치 버튼에 해당합니다."""
    _gps_location()
    st.slider("내 위치 반경", min_value=200, max_value=2000, step=100, format="%dm",
              key="parking_radius", on_change=_radius_changed, help="200m–2km · 내 주변에 적용")
    all_col, locate_col = st.columns(2, vertical_alignment="center")
    with all_col:
        st.session_state["map_show_all"] = show_all
        st.toggle("전체보기", key="map_show_all", on_change=_show_all_changed)
    with locate_col:
        with st.popover("◎ 현재 위치", width="stretch"):
            st.session_state.setdefault("location_preset", next(iter(LOCATION_PRESETS)))
            st.session_state.setdefault("location_lat", lat)
            st.session_state.setdefault("location_lon", lon)
            st.button("GPS로 내 위치 찾기", key="gps_button", on_click=_request_gps, type="primary", width="stretch")
            st.caption("브라우저 위치 권한이 필요합니다. 기기에 따라 GPS·Wi-Fi로 위치를 잡습니다.")
            st.divider()
            st.caption("또는 기준 위치를 직접 고르세요.")
            st.selectbox("기준 위치", list(LOCATION_PRESETS), key="location_preset", on_change=_preset_changed)
            st.number_input("위도", key="location_lat", format="%.6f", step=0.0005)
            st.number_input("경도", key="location_lon", format="%.6f", step=0.0005)
            st.button("이 위치로 검색", on_click=_apply_location, width="stretch")
    kind, text = st.session_state.get("gps_status") or (None, None)
    if kind == "warning":
        st.warning(text)
    elif kind == "caption":
        st.caption(text)


def render_map(rows, lat, lon, radius, selected_id, show_all, has_location, fit_rows):
    """rows: id·name·address·lat·lon·score·level·icon 컬럼. fit_rows=True면 결과 전체가 보이게 맞춥니다."""
    map_controls(show_all, lat, lon)
    records = json_records(rows[["id", "name", "address", "lat", "lon", "score", "level", "icon"]])
    for row in records:
        row["label"] = "—" if row["score"] is None else f'{row["score"]:.1f}'
        row["tip"] = "위험지수 미산정" if row["score"] is None else f'추정 위험지수 {row["score"]:.1f} / 100 · {row["level"]}'

    if fit_rows and records:
        view = pdk.data_utils.compute_view([[r["lon"], r["lat"]] for r in records], view_proportion=1)
        view.zoom = min(max(view.zoom - 0.3, 10), 16)
    else:
        view = pdk.ViewState(latitude=lat, longitude=lon, zoom=16 if radius <= 300 else 15 if radius <= 700 else 14 if radius <= 1400 else 13.4)
    view.pitch = 0

    origin = [{"lat": lat, "lon": lon}] if has_location else []
    pin_size = 34 if show_all else 56
    layers = [
        pdk.Layer("ScatterplotLayer", id="radius", data=origin if radius > 0 else [],
                  get_position="[lon, lat]", get_radius=radius,
                  get_fill_color=[53, 112, 212, 13], get_line_color=[53, 112, 212, 115],
                  stroked=True, line_width_min_pixels=1),
        pdk.Layer("IconLayer", id="parking", data=records, get_position="[lon, lat]",
                  get_icon="icon", get_size=pin_size, size_units='"pixels"',
                  pickable=True, auto_highlight=True),
    ]
    if not show_all:
        # 카카오 지도처럼 핀 아래에 점수 표시 (전체보기에서는 숨김)
        layers.append(pdk.Layer(
            "TextLayer", id="score", data=records, get_position="[lon, lat]", get_text="label",
            get_size=12, get_color=[23, 62, 104], get_pixel_offset=[0, 11],
            get_text_anchor='"middle"', get_alignment_baseline='"top"', font_weight=800,
            background=True, get_background_color=[234, 244, 255, 245],
            get_border_color=[185, 217, 238], get_border_width=1, background_padding=[5, 2],
        ))
    layers.append(pdk.Layer(
        "ScatterplotLayer", id="me", data=origin, get_position="[lon, lat]", get_radius=8,
        radius_units='"pixels"', get_fill_color=[8, 123, 255, 255], get_line_color=[255, 255, 255, 255],
        stroked=True, line_width_min_pixels=3,
    ))
    st.pydeck_chart(
        pdk.Deck(map_style=None, initial_view_state=view, layers=layers,
                 tooltip={"text": "{name}\n{address}\n{tip}"}),
        height=620, key="parking_map", on_select=_map_selected, selection_mode="single-object",
    )
    if not records:
        st.caption("현재 조건에 맞는 주차장이 없습니다. 반경을 넓히거나 전체보기에서 다른 구를 선택하세요.")
